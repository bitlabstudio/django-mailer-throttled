"""
Custom send mail command that only sends X mails per run.

Source: https://github.com/pinax/django-mailer/blob/master/mailer/management/commands/send_mail.py  # NOQA

This version calls a custom send_all method that uses throttled sending.

"""
from optparse import make_option
from socket import error as socket_error
import logging
import smtplib
import time

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.db import connection as db_connection

try:
    # Django 1.2
    from django.core.mail import get_connection
except ImportError:
    # ImportError: cannot import name get_connection
    from django.core.mail import SMTPConnection
    get_connection = lambda backend=None, fail_silently=False, **kwds: SMTPConnection(fail_silently=fail_silently)

from mailer.engine import prioritize
from mailer.lockfile import FileLock, AlreadyLocked, LockTimeout
from mailer.models import MessageLog


# allow a sysadmin to pause the sending of mail temporarily.
PAUSE_SEND = getattr(settings, "MAILER_PAUSE_SEND", False)

# when queue is empty, how long to wait (in seconds) before checking again
EMPTY_QUEUE_SLEEP = getattr(settings, "MAILER_EMPTY_QUEUE_SLEEP", 30)

# lock timeout value. how long to wait for the lock to become available.
# default behavior is to never wait for the lock to be available.
LOCK_WAIT_TIMEOUT = getattr(settings, "MAILER_LOCK_WAIT_TIMEOUT", -1)


def send_all_throttled():
    """
    Send all eligible messages in the queue.

    Source: https://github.com/pinax/django-mailer/blob/master/mailer/engine.py

    This customized version will send only X mails per run.

    """
    # The actual backend to use for sending, defaulting to the Django default.
    # To make testing easier this is not stored at module level.
    EMAIL_BACKEND = getattr(
        settings, 'MAILER_EMAIL_BACKEND',
        'django.core.mail.backends.smtp.EmailBackend')

    lock = FileLock('send_mail')

    logging.debug("acquiring lock...")
    try:
        lock.acquire(LOCK_WAIT_TIMEOUT)
    except AlreadyLocked:
        logging.debug("lock already in place. quitting.")
        return
    except LockTimeout:
        logging.debug("waiting for the lock timed out. quitting.")
        return
    logging.debug("acquired.")

    start_time = time.time()

    deferred = 0
    sent = 0

    try:
        connection = None
        for message in prioritize():
            try:
                if connection is None:
                    connection = get_connection(backend=EMAIL_BACKEND)
                logging.info("sending message '%s' to %s" % (message.subject.encode("utf-8"), u", ".join(message.to_addresses).encode("utf-8")))  # NOQA
                email = message.email
                email.connection = connection
                email.send()
                MessageLog.objects.log(message, 1)
                message.delete()
                sent += 1
            except (socket_error, smtplib.SMTPSenderRefused, smtplib.SMTPRecipientsRefused, smtplib.SMTPAuthenticationError) as err:  # NOQA
                message.defer()
                logging.info("message deferred due to failure: %s" % err)
                MessageLog.objects.log(message, 3, log_message=str(err))
                deferred += 1
                # Get new connection, it case the connection itself has an
                # error.
                connection = None
            if sent == getattr(settings, 'MAILER_THROTTLE_AMOUNT', 25):
                break
    finally:
        logging.debug("releasing lock...")
        lock.release()
        logging.debug("released.")

    logging.info("")
    logging.info("%s sent; %s deferred;" % (sent, deferred))
    logging.info("done in %.2f seconds" % (time.time() - start_time))


class Command(NoArgsCommand):
    help = "Do one pass through the mail queue, attempting to send all mail."
    base_options = (
        make_option(
            '-c', '--cron', default=0, type='int',
            help='If 1 don\'t print messagges, but only errors.'
        ),
    )
    option_list = NoArgsCommand.option_list + base_options

    def handle_noargs(self, **options):
        if options['cron'] == 0:
            logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        else:
            logging.basicConfig(level=logging.ERROR, format="%(message)s")
        logging.info("-" * 72)
        # if PAUSE_SEND is turned on don't do anything.
        if not PAUSE_SEND:
            send_all_throttled()
        else:
            logging.info("sending is paused, quitting.")
        db_connection.close()

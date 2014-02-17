Django Mailer Throttled
=======================

Addon for `django-mailer <https://github.com/pinax/django-mailer/>`_ allows to
send throttled emails.

Install this as an addon alongside `django-mailer`.

Installation
============

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django-mailer-throttled

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/bitmazk/django-mailer-throttled.git#egg=mailer_throttled

Add ``mailer_throttled`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'mailer'
        'mailer_throttled',
    )

Usage
=====

Set the ``MAILER_THROTTLE_AMOUNT`` to the number of emails you would like to
send per run.

Don't use the original ``send_mail`` management command any more but the new
``send_mail_throttled``.


Contribute
==========

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python2.7 django-mailer-throttled
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch

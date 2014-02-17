Django Mailer Throttled
============

Addon for django-mailer that allows to send throttled emails

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django-mailer-throttled

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/bitmazk/django-mailer-throttled.git#egg=mailer_throttled

TODO: Describe further installation steps (edit / remove the examples below):

Add ``mailer_throttled`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'mailer_throttled',
    )

Add the ``mailer_throttled`` URLs to your ``urls.py``

.. code-block:: python

    urlpatterns = patterns('',
        ...
        url(r'^//', include('mailer_throttled.urls')),
    )

Before your tags/filters are available in your templates, load them by using

.. code-block:: html

	{% load mailer_throttled_tags %}


Don't forget to migrate your database

.. code-block:: bash

    ./manage.py migrate mailer_throttled


Usage
-----

TODO: Describe usage or point to docs. Also describe available settings and
templatetags.


Contribute
----------

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

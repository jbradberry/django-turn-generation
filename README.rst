======================
django-turn-generation
======================

.. image:: https://travis-ci.com/jbradberry/django-turn-generation.svg?branch=master
    :target: https://travis-ci.com/jbradberry/django-turn-generation

A Django app for specifying the timing of and triggering turn
generation for turn-based strategy games.

Requirements
------------

- Python 2.7, 3.5+
- Django >= 1.10, < 2.3
- `djangorestframework <http://www.django-rest-framework.org/>`_ >= 3.7
- Celery >= 3.1
- python-dateutil
- pytz


Configuration
-------------

Add ``'turngeneration'`` to the ``INSTALLED_APPS`` in your settings
file, and the custom permissions plugin to ``AUTHENTICATION_BACKENDS``
::

    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        # Added.
        'rest_framework',
        'turngeneration',
    ]

    AUTHENTICATION_BACKENDS = [
        'turngeneration.backends.TurnGenerationBackend',
        'django.contrib.auth.backends.ModelBackend',
    ]


Also, be sure to include ``turngeneration.urls`` in your root urlconf.

Example::

    from django.conf.urls import include, url

    urlpatterns = [
        url(r'^', include('turngeneration.urls')),
        url(r'^admin/', include('admin.site.urls')),
        url(r'^accounts/', include('django.contrib.auth.urls'),
    ]

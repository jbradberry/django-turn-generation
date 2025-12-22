======================
django-turn-generation
======================

A Django app for specifying the timing of and triggering turn
generation for turn-based strategy games.

Requirements
------------

- Python 3.10+
- Django 5.0, 5.1, 5.2
- `djangorestframework <http://www.django-rest-framework.org/>`_ >= 3.15
- Celery >= 5.2
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

Point to wherever you have your Celery broker configured::

    CELERY_BROKER_URL = 'memory://localhost/'  # FIXME

Also, be sure to include ``turngeneration.urls`` in your root urlconf.

Example::

    from django.urls import include, path

    urlpatterns = [
        path('', include('turngeneration.urls')),
        path('admin/', include('admin.site.urls')),
        path('accounts/', include('django.contrib.auth.urls'),
    ]

===============
django-jhouston
===============

"Houston, we have a Javascript problem!"

`jhouston` catches Javascript errors occurring in the browser and
automatically posts them to the server. There they are sent to sentry and/or
saved to a database table for debugging & analysis purposes. This opens up a
whole new view on what is happening client-side.

Installation
============

settings.py::

    INSTALLED_APPS = (
        ...
        'jhouston',

urls.py::

    urlpatterns = patterns('',
        ...
        ('', include('jhouston.urls')))

base.html::

    ...
    <script src="/static/jhouston/js/jhouston.js" type="text/javascript">
    </script>

Configuration
=============

In your settings file, define the following setting::

    JHOUSTON_STORAGE_METHOD = [setting]
    
The value of this setting can either be:

* ``"sentry"`` will send all errors and logs to sentry,

* ``"database"`` will save the errors and logs into a database table viewable in
the django admin

* ``"sentry+database"`` will do both.

If you want to use the ``"database"`` or ``"sentry+database"`` setting, you must run ``python manage.py syncdb`` first.

If you want to use the `"sentry"` or `"database+sentry"` setting, you also must include a `SENTRY_DSN` setting (see sentry docs).
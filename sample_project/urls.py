from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    (r'^realm/(?P<realm_slug>[-\w]+)/',
     include('turngeneration.urls', namespace="sample_app",
             app_name="turngeneration"),
     {'realm_content_type': 'sample_app.TestRealm'}),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
)

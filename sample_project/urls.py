from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    (r'^api/', include('turngeneration.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
)

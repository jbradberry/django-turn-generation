from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^pause/$', views.PauseView.as_view(), name='pause_view'),
)

from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^pause/(?P<agent_slug>[-\w]+)/$', views.PauseView.as_view(),
        name='pause_view'),
    url(r'^unpause/(?P<agent_slug>[-\w]+)/$', views.UnPauseView.as_view(),
        name='unpause_view'),
    url(r'^ready/(?P<agent_slug>[-\w]+)/$', views.ReadyView.as_view(),
        name='ready_view'),
    url(r'^unready/(?P<agent_slug>[-\w]+)/$', views.UnReadyView.as_view(),
        name='unready_view'),
)

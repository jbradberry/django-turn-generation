from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^pause/(?P<owner_slug>[-\w]+)/$', views.PauseView.as_view(),
        name='pause_view'),
)

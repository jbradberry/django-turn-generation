from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^(?P<realm_alias>[-\w]+)/$', views.RealmListView.as_view(),
        name='realm_list'),
)

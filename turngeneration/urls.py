from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^(?P<realm_alias>[-\w]+)/$', views.RealmListView.as_view(),
        name='realm_list'),
    url(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/$',
        views.RealmRetrieveView.as_view(),
        name='realm_detail'),
)

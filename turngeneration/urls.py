from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^(?P<realm_alias>[-\w]+)/$', views.RealmListView.as_view(),
        name='realm_list'),
    url(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/$',
        views.RealmRetrieveView.as_view(),
        name='realm_detail'),
    url(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/generator/$',
        views.GeneratorView.as_view(),
        name='generator'),
    url(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/generator/rules/$',
        views.GenerationRuleListView.as_view(),
        name='generation_rules_list'),
    url(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/generator/rules/(?P<pk>\d+)/$',
        views.GenerationRuleView.as_view(),
        name='generation_rule_detail'),
)

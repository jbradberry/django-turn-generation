from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^(?P<realm_alias>[-\w]+)/$', views.RealmListView.as_view(),
        name='realm_list'),
    url(r'^(?P<realm_alias>[-\w]+)/(?P<pk>\d+)/$',
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
    url(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/(?P<agent_alias>[-\w]+)/$',
        views.AgentListView.as_view(),
        name='agent_list'),
    url(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/(?P<agent_alias>[-\w]+)/(?P<pk>\d+)/$',
        views.AgentRetrieveView.as_view(),
        name='agent_detail'),
    url(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/(?P<agent_alias>[-\w]+)/(?P<agent_pk>\d+)/pause/$',
        views.PauseView.as_view(),
        name='pause'),
    url(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/(?P<agent_alias>[-\w]+)/(?P<agent_pk>\d+)/ready/$',
        views.ReadyView.as_view(),
        name='ready'),
)

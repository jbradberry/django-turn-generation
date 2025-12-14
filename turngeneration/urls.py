from django.urls import re_path

from . import views


urlpatterns = [
    re_path(r'^(?P<realm_alias>[-\w]+)/$', views.RealmListView.as_view(), name='realm_list'),
    re_path(r'^(?P<realm_alias>[-\w]+)/(?P<pk>\d+)/$',
            views.RealmRetrieveView.as_view(),
            name='realm_detail'),
    re_path(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/generator/$',
            views.GeneratorView.as_view(),
            name='generator'),
    re_path(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/generator/rules/$',
            views.GenerationRuleListView.as_view(),
            name='generation_rules_list'),
    re_path(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/generator/rules/(?P<pk>\d+)/$',
            views.GenerationRuleView.as_view(),
            name='generation_rule_detail'),
    re_path(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/(?P<agent_alias>[-\w]+)/$',
            views.AgentListView.as_view(),
            name='agent_list'),
    re_path(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/(?P<agent_alias>[-\w]+)/(?P<pk>\d+)/$',
            views.AgentRetrieveView.as_view(),
            name='agent_detail'),
    re_path(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/(?P<agent_alias>[-\w]+)/(?P<agent_pk>\d+)/pause/$',
            views.PauseView.as_view(),
            name='pause'),
    re_path(r'^(?P<realm_alias>[-\w]+)/(?P<realm_pk>\d+)/(?P<agent_alias>[-\w]+)/(?P<agent_pk>\d+)/ready/$',
            views.ReadyView.as_view(),
            name='ready'),
]

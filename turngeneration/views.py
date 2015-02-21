from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.conf import settings

from rest_framework import generics, viewsets, mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings

import logging

from . import models, forms, plugins, serializers
from .permissions import PluginPermissions

logger = logging.getLogger(__name__)


class CrudAPIView(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RealmQuerysetMixin(object):
    serializer_class = serializers.RealmSerializer

    def get_queryset(self):
        alias = self.kwargs.get('realm_alias')
        ct = plugins.realm_type(alias)
        if ct is None:
            raise Http404
        return ct.model_class().objects.all()


class RealmListView(RealmQuerysetMixin, generics.ListAPIView):
    # /api/starsgame/
    pass


class RealmRetrieveView(RealmQuerysetMixin, generics.RetrieveAPIView):
    # /api/starsgame/3/
    pass


class GeneratorMixin(object):
    def get_generator(self, queryset):
        realm = self.get_realm()

        if getattr(self, '_generator', None) is not None:
            return self._generator

        filter_kwargs = {
            'content_type': ContentType.objects.get_for_model(realm),
            'object_id': realm.pk
        }
        self._generator = get_object_or_404(queryset, **filter_kwargs)
        return self._generator

    def get_realm(self):
        if getattr(self, '_realm', None) is not None:
            return self._realm

        alias = self.kwargs.get('realm_alias')
        ct = plugins.realm_type(alias)
        pk = self.kwargs.get('realm_pk')

        if ct is None:
            raise Http404

        try:
            self._realm = ct.get_object_for_this_type(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

        return self._realm

    def get_parent_obj(self):
        return self.get_realm()


class GeneratorView(GeneratorMixin, CrudAPIView):
    # /api/starsgame/3/generator/
    serializer_class = serializers.GeneratorSerializer
    queryset = models.Generator.objects.all()
    permission_classes = (PluginPermissions,)

    def create(self, request, *args, **kwargs):
        realm = self.get_realm()
        instance = models.Generator(content_object=realm)

        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        generator = self.get_generator(queryset)

        # May raise a permission denied
        self.check_object_permissions(self.request, generator)

        return generator


class GenerationRuleListView(GeneratorMixin, generics.ListCreateAPIView):
    # /api/starsgame/3/generator/rules/
    serializer_class = serializers.GenerationRuleSerializer
    queryset = models.GenerationRule.objects.all()
    permission_classes = (PluginPermissions,)

    def create(self, request, *args, **kwargs):
        generator = self.get_generator(models.Generator.objects.all())
        instance = models.GenerationRule(generator=generator)

        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        generator = self.get_generator(models.Generator.objects.all())
        return generator.rules.all()

    def get_parent_obj(self):
        realm = self.get_realm()
        # Make sure that the Generator actually exists before checking
        # permissions.
        self.get_generator(models.Generator.objects.all())
        return realm


class GenerationRuleView(GeneratorMixin, generics.RetrieveUpdateDestroyAPIView):
    # /api/starsgame/3/generator/rules/7/
    serializer_class = serializers.GenerationRuleSerializer
    queryset = models.GenerationRule.objects.all()
    permission_classes = (PluginPermissions,)

    def get_queryset(self):
        generator = self.get_generator(models.Generator.objects.all())
        return generator.rules.all()


class AgentQuerysetMixin(object):
    def get_queryset(self):
        generator = self.get_generator(models.Generator.objects.all())
        agent_type = plugins.agent_type(self.kwargs.get('agent_alias'))

        # TODO: this is clunky, create a better api
        plugin = plugins.get_plugin_for_model(agent_type.model_class())
        if agent_type is None or plugin is None:
            raise Http404

        queryset = plugin.related_agents(generator.content_object, agent_type)
        if queryset is None:
            raise Http404
        return queryset


class AgentListView(AgentQuerysetMixin, GeneratorMixin, generics.ListAPIView):
    # /api/starsgame/3/starsrace/
    serializer_class = serializers.AgentSerializer


class AgentRetrieveView(AgentQuerysetMixin, GeneratorMixin,
                        generics.RetrieveAPIView):
    # /api/starsgame/3/starsrace/5/
    serializer_class = serializers.AgentSerializer


class AgentMixin(object):
    def get_agent(self):
        realm = self.get_realm()
        generator = self.get_generator(models.Generator.objects.all())

        if getattr(self, '_agent', None) is not None:
            return self._agent

        alias = self.kwargs.get('agent_alias')
        ct = plugins.agent_type(alias)
        pk = self.kwargs.get('agent_pk')

        if ct is None:
            raise Http404

        plugin = plugins.get_plugin_for_model(ct.model_class())
        qs = plugin.related_agents(realm, ct)
        if qs is None:
            raise Http404

        self._agent = get_object_or_404(qs, pk=pk)
        return self._agent

    def get_parent_obj(self):
        return self.get_agent()


class PauseView(AgentMixin, GeneratorMixin, CrudAPIView):
    # /api/starsgame/3/starsrace/5/pause/
    serializer_class = serializers.PauseSerializer
    queryset = models.Pause.objects.all()
    permission_classes = (PluginPermissions,)

    def create(self, request, *args, **kwargs):
        generator = self.get_generator(models.Generator.objects.all())
        agent = self.get_agent()
        if not generator.allow_pauses:
            raise PermissionDenied

        instance = models.Pause(generator=generator, agent=agent)

        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        generator = self.get_generator(models.Generator.objects.all())
        agent = self.get_agent()

        filter_kwargs = {
            'content_type': ContentType.objects.get_for_model(agent),
            'object_id': agent.pk, 'generator': generator
        }
        pause = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, pause)

        return pause


class ReadyView(AgentMixin, GeneratorMixin, CrudAPIView):
    # /api/starsgame/3/starsrace/5/ready/
    serializer_class = serializers.ReadySerializer
    queryset = models.Ready.objects.all()
    permission_classes = (PluginPermissions,)

    def create(self, request, *args, **kwargs):
        generator = self.get_generator(models.Generator.objects.all())
        agent = self.get_agent()

        instance = models.Ready(generator=generator, agent=agent)

        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        generator = self.get_generator(models.Generator.objects.all())
        agent = self.get_agent()

        filter_kwargs = {
            'content_type': ContentType.objects.get_for_model(agent),
            'object_id': agent.pk, 'generator': generator
        }
        ready = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, ready)

        return ready

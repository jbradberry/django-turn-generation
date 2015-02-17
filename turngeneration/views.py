from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.conf import settings

from rest_framework import generics, viewsets, mixins

import logging

from . import models, forms, plugins, serializers

logger = logging.getLogger(__name__)


# new url scheme:

# /api/starsgame/
# /api/starsgame/3/
# /api/starsgame/3/generator/
# /api/starsgame/3/generator/rules/
# /api/starsgame/3/generator/rules/7/
# /api/starsgame/3/starsrace/
# /api/starsgame/3/starsrace/5/
# /api/starsgame/3/starsrace/5/pause/
# /api/starsgame/3/starsrace/5/ready/


class RealmMixin(object):
    serializer_class = serializers.RealmSerializer
    lookup_url_kwarg = 'realm_pk'
    type_url_kwarg = 'realm_alias'

    def get_type_kwarg(self):
        return self.type_url_kwarg

    def get_queryset(self):
        alias = self.kwargs.get(self.get_type_kwarg())
        content_type = plugins.realm_type(alias)
        if content_type is None:
            raise Http404
        return content_type.model_class().objects.all()


class RealmListView(RealmMixin, generics.ListAPIView):
    # /api/starsgame/
    pass


class RealmRetrieveView(RealmMixin, generics.RetrieveAPIView):
    # /api/starsgame/3/
    pass


class GeneratorMixin(object):
    def get_generator(self, queryset):
        alias = self.kwargs.get('realm_alias')
        ct = plugins.realm_type(alias)
        pk = self.kwargs.get('realm_pk')

        filter_kwargs = {'content_type': ct, 'object_id': pk}
        return get_object_or_404(queryset, **filter_kwargs)


class GeneratorView(GeneratorMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    # /api/starsgame/3/generator/
    serializer_class = serializers.GeneratorSerializer
    queryset = models.Generator.objects.all()

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

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        generator = self.get_generator(queryset)

        # May raise a permission denied
        self.check_object_permissions(self.request, generator)

        return generator


class GenerationRuleListView(GeneratorMixin, generics.ListCreateAPIView):
    # /api/starsgame/3/generator/rules/
    serializer_class = serializers.GenerationRuleSerializer

    def perform_create(self, serializer):
        generator = self.get_generator(models.Generator.objects.all())
        serializer.save(generator_id=generator.id)

    def get_queryset(self):
        generator = self.get_generator(models.Generator.objects.all())
        return generator.rules.all()


class GenerationRuleView(GeneratorMixin, generics.RetrieveUpdateDestroyAPIView):
    # /api/starsgame/3/generator/rules/7/
    serializer_class = serializers.GenerationRuleSerializer

    def get_queryset(self):
        generator = self.get_generator(models.Generator.objects.all())
        return generator.rules.all()


class AgentMixin(object):
    def get_queryset(self):
        generator = self.get_generator(models.Generator.objects.all())
        agent_type = plugins.agent_type(self.kwargs.get('agent_alias'))
        plugin = plugins.agent_plugin(self.kwargs.get('agent_alias'))
        if agent_type is None or plugin is None:
            raise Http404

        queryset = plugin.related_agents(generator.content_object, agent_type)
        if queryset is None:
            raise Http404
        return queryset


class AgentListView(GeneratorMixin, AgentMixin, generics.ListAPIView):
    # /api/starsgame/3/starsrace/
    serializer_class = serializers.AgentSerializer


class AgentRetrieveView(GeneratorMixin, AgentMixin, generics.RetrieveAPIView):
    # /api/starsgame/3/starsrace/5/
    serializer_class = serializers.AgentSerializer


class PauseView(GeneratorMixin,
                mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                mixins.UpdateModelMixin,
                mixins.DestroyModelMixin,
                generics.GenericAPIView):
    # /api/starsgame/3/starsrace/5/pause/
    serializer_class = serializers.PauseSerializer
    queryset = models.Pause.objects.all()

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

    def perform_create(self, serializer):
        generator = self.get_generator(models.Generator.objects.all())

        alias = self.kwargs.get('agent_alias')
        ct = plugins.agent_type(alias)
        pk = self.kwargs.get('agent_pk')

        serializer.save(content_type=ct, object_id=pk,
                        generator_id=generator.id)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        generator = self.get_generator(models.Generator.objects.all())

        alias = self.kwargs.get('agent_alias')
        ct = plugins.agent_type(alias)
        pk = self.kwargs.get('agent_pk')

        filter_kwargs = {'content_type': ct, 'object_id': pk,
                         'generator': generator}
        pause = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, pause)

        return pause

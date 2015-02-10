from rest_framework import viewsets

from . import serializers


import logging

from django.contrib.contenttypes.models import ContentType
from django.views.generic import CreateView, DeleteView
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import (PermissionDenied, ObjectDoesNotExist,
                                    ImproperlyConfigured)
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.conf import settings

from .shim14 import JsonResponse

from . import models, forms, plugins

logger = logging.getLogger(__name__)


class RealmMixin(object):
    pass


class AgentMixin(object):
    pass


class GeneratorViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.GeneratorSerializer
    queryset = models.Generator.objects.all()

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.request.method == 'POST':
            serializer_class = serializers.GeneratorCreateSerializer

        return serializer_class

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        assert 'realm_content_type' in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            "named 'realm_content_type'." % (self.__class__.__name__,)
        )

        assert 'realm_pk' in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            "named 'realm_pk'." % (self.__class__.__name__,)
        )

        realm_content_type = self.kwargs['realm_content_type']
        try:
            app_label, model = realm_content_type.split('.')
            model = model.lower()
            realm_type = ContentType.objects.get(app_label=app_label,
                                                 model=model)
        except (ObjectDoesNotExist, ValueError) as e:
            raise Http404

        if app_label not in plugins.entry_points:
            raise Http404

        filter_kwargs = {'content_type': realm_type,
                         'object_id': self.kwargs['realm_pk']}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_proxy(self):
        return


class AjaxMixin(object):
    def form_invalid(self, form):
        response = super(AjaxMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        return response

    def form_valid(self, form):
        response = super(AjaxMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {'pk': self.object.pk}
            return JsonResponse(data)
        return response


class RealmMixin(object):
    realm_slug_field = 'slug'

    slug_realm_kwarg = 'realm_slug'
    pk_realm_kwarg = 'realm_pk'

    def get_realm(self):
        realm = None

        realm_content_type = self.kwargs.get('realm_content_type')
        if realm_content_type is None:
            realm_content_type = getattr(settings, 'DEFAULT_REALM_TYPE', '')

        try:
            app_label, model = realm_content_type.split('.')
            model = model.lower()
            self.realm_type = ContentType.objects.get(app_label=app_label,
                                                      model=model)
        except (ObjectDoesNotExist, ValueError) as e:
            raise ImproperlyConfigured(
                "{0} is missing a valid realm_content_type.".format(
                    self.__class__.__name__))

        plugin = plugins.get(self.realm_type.app_label)
        if plugin is None:
            raise ImproperlyConfigured(
                "Plugin for app '{app}' does not exist.".format(
                    app=self.realm_type.app_label)
            )
        self.plugin = plugin

        realm_pk = self.kwargs.get(self.pk_realm_kwarg)
        realm_slug = self.kwargs.get(self.slug_realm_kwarg)

        if realm_pk is not None:
            opts = {'pk': realm_pk}
        elif realm_slug is not None:
            opts = {self.realm_slug_field: realm_slug}
        else:
            opts = None

        if opts:
            try:
                realm = self.realm_type.get_object_for_this_type(**opts)
            except ObjectDoesNotExist:
                raise Http404("No %s found matching this query."
                              % self.realm_type.__class__.__name__)

        return realm

    def get_generator(self):
        qs = models.Generator.objects.filter(content_type=self.realm_type,
                                             object_id=self.realm.pk)
        if not qs:
            raise Http404
        return qs.get()

    def get_agent(self):
        agent = self.plugin.get_agent(self.realm, self.kwargs)
        if agent is None:
            raise Http404
        return agent

    def get(self, request, *args, **kwargs):
        self.realm = self.get_realm()
        self.generator = self.get_generator()
        self.agent = self.get_agent()
        if not self.has_permission(self.request.user, self.agent):
            raise PermissionDenied

        return super(RealmMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.realm = self.get_realm()
        self.generator = self.get_generator()
        self.agent = self.get_agent()
        if not self.has_permission(self.request.user, self.agent):
            raise PermissionDenied

        return super(RealmMixin, self).post(request, *args, **kwargs)


class PauseView(AjaxMixin, RealmMixin, CreateView):
    model = models.Pause
    form_class = forms.PauseForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PauseView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return self.realm.get_absolute_url()

    def get_form_kwargs(self):
        kwargs = super(PauseView, self).get_form_kwargs()
        kwargs.update(instance=self.model(generator=self.generator,
                                          agent=self.agent))
        return kwargs

    def has_permission(self, user, agent):
        return self.plugin.has_pause_permission(user, agent)


class UnPauseView(AjaxMixin, RealmMixin, DeleteView):
    model = models.Pause

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UnPauseView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return self.realm.get_absolute_url()

    def get_object(self):
        agent_type = ContentType.objects.get_for_model(self.agent)
        try:
            return models.Pause.objects.filter(generator=self.generator,
                                               content_type=agent_type,
                                               object_id=self.agent.pk)
        except ObjectDoesNotExist:
            raise Http404

    def has_permission(self, user, agent):
        return self.plugin.has_unpause_permission(user, agent)


class ReadyView(AjaxMixin, RealmMixin, CreateView):
    model = models.Ready
    form_class = forms.ReadyForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReadyView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return self.realm.get_absolute_url()

    def get_form_kwargs(self):
        kwargs = super(ReadyView, self).get_form_kwargs()
        kwargs.update(instance=self.model(generator=self.generator,
                                          agent=self.agent))
        return kwargs

    def has_permission(self, user, agent):
        return self.plugin.has_ready_permission(user, agent)


class UnReadyView(AjaxMixin, RealmMixin, DeleteView):
    model = models.Ready

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UnReadyView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return self.realm.get_absolute_url()

    def get_object(self):
        agent_type = ContentType.objects.get_for_model(self.agent)
        try:
            return models.Ready.objects.filter(generator=self.generator,
                                               content_type=agent_type,
                                               object_id=self.agent.pk)
        except ObjectDoesNotExist:
            raise Http404

    def has_permission(self, user, agent):
        return self.plugin.has_unready_permission(user, agent)

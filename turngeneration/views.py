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

        plugin = plugins.all_plugins.get(self.realm_type.app_label)
        if plugin is None:
            raise ImproperlyConfigured(
                "Plugin for app '{app}' does not exist.".format(
                    app=self.realm_type.app_label)
            )
        self.plugin = plugin()

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

    def get_owner(self):
        owner = self.plugin.get_owner(self.realm, self.kwargs)
        if owner is None:
            raise Http404
        return owner

    def get(self, request, *args, **kwargs):
        self.realm = self.get_realm()
        self.generator = self.get_generator()
        self.owner = self.get_owner()
        if not self.has_permission(self.request.user, self.owner):
            raise PermissionDenied

        return super(RealmMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.realm = self.get_realm()
        self.generator = self.get_generator()
        self.owner = self.get_owner()
        if not self.has_permission(self.request.user, self.owner):
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
                                          owner=self.owner))
        return kwargs

    def has_permission(self, user, owner):
        return self.plugin.has_pause_permission(user, owner)


class UnPauseView(AjaxMixin, RealmMixin, DeleteView):
    model = models.Pause

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UnPauseView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return self.realm.get_absolute_url()

    def get_object(self):
        owner_type = ContentType.objects.get_for_model(self.owner)
        try:
            return models.Pause.objects.filter(generator=self.generator,
                                               content_type=owner_type,
                                               object_id=self.owner.pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_form_kwargs(self):
        kwargs = super(UnPauseView, self).get_form_kwargs()
        kwargs.update(instance=self.model(generator=self.generator,
                                          owner=self.owner))
        return kwargs

    def has_permission(self, user, owner):
        return self.plugin.has_unpause_permission(user, owner)

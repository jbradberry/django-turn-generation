from django.contrib.contenttypes.models import ContentType
from django.views.generic import CreateView, DeleteView
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.conf import settings

from .shim14 import JsonResponse

from . import models
from . import forms


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
        app_config = getattr(settings, 'TURNGENERATION_SETTINGS', {})
        model_config = app_config.get(
            '{0.app_label}.{0.model}'.format(self.realm_type), {})
        pause_owner = model_config.get('pause_owner')
        if pause_owner is None:
            return

        owner_model_name, kwarg_template = pause_owner
        app_label, model = owner_model_name.split('.')
        owner_type = ContentType.objects.get(app_label=app_label,
                                             model=model)
        kwargs = {}
        for key, value in kwarg_template.iteritems():
            if isinstance(value, basestring):
                if value.startswith('{') and not value.startswith('{{'):
                    value = value[1:-1]
                    if value == 'realm':
                        value = self.realm
                    elif value == 'user':
                        value = self.request.user
                    elif value.startswith('session.'):
                        value = self.request.session.get(value[8:])
                        if value is None:
                            continue
                else:
                    # unescape the escaped braces
                    kwargs[key] = value.format()

            kwargs[key] = value

        qs = owner_type.model_class().objects.filter(**kwargs)
        if qs:
            return qs[0]


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

    def get(self, request, *args, **kwargs):
        self.realm = self.get_realm()
        self.generator = self.get_generator()
        self.owner = self.get_owner()
        if self.owner is None:
            raise PermissionDenied
        return super(PauseView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.realm = self.get_realm()
        self.generator = self.get_generator()
        self.owner = self.get_owner()
        if self.owner is None:
            raise PermissionDenied
        return super(PauseView, self).post(request, *args, **kwargs)

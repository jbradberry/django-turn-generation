from rest_framework import generics, viewsets

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

from . import models, forms, plugins

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


class RealmListView(generics.ListAPIView):
    # /api/starsgame/
    serializer_class = serializers.RealmSerializer

    def get_queryset(self):
        content_type = plugins.realm_type(self.kwargs.get('realm_alias'))
        if content_type is None:
            raise Http404
        return content_type.model_class().objects.all()

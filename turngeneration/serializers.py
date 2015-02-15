from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from . import models


class ContentTypeField(serializers.Field):
    def to_representation(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return u'{ct.app_label}.{ct.model}'.format(ct=ct)

    def get_attribute(self, obj):
        return obj


class RealmSerializer(serializers.Serializer):
    content_type = ContentTypeField()
    object_id = serializers.IntegerField(source='pk')
    repr = serializers.CharField(source='__repr__')

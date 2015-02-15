from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from . import models


class ContentTypeField(serializers.Field):
    def to_representation(self, value):
        return u'{value.app_label}.{value.model}'.format(value=value)

    def to_internal_value(self, data):
        app_label, model = data.split('.')
        return ContentType.objects.get_by_natural_key(app_label, model)


class ReadOnlyDefault(object):
    def set_context(self, serializer_field):
        self.current_value = getattr(serializer_field.parent.instance,
                                     serializer_field.name, None)

    def __call__(self):
        return self.current_value

    def __repr__(self):
        return '%s()' % (self.__class__.__name__,)


class GeneratorSerializer(serializers.ModelSerializer):
    content_type = ContentTypeField(read_only=True, default=ReadOnlyDefault())
    object_id = serializers.IntegerField(read_only=True,
                                         default=ReadOnlyDefault())

    class Meta(object):
        model = models.Generator
        fields = ('content_type', 'object_id',
                  'generating', 'generation_time', 'autogenerate',
                  'allow_pauses', 'minimum_between_generations')
        read_only_fields = ('generating', 'generation_time')


class RealmSerializer(serializers.Serializer):
    content_type = serializers.SerializerMethodField()
    object_id = serializers.IntegerField(source='pk')
    repr = serializers.CharField(source='__repr__')
    generator = serializers.SerializerMethodField(required=False)

    def get_content_type(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return u'{ct.app_label}.{ct.model}'.format(ct=ct)

    def get_generator(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        try:
            generator = models.Generator.objects.get(
                content_type=ct, object_id=obj.pk)
        except models.Generator.DoesNotExist:
            return None

        return GeneratorSerializer(generator).data

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers, validators

from . import models


class ContentTypeField(serializers.Field):
    def to_representation(self, value):
        return f'{value.app_label}.{value.model}'

    def to_internal_value(self, data):
        app_label, model = data.split('.')
        return ContentType.objects.get_by_natural_key(app_label, model)


class GeneratorSerializer(serializers.ModelSerializer):
    content_type = ContentTypeField(read_only=True)

    class Meta:
        model = models.Generator
        fields = ('content_type', 'object_id', 'generating',
                  'generation_time', 'force_generate', 'autogenerate',
                  'allow_pauses', 'minimum_between_generations')
        read_only_fields = ('content_type', 'object_id', 'generating', 'generation_time')


class RealmSerializer(serializers.Serializer):
    content_type = serializers.SerializerMethodField()
    object_id = serializers.IntegerField(source='pk')
    repr = serializers.CharField(source='__repr__')
    generator = serializers.SerializerMethodField(required=False)

    def get_content_type(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return f'{ct.app_label}.{ct.model}'

    def get_generator(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        generator = models.Generator.objects.filter(content_type=ct, object_id=obj.pk).first()
        if generator is None:
            return None

        return GeneratorSerializer(generator).data


class GenerationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GenerationRule
        fields = ('id', 'generator_id', 'freq', 'dtstart', 'interval', 'count',
                  'until', 'bysetpos', 'bymonth', 'bymonthday', 'byyearday',
                  'byweekno', 'byweekday', 'byhour', 'byminute')
        read_only_fields = ('id', 'generator_id')


class PauseSerializer(serializers.ModelSerializer):
    content_type = ContentTypeField(read_only=True)
    generator = serializers.PrimaryKeyRelatedField(read_only=True)

    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Pause
        fields = ('content_type', 'object_id', 'generator',
                  'user', 'timestamp', 'reason')
        read_only_fields = ('content_type', 'object_id', 'generator', 'user', 'timestamp')


class ReadySerializer(serializers.ModelSerializer):
    content_type = ContentTypeField(read_only=True)
    generator = serializers.PrimaryKeyRelatedField(read_only=True)

    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Ready
        fields = ('content_type', 'object_id', 'generator',
                  'user', 'timestamp')
        read_only_fields = ('content_type', 'object_id', 'generator', 'user', 'timestamp')


class AgentSerializer(serializers.Serializer):
    content_type = serializers.SerializerMethodField()
    object_id = serializers.IntegerField(source='pk')
    repr = serializers.CharField(source='__repr__')

    pause = serializers.SerializerMethodField(required=False)
    ready = serializers.SerializerMethodField(required=False)

    def get_content_type(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return f'{ct.app_label}.{ct.model}'

    def get_pause(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        pause = models.Pause.objects.filter(content_type=ct, object_id=obj.pk).first()
        if pause is None:
            return None

        return PauseSerializer(pause).data

    def get_ready(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        ready = models.Ready.objects.filter(content_type=ct, object_id=obj.pk).first()
        if ready is None:
            return None

        return ReadySerializer(ready).data

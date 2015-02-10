from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from . import models


class ContentTypeField(serializers.RelatedField):
    def to_representation(self, value):
        return u'{value.app_label}.{value.model}'.format(value=value)

    def to_internal_value(self, data):
        app_label, model = data.split('.')
        return ContentType.objects.get_by_natural_key(app_label, model)


class GeneratorSerializer(serializers.ModelSerializer):
    content_type = ContentTypeField(queryset=ContentType.objects.all())

    class Meta(object):
        model = models.Generator
        fields = ('content_type', 'object_id',
                  'generating', 'generation_time', 'autogenerate',
                  'allow_pauses', 'minimum_between_generations')
        read_only_fields = ('content_type', 'object_id',
                            'generating', 'generation_time')


class GeneratorCreateSerializer(GeneratorSerializer):
    class Meta(GeneratorSerializer.Meta):
        read_only_fields = ('generating', 'generation_time')


class GenerationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GenerationRule
        fields = ('freq', 'dtstart', 'interval', 'count', 'until',
                  'bysetpos', 'bymonth', 'bymonthday', 'byyearday',
                  'byweekno', 'byweekday', 'byhour', 'byminute')


class PauseSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Pause
        fields = ('user', 'timestamp', 'reason')
        read_only_fields = ('user', 'timestamp')


class ReadySerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Ready
        fields = ('user', 'timestamp')
        read_only_fields = ('user', 'timestamp')


class AgentSerializer(serializers.Serializer):
    pause = PauseSerializer(read_only=True)
    ready = ReadySerializer(read_only=True)

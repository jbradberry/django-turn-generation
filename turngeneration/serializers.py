from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers, validators

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
                                     serializer_field.field_name, None)

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
        fields = ('content_type', 'object_id', 'generating',
                  'generation_time', 'force_generate', 'autogenerate',
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


class GenerationRuleSerializer(serializers.ModelSerializer):
    generator_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.GenerationRule
        fields = ('id', 'generator_id', 'freq', 'dtstart', 'interval', 'count',
                  'until', 'bysetpos', 'bymonth', 'bymonthday', 'byyearday',
                  'byweekno', 'byweekday', 'byhour', 'byminute')
        read_only_fields = ('id',)


class PauseSerializer(serializers.ModelSerializer):
    content_type = ContentTypeField(read_only=True, default=ReadOnlyDefault())
    object_id = serializers.IntegerField(read_only=True,
                                         default=ReadOnlyDefault())
    generator = serializers.PrimaryKeyRelatedField(read_only=True,
                                                   default=ReadOnlyDefault())

    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Pause
        fields = ('content_type', 'object_id', 'generator',
                  'user', 'timestamp', 'reason')
        read_only_fields = ('user', 'timestamp')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=models.Pause.objects.all(),
                fields=('content_type', 'object_id', 'generator'),
            )
        ]


class ReadySerializer(serializers.ModelSerializer):
    content_type = ContentTypeField(read_only=True, default=ReadOnlyDefault())
    object_id = serializers.IntegerField(read_only=True,
                                         default=ReadOnlyDefault())
    generator = serializers.PrimaryKeyRelatedField(read_only=True,
                                                   default=ReadOnlyDefault())

    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Ready
        fields = ('content_type', 'object_id', 'generator',
                  'user', 'timestamp')
        read_only_fields = ('user', 'timestamp')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=models.Ready.objects.all(),
                fields=('content_type', 'object_id', 'generator'),
            )
        ]


class AgentSerializer(serializers.Serializer):
    content_type = serializers.SerializerMethodField()
    object_id = serializers.IntegerField(source='pk')
    repr = serializers.CharField(source='__repr__')

    pause = serializers.SerializerMethodField(required=False)
    ready = serializers.SerializerMethodField(required=False)

    def get_content_type(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return u'{ct.app_label}.{ct.model}'.format(ct=ct)

    def get_pause(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        try:
            pause = models.Pause.objects.get(content_type=ct, object_id=obj.pk)
        except models.Pause.DoesNotExist:
            return None

        return PauseSerializer(pause).data

    def get_ready(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        try:
            ready = models.Ready.objects.get(content_type=ct, object_id=obj.pk)
        except models.Ready.DoesNotExist:
            return None

        return ReadySerializer(ready).data

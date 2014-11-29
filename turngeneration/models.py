from django.contrib.contenttypes import generic
from django.utils import timezone
from django.db import models

from celery import current_app as celery
from dateutil import rrule
import datetime
import pytz


class GenerationTime(models.Model):
    content_type = models.ForeignKey("contenttypes.ContentType")
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    generation_time = models.DateTimeField(null=True)
    task_id = models.TextField()

    autogenerate = models.BooleanField(default=True, blank=True)
    allow_pauses = models.BooleanField(default=True, blank=True)
    minimum_between_generations = models.PositiveIntegerField(
        null=True, blank=True)

    class Meta:
        unique_together = ('content_type', 'object_id')


class GenerationRule(models.Model):
    FREQUENCIES = (
        ('Yearly', rrule.YEARLY),
        ('Monthly', rrule.MONTHLY),
        ('Weekly', rrule.WEEKLY),
        ('Daily', rrule.DAILY),
        ('Hourly', rrule.HOURLY),
        ('Minutely', rrule.MINUTELY),
        # ignore SECONDLY
    )

    generator = models.ForeignKey(GenerationTime)

    freq = models.PositiveSmallIntegerField(choices=FREQUENCIES,
                                            default=rrule.DAILY, blank=True)
    dtstart = models.DateTimeField(blank=True, null=True)
    interval = models.PositiveIntegerField(blank=True, null=True)
    # ignore wkst
    count = models.PositiveIntegerField(blank=True, null=True)
    until = models.DateTimeField(blank=True, null=True)

    bysetpos = models.CommaSeparatedIntegerField(max_length=64, blank=True)
    bymonth = models.CommaSeparatedIntegerField(max_length=64, blank=True)
    bymonthday = models.CommaSeparatedIntegerField(max_length=64, blank=True)
    byyearday = models.CommaSeparatedIntegerField(max_length=64, blank=True)
    byweekno = models.CommaSeparatedIntegerField(max_length=64, blank=True)
    byweekday = models.CommaSeparatedIntegerField(max_length=64, blank=True)
    byhour = models.CommaSeparatedIntegerField(max_length=64, blank=True)
    byminute = models.CommaSeparatedIntegerField(max_length=64, blank=True)
    # ignore bysecond and byeaster

    @property
    def rrule(self):
        tz = timezone.get_current_timezone()

        kwargs = {}
        datetime_fields = ('dtstart', 'until')
        comma_fields = ('bysetpos', 'bymonth', 'bymonthday', 'byyearday',
                        'byweekno', 'byweekday', 'byhour', 'byminute')
        int_fields = ('interval', 'count')

        for field in int_fields + datetime_fields + comma_fields:
            value = getattr(self, field, None)
            if value is None:
                continue
            if field in datetime_fields:
                value = tz.normalize(value.astimezone(tz))
            elif field in comma_fields:
                value = [int(x.strip()) for x in value.split(',')]
            kwargs[field] = value

        return rrule.rrule(self.freq, **kwargs)


class Pause(models.Model):
    content_type = models.ForeignKey("contenttypes.ContentType")
    object_id = models.PositiveIntegerField()
    owner = generic.GenericForeignKey()

    generator = models.ForeignKey(GenerationTime, related_name='pauses')
    timestamp = models.DateTimeField(auto_now=True)
    reason = models.TextField()


class Ready(models.Model):
    content_type = models.ForeignKey("contenttypes.ContentType")
    object_id = models.PositiveIntegerField()
    owner = generic.GenericForeignKey()

    generator = models.ForeignKey(GenerationTime, related_name='readies')
    timestamp = models.DateTimeField()

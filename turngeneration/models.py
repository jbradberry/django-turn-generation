from django.contrib.contenttypes import generic
from django.utils import timezone
from django.db import models

from celery import current_app as celery
from dateutil import rrule
import datetime
import pytz


class Generator(models.Model):
    content_type = models.ForeignKey("contenttypes.ContentType")
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    generating = models.BooleanField(default=False, blank=True)

    generation_time = models.DateTimeField(null=True)
    task_id = models.TextField()

    autogenerate = models.BooleanField(default=True, blank=True)
    allow_pauses = models.BooleanField(default=True, blank=True)
    minimum_between_generations = models.PositiveIntegerField(
        null=True, blank=True)

    class Meta:
        unique_together = ('content_type', 'object_id')

    @property
    def rruleset(self):
        rset = rrule.rruleset()
        for rule in self.rules.all():
            rset.rrule(rule.rrule)

        return rset

    def next_time(self, cutoff=None):
        if cutoff is None:
            cutoff = datetime.datetime.utcnow()

        return self.rruleset.after(cutoff)


class GenerationRule(models.Model):
    FREQUENCIES = (
        (rrule.YEARLY, 'Yearly'),
        (rrule.MONTHLY, 'Monthly'),
        (rrule.WEEKLY, 'Weekly'),
        (rrule.DAILY, 'Daily'),
        (rrule.HOURLY, 'Hourly'),
        (rrule.MINUTELY, 'Minutely'),
        # ignore SECONDLY
    )

    generator = models.ForeignKey(Generator, related_name='rules')

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
        kwargs = {}
        datetime_fields = ('dtstart', 'until')
        comma_fields = ('bysetpos', 'bymonth', 'bymonthday', 'byyearday',
                        'byweekno', 'byweekday', 'byhour', 'byminute')
        int_fields = ('interval', 'count')

        for field in int_fields + datetime_fields + comma_fields:
            value = getattr(self, field, None)
            if field in comma_fields:
                value = [int(x.strip()) for x in value.split(',') if x.strip()]
            if field in datetime_fields and value is not None:
                value = value.replace(tzinfo=None)
            if value is None or value == []:
                continue
            kwargs[field] = value

        return rrule.rrule(self.freq, **kwargs)


class Pause(models.Model):
    content_type = models.ForeignKey("contenttypes.ContentType")
    object_id = models.PositiveIntegerField()
    agent = generic.GenericForeignKey()

    generator = models.ForeignKey(Generator, related_name='pauses')
    user = models.ForeignKey("auth.User", null=True)
    timestamp = models.DateTimeField(auto_now=True)
    reason = models.TextField()

    class Meta:
        unique_together = ('content_type', 'object_id', 'generator')


class Ready(models.Model):
    content_type = models.ForeignKey("contenttypes.ContentType")
    object_id = models.PositiveIntegerField()
    agent = generic.GenericForeignKey()

    generator = models.ForeignKey(Generator, related_name='readies')
    user = models.ForeignKey("auth.User", null=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('content_type', 'object_id', 'generator')

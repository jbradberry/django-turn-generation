from django.contrib.contenttypes import fields
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.utils import timezone

from celery import current_app as celery
from dateutil import rrule
import datetime
import pytz
import logging

from . import tasks

logger = logging.getLogger(__name__)


class Generator(models.Model):
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    realm = fields.GenericForeignKey()

    generating = models.BooleanField(default=False, blank=True)

    generation_time = models.DateTimeField(null=True)
    task_id = models.TextField()

    force_generate = models.BooleanField(default=True, blank=True)
    autogenerate = models.BooleanField(default=True, blank=True)
    allow_pauses = models.BooleanField(default=True, blank=True)
    minimum_between_generations = models.PositiveIntegerField(
        null=True, blank=True)

    class Meta:
        unique_together = ('content_type', 'object_id')

    def is_ready(self):
        from . import plugins
        plugin = plugins.get_plugin_for_model(self.realm)

        readies = set(ready.agent for ready in self.readies.all())
        if not readies:
            return False
        agents = plugin.related_agents(self.realm)
        if not agents:
            return False

        return all(agent in readies for agent in agents)

    def save(self, *args, **kwargs):
        if self.autogenerate and self.is_ready():
            tasks.ready_generation.apply_async((self.pk,))
        elif self.force_generate and not self.task_id:
            eta = self.next_time()
            if eta is not None:
                task_id = tasks.timed_generation.apply_async(
                    (self.pk,), eta=eta).id
                self.task_id, self.generation_time = task_id, eta
        elif not self.force_generate and self.task_id:
            celery.control.revoke(self.task_id)
            self.task_id, self.generation_time = '', None

        super(Generator, self).save(*args, **kwargs)

    @property
    def rruleset(self):
        rset = rrule.rruleset()
        for rule in self.rules.all():
            rset.rrule(rule.rrule)

        return rset

    def next_time(self, cutoff=None):
        if cutoff is None:
            cutoff = datetime.datetime.utcnow()

        nexttime = self.rruleset.after(cutoff)
        if nexttime is not None:
            return pytz.utc.localize(nexttime)

    @property
    def last_generation(self):
        try:
            return self.timestamps.latest()
        except ObjectDoesNotExist:
            return


class GenerationTime(models.Model):
    generator = models.ForeignKey(Generator, on_delete=models.CASCADE, related_name='timestamps')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        get_latest_by = "timestamp"


# FIXME: when a new one is saved and the generator doesn't already
# have a task queued, check to see if we should queue one.
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

    generator = models.ForeignKey(Generator, on_delete=models.CASCADE, related_name='rules')

    freq = models.PositiveSmallIntegerField(choices=FREQUENCIES,
                                            default=rrule.DAILY, blank=True)

    # NOTE: The resultant next_time will depend on the datetime that
    # it is called if the user does not fill out the dtstart field.
    dtstart = models.DateTimeField(blank=True, null=True)
    interval = models.PositiveIntegerField(blank=True, null=True)
    # ignore wkst
    count = models.PositiveIntegerField(blank=True, null=True)
    until = models.DateTimeField(blank=True, null=True)

    bysetpos = models.CharField(max_length=64, blank=True, validators=[validate_comma_separated_integer_list])
    bymonth = models.CharField(max_length=64, blank=True, validators=[validate_comma_separated_integer_list])
    bymonthday = models.CharField(max_length=64, blank=True, validators=[validate_comma_separated_integer_list])
    byyearday = models.CharField(max_length=64, blank=True, validators=[validate_comma_separated_integer_list])
    byweekno = models.CharField(max_length=64, blank=True, validators=[validate_comma_separated_integer_list])
    byweekday = models.CharField(max_length=64, blank=True, validators=[validate_comma_separated_integer_list])
    byhour = models.CharField(max_length=64, blank=True, validators=[validate_comma_separated_integer_list])
    byminute = models.CharField(max_length=64, blank=True, validators=[validate_comma_separated_integer_list])
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
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    agent = fields.GenericForeignKey()

    generator = models.ForeignKey(Generator, on_delete=models.CASCADE, related_name='pauses')
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    reason = models.TextField()

    class Meta:
        unique_together = ('content_type', 'object_id', 'generator')


class Ready(models.Model):
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    agent = fields.GenericForeignKey()

    generator = models.ForeignKey(Generator, on_delete=models.CASCADE, related_name='readies')
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('content_type', 'object_id', 'generator')

    def save(self, *args, **kwargs):
        super(Ready, self).save(*args, **kwargs)

        if self.generator.autogenerate and self.generator.is_ready():
            logger.debug(
                "Triggering autogeneration for: {0}".format(self.generator.pk))
            result = tasks.ready_generation.apply_async((self.generator.pk,))

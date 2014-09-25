from django.contrib.contenttypes import generic
from django.utils import timezone
from django.db import models

from celery import current_app as celery
import datetime

from .tasks import trigger_generation


class GenerationTime(models.Model):
    content_type = models.ForeignKey("contenttypes.ContentType")
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    generation_time = models.DateTimeField(null=True)
    task_id = models.TextField()

    autogenerate = models.BooleanField(default=True, blank=True)
    allow_pauses = models.BooleanField(default=True, blank=True)

    class Meta:
        unique_together = ('content_type', 'object_id')

    def next_time(self, last_generation=None):
        tz = timezone.get_current_timezone()

        next_datetimes = []
        for rule in self.rules.filter(active=True):
            if last_generation is None:
                if rule.date is None:
                    continue
                last_generation = timezone.now()

            base_time = last_generation.replace()
            if rule.at_least is not None:
                base_time += datetime.timedelta(minutes=rule.at_least)

            # Drop down to naive datetimes for the remainder of our
            # calculations.  We do this because we don't want a DST
            # transition to cause, for example, a specified time of
            # day in the rule to shift by an hour.
            base_time = timezone.make_naive(base_time, tz)

            next_gen = base_time.replace()

            if rule.time is not None:
                if rule.time < next_gen.time():
                    next_gen += datetime.timedelta(days=1)
                next_gen = next_gen.replace(hour=rule.time.hour,
                                            minute=rule.time.minute)

            if rule.date is not None:
                next_gen = next_gen.replace(year=rule.date.year,
                                            month=rule.date.month,
                                            day=rule.date.day)
            elif rule.weekday is not None:
                day_delta = (rule.weekday - next_gen.weekday()) % 7
                next_gen += datetime.timedelta(days=day_delta)

            if next_gen >= base_time:
                next_datetimes.append(timezone.make_aware(next_gen, tz))

        next_datetimes.sort()

        next_gen = None
        if next_datetimes:
            next_gen = next_datetimes[0]

        return next_gen

    def update_time(self, last_generation=None):
        if self.task_id:
            celery.control.revoke(self.task_id)

        next_gen = self.next_time(last_generation)
        request = trigger_generation.apply_async((self.pk,), eta=next_gen)

        self.generation_time = next_gen
        self.task_id = request.id
        self.save()



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

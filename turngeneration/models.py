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
    minimum_between_generations = models.PositiveIntegerField(
        null=True, blank=True)

    class Meta:
        unique_together = ('content_type', 'object_id')

    def next_time(self, last_generation=None):
        pass

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

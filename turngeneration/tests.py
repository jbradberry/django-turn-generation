import datetime

from django.utils import timezone
from django.test import TestCase
from django.db import models
from dateutil import rrule

from .models import GenerationTime, GenerationRule


class TestRealm(models.Model):
    pass


class GenerationRuleTestCase(TestCase):
    def setUp(self):
        self.realm = TestRealm.objects.create()
        self.gentime = GenerationTime(content_object=self.realm)
        self.gentime.save()

        self.now = datetime.datetime(2014, 11, 30, 10)

    def test_empty(self):
        next_time = self.gentime.next_time(self.now)
        self.assertIsNone(next_time)

    def test_daily(self):
        self.gentime.rules.create(freq=rrule.DAILY)

        self.assertEqual(self.gentime.rules.count(), 1)

        next_time = self.gentime.next_time(self.now)
        self.assertIsNotNone(next_time)

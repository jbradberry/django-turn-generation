import datetime

from django.utils import timezone
from django.test import TestCase
from django.db import models
from dateutil import rrule
import pytz

from .models import Generator, GenerationRule


class TestRealm(models.Model):
    pass


class GenerationRuleTestCase(TestCase):
    def setUp(self):
        self.realm = TestRealm.objects.create()
        self.gentime = Generator(content_object=self.realm)
        self.gentime.save()

        self.now = datetime.datetime(2014, 11, 30, 10)

    def test_empty(self):
        next_time = self.gentime.next_time(self.now)
        self.assertIsNone(next_time)

    def test_daily(self):
        self.gentime.rules.create(
            freq=rrule.DAILY,
            dtstart=datetime.datetime(2014, 11, 29, 18, tzinfo=pytz.utc)
        )

        self.assertEqual(self.gentime.rules.count(), 1)

        next_time = self.gentime.next_time(self.now)
        self.assertEqual(next_time, datetime.datetime(2014, 11, 30, 18))

    def test_weekly(self):
        self.gentime.rules.create(
            freq=rrule.WEEKLY,
            dtstart=datetime.datetime(2014, 11, 29, 18, tzinfo=pytz.utc)
        )

        self.assertEqual(self.gentime.rules.count(), 1)

        next_time = self.gentime.next_time(self.now)
        self.assertEqual(next_time, datetime.datetime(2014, 12, 6, 18))

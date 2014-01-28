from django.utils import timezone
from django.test import TestCase
from django.db import models

from .models import GenerationTime, GenerationRule

import datetime


class TestRealm(models.Model):
    pass


class NextTimeTestCase(TestCase):
    def setUp(self):
        self.realm = TestRealm.objects.create()
        self.gentime = GenerationTime(content_object=self.realm)
        self.gentime.save()

        self.tz = timezone.get_current_timezone()
        self.now = timezone.make_aware(
            datetime.datetime(2014, 1, 27, 21), self.tz)

    def test_empty(self):
        next_time = self.gentime.next_time(self.now)
        self.assertIsNone(next_time)

    def test_inactive(self):
        self.gentime.rules.create(date=datetime.date(2014, 1, 28),
                                  time=datetime.time(18, 0, 0),
                                  active=False)
        next_time = self.gentime.next_time(self.now)
        self.assertIsNone(next_time)

    def test_datetime(self):
        self.gentime.rules.create(date=datetime.date(2014, 1, 28),
                                  time=datetime.time(18, 0, 0))
        next_time = self.gentime.next_time(self.now)
        self.assertEqual(
            next_time,
            timezone.make_aware(datetime.datetime(2014, 1, 28, 18), self.tz)
        )

    def test_date(self):
        # Using just a date is underspecified, but the time portion will
        # wind up being the same as the last generation's time of day.

        self.gentime.rules.create(date=datetime.date(2014, 1, 28))
        next_time = self.gentime.next_time(self.now)
        self.assertEqual(
            next_time,
            timezone.make_aware(datetime.datetime(2014, 1, 28, 21), self.tz)
        )

    def test_time(self):
        # Using just a time is underspecified, but it'll just choose the next
        # date that can hit that time.

        self.gentime.rules.create(time=datetime.time(18, 0, 0))
        next_time = self.gentime.next_time(self.now)
        self.assertEqual(
            next_time,
            timezone.make_aware(datetime.datetime(2014, 1, 28, 18), self.tz)
        )

    def test_day_of_week(self):
        # Using just a day of the week is underspecified, but the time portion
        # will wind up being the same as the last generation's time of day.

        self.gentime.rules.create(weekday=GenerationRule.SUNDAY)
        next_time = self.gentime.next_time(self.now)
        self.assertEqual(
            next_time,
            timezone.make_aware(datetime.datetime(2014, 2, 2, 21), self.tz)
        )

    def test_at_least_minutes(self):
        self.gentime.rules.create(at_least=20)
        next_time = self.gentime.next_time(self.now)
        self.assertEqual(
            next_time,
            timezone.make_aware(datetime.datetime(2014, 1, 27, 21, 20), self.tz)
        )

    def test_datetime_in_the_past(self):
        self.gentime.rules.create(date=datetime.date(2014, 1, 26),
                                  time=datetime.time(18, 0, 0))
        next_time = self.gentime.next_time(self.now)
        self.assertIsNone(next_time)

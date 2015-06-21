import datetime

from django.contrib.auth.models import User
from django.utils import timezone
from django.test import TestCase
from mock import patch, call
from dateutil import rrule
import pytz

from ..models import Generator, GenerationTime, GenerationRule, Pause, Ready
from sample_project.sample_app.models import TestRealm, TestAgent


@patch('turngeneration.tasks.ready_generation')
@patch('turngeneration.tasks.timed_generation')
class AutoGenerateTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='player',
                                             password='password')

        self.realm = TestRealm.objects.create(slug='mygame')
        self.generator = Generator(realm=self.realm)
        self.generator.save()
        self.agent1 = self.realm.agents.create(slug='agent1')
        self.agent2 = self.realm.agents.create(slug='agent2')

    def test_autogenerate_when_ready_and_enabled(self, timed_task, ready_task):
        self.assertTrue(self.generator.autogenerate)

        Ready(agent=self.agent1,
              generator=self.generator,
              user=self.user).save()
        self.assertFalse(self.generator.is_ready())

        self.assertFalse(timed_task.mock_calls)
        self.assertFalse(ready_task.mock_calls)

        Ready(agent=self.agent2,
              generator=self.generator,
              user=self.user).save()
        self.assertTrue(self.generator.is_ready())

        self.assertFalse(timed_task.mock_calls)
        self.assertEqual(ready_task.mock_calls,
                         [call.apply_async((self.generator.pk,))])

    def test_no_autogenerate_when_ready_and_disabled(self, timed_task, ready_task):
        self.generator.autogenerate = False
        self.generator.save()

        self.assertFalse(self.generator.autogenerate)

        Ready(agent=self.agent1,
              generator=self.generator,
              user=self.user).save()
        self.assertFalse(self.generator.is_ready())

        self.assertFalse(timed_task.mock_calls)
        self.assertFalse(ready_task.mock_calls)

        Ready(agent=self.agent2,
              generator=self.generator,
              user=self.user).save()
        self.assertTrue(self.generator.is_ready())

        self.assertFalse(timed_task.mock_calls)
        self.assertFalse(ready_task.mock_calls)

    def test_still_autogenerate_when_paused(self, timed_task, ready_task):
        self.assertTrue(self.generator.autogenerate)
        self.assertTrue(self.generator.allow_pauses)

        Pause(agent=self.agent2,
              generator=self.generator,
              user=self.user,
              reason="1 week vacation.").save()

        Ready(agent=self.agent1,
              generator=self.generator,
              user=self.user).save()
        self.assertFalse(self.generator.is_ready())

        self.assertFalse(timed_task.mock_calls)
        self.assertFalse(ready_task.mock_calls)

        Ready(agent=self.agent2,
              generator=self.generator,
              user=self.user).save()
        self.assertTrue(self.generator.is_ready())

        self.assertFalse(timed_task.mock_calls)
        self.assertEqual(ready_task.mock_calls,
                         [call.apply_async((self.generator.pk,))])

    def test_no_autogenerate_when_paused_and_disabled(self, timed_task, ready_task):
        self.generator.autogenerate = False
        self.generator.save()

        self.assertFalse(self.generator.autogenerate)
        self.assertTrue(self.generator.allow_pauses)

        Pause(agent=self.agent2,
              generator=self.generator,
              user=self.user,
              reason="1 week vacation.").save()

        Ready(agent=self.agent1,
              generator=self.generator,
              user=self.user).save()
        self.assertFalse(self.generator.is_ready())

        self.assertFalse(timed_task.mock_calls)
        self.assertFalse(ready_task.mock_calls)

        Ready(agent=self.agent2,
              generator=self.generator,
              user=self.user).save()
        self.assertTrue(self.generator.is_ready())

        self.assertFalse(timed_task.mock_calls)
        self.assertFalse(ready_task.mock_calls)


class GenerationRuleTestCase(TestCase):
    def setUp(self):
        self.realm = TestRealm.objects.create()
        self.gentime = Generator(realm=self.realm)
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

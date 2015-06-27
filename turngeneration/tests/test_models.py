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
class GeneratorTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='player',
                                             password='password')

        self.realm = TestRealm.objects.create(slug='mygame')
        self.generator = Generator(realm=self.realm)
        self.generator.save()
        self.agent1 = self.realm.agents.create(slug='agent1')
        self.agent2 = self.realm.agents.create(slug='agent2')

    def test_is_ready(self, timed_task, ready_task):
        self.assertFalse(self.generator.is_ready())

        Ready(agent=self.agent1,
              generator=self.generator,
              user=self.user).save()

        self.assertFalse(self.generator.is_ready())

        Ready(agent=self.agent2,
              generator=self.generator,
              user=self.user).save()

        self.assertTrue(self.generator.is_ready())

    def test_enabling_autogen_when_ready(self, timed_task, ready_task):
        self.generator.autogenerate = False
        self.generator.save()

        self.assertFalse(self.generator.is_ready())

        Ready(agent=self.agent1,
              generator=self.generator,
              user=self.user).save()
        Ready(agent=self.agent2,
              generator=self.generator,
              user=self.user).save()

        self.assertTrue(self.generator.is_ready())
        self.assertFalse(timed_task.mock_calls)
        self.assertFalse(ready_task.mock_calls)

        self.generator.autogenerate = True
        self.generator.save()

        self.assertTrue(self.generator.is_ready())
        self.assertFalse(timed_task.mock_calls)
        self.assertEqual(ready_task.mock_calls,
                         [call.apply_async((self.generator.pk,))])

    def test_enabling_autogen_when_ready_and_paused(self, timed_task, ready_task):
        self.generator.autogenerate = False
        self.generator.save()

        self.assertFalse(self.generator.is_ready())

        Pause(agent=self.agent2,
              generator=self.generator,
              user=self.user,
              reason="1 week vacation.").save()

        Ready(agent=self.agent1,
              generator=self.generator,
              user=self.user).save()
        Ready(agent=self.agent2,
              generator=self.generator,
              user=self.user).save()

        self.assertTrue(self.generator.is_ready())
        self.assertFalse(timed_task.mock_calls)
        self.assertFalse(ready_task.mock_calls)

        self.generator.autogenerate = True
        self.generator.save()

        self.assertTrue(self.generator.is_ready())
        self.assertFalse(timed_task.mock_calls)
        self.assertEqual(ready_task.mock_calls,
                         [call.apply_async((self.generator.pk,))])

    def test_enabling_forcegen_when_no_existing_task(self, timed_task, ready_task):
        mocktask = timed_task.apply_async.return_value
        mocktask.id = 'fake'

        self.generator.rules.create(
            freq=rrule.DAILY,
            dtstart=datetime.datetime(2014, 11, 29, 18, tzinfo=pytz.utc)
        )
        self.generator.force_generate = False
        self.generator.save()

        self.assertFalse(self.generator.task_id)
        self.assertIsNone(self.generator.generation_time)

        self.generator.force_generate = True
        self.generator.save()

        self.assertTrue(self.generator.task_id)
        self.assertIsNotNone(self.generator.generation_time)

    def test_enabling_forcegen_when_task_exists(self, timed_task, ready_task):
        Generator.objects.filter(id=self.generator.id).update(
            force_generate=False, task_id='fake',
            generation_time=datetime.datetime(2014, 11, 29, 18, tzinfo=pytz.utc)
        )

        generator = Generator.objects.get(id=self.generator.id)
        generator.force_generate = True
        generator.save()

        self.assertEqual(generator.task_id, 'fake')
        self.assertEqual(generator.generation_time,
                         datetime.datetime(2014, 11, 29, 18, tzinfo=pytz.utc))
        self.assertFalse(timed_task.mock_calls)

    def test_disabling_forcegen_when_task_exists(self, timed_task, ready_task):
        Generator.objects.filter(id=self.generator.id).update(
            task_id='fake',
            generation_time=datetime.datetime(2014, 11, 29, 18, tzinfo=pytz.utc)
        )

        generator = Generator.objects.get(id=self.generator.id)
        with patch('celery.current_app.control') as control:
            generator.force_generate = False
            generator.save()

            self.assertEqual(control.mock_calls, [call.revoke('fake')])

        self.assertFalse(generator.task_id)
        self.assertIsNone(generator.generation_time)

    def test_disabling_forcegen_when_no_existing_task(self, timed_task, ready_task):
        self.assertTrue(self.generator.force_generate)
        self.assertFalse(self.generator.task_id)
        self.assertIsNone(self.generator.generation_time)

        with patch('celery.current_app.control') as control:
            self.generator.force_generate = False
            self.generator.save()

            self.assertFalse(control.mock_calls)

        self.assertFalse(self.generator.task_id)
        self.assertIsNone(self.generator.generation_time)


class GenerationRuleTestCase(TestCase):
    def setUp(self):
        self.realm = TestRealm.objects.create()
        self.generator = Generator(realm=self.realm)
        self.generator.save()

        self.now = datetime.datetime(2014, 11, 30, 10)

    def test_empty(self):
        next_time = self.generator.next_time(self.now)
        self.assertIsNone(next_time)

    def test_daily(self):
        self.generator.rules.create(
            freq=rrule.DAILY,
            dtstart=datetime.datetime(2014, 11, 29, 18, tzinfo=pytz.utc)
        )

        self.assertEqual(self.generator.rules.count(), 1)

        next_time = self.generator.next_time(self.now)
        self.assertEqual(next_time,
                         datetime.datetime(2014, 11, 30, 18, tzinfo=pytz.utc))

    def test_weekly(self):
        self.generator.rules.create(
            freq=rrule.WEEKLY,
            dtstart=datetime.datetime(2014, 11, 29, 18, tzinfo=pytz.utc)
        )

        self.assertEqual(self.generator.rules.count(), 1)

        next_time = self.generator.next_time(self.now)
        self.assertEqual(next_time,
                         datetime.datetime(2014, 12, 6, 18, tzinfo=pytz.utc))


@patch('turngeneration.tasks.ready_generation')
@patch('turngeneration.tasks.timed_generation')
class ReadyTestCase(TestCase):
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

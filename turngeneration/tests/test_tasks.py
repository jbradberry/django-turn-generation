from django.test import TestCase
from mock import patch

from sample_app.models import TestRealm
from ..models import Generator, GenerationTime, Ready, Pause


class TimedGenerationTestCase(TestCase):
    def setUp(self):
        from .. import tasks

        self.timed_generation = tasks.timed_generation
        self.ready_generation = tasks.ready_generation

        self.realm = TestRealm.objects.create()
        self.generator = Generator(realm=self.realm)
        self.generator.save()

    def test_simple(self):
        self.assertEqual(GenerationTime.objects.count(), 0)
        try:
            result = self.timed_generation.apply((self.generator.pk,), throw=True)
        except Exception as e:
            self.fail(e)
        self.assertEqual(result.status, 'SUCCESS')
        self.assertEqual(GenerationTime.objects.count(), 1)


class ReadyGenerationTestCase(TestCase):
    def setUp(self):
        from .. import tasks

        self.timed_generation = tasks.timed_generation
        self.ready_generation = tasks.ready_generation

        self.realm = TestRealm.objects.create()
        self.generator = Generator(realm=self.realm)
        self.generator.save()

    @patch.object(Generator, 'is_ready', autospec=True)
    def test_simple(self, is_ready):
        is_ready.return_value = True

        self.assertEqual(GenerationTime.objects.count(), 0)
        try:
            result = self.ready_generation.apply((self.generator.pk,), throw=True)
        except Exception as e:
            self.fail(e)
        self.assertEqual(result.status, 'SUCCESS')
        self.assertEqual(GenerationTime.objects.count(), 1)


class IntegrationTestCase(TestCase):
    def setUp(self):
        from .. import tasks

        self.timed_generation = tasks.timed_generation
        self.ready_generation = tasks.ready_generation

        self.realm = TestRealm.objects.create()
        self.generator = Generator(realm=self.realm)
        self.generator.save()

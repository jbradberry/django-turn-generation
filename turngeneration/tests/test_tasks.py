from django.test import TestCase

from sample_project.sample_app.models import TestRealm
from ..models import Generator, GenerationTime


class TimedGenerationTestCase(TestCase):
    def setUp(self):
        from .. import tasks

        self.timed_generation = tasks.timed_generation
        self.ready_generation = tasks.ready_generation

        self.realm = TestRealm.objects.create()
        self.gentime = Generator(realm=self.realm)
        self.gentime.save()

    def test_simple(self):
        self.assertEqual(GenerationTime.objects.count(), 0)
        try:
            result = self.timed_generation.apply((self.gentime.pk,), throw=True)
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
        self.gentime = Generator(realm=self.realm)
        self.gentime.save()

    def test_simple(self):
        self.assertEqual(GenerationTime.objects.count(), 0)
        try:
            result = self.ready_generation.apply((self.gentime.pk,), throw=True)
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
        self.gentime = Generator(realm=self.realm)
        self.gentime.save()

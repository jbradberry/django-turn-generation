from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase

from .. import models
from sample_project.sample_app.models import TestRealm, TestAgent


class PauseViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             password='password')
        self.realm = TestRealm(slug='500years')
        self.realm.save()
        self.agent = TestAgent(realm=self.realm, slug='bob')
        self.agent.save()
        self.client.login(username='test', password='password')

    def test_realm_does_not_exist(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk + 1,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Pause.objects.count(), 0)

    def test_generator_does_not_exist(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Pause.objects.count(), 0)

    def test_agent_does_not_exist(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        generator = models.Generator(content_object=self.realm)
        generator.save()

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent.pk + 1})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url,
            {'reason': 'laziness'},
            follow=True
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Pause.objects.count(), 0)

    def test_user_does_not_have_permission(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        generator = models.Generator(content_object=self.realm)
        generator.save()

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url,
            {'reason': 'laziness'},
            follow=True
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 403)

        self.assertEqual(models.Pause.objects.count(), 0)

    def test_pauses_not_allowed(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        generator = models.Generator(content_object=self.realm,
                                     allow_pauses=False)
        generator.save()
        self.agent.user = self.user
        self.agent.save()

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url,
            {'reason': 'laziness'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pauses are not enabled.")

        self.assertEqual(models.Pause.objects.count(), 0)

    def test_success(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        generator = models.Generator(content_object=self.realm)
        generator.save()
        self.agent.user = self.user
        self.agent.save()

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url,
            {'reason': 'laziness'},
            follow=True
        )
        self.assertEqual(response.status_code, 201)

        self.assertEqual(models.Pause.objects.count(), 1)

    def test_already_paused(self):
        generator = models.Generator(content_object=self.realm)
        generator.save()
        self.agent.user = self.user
        self.agent.save()

        pause = models.Pause(agent=self.agent, generator=generator)
        pause.save()
        self.assertEqual(models.Pause.objects.count(), 1)

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(realm_url,
            {'reason': 'laziness'},
            follow=True
        )
        self.assertContains(response,
            "The fields content_type, object_id, generator must make a"
            " unique set.",
            status_code=400
        )

        self.assertEqual(models.Pause.objects.count(), 1)

    def test_pauses_not_allowed_can_still_unpause(self):
        pass

    def test_already_unpaused(self):
        pass


class ReadyViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             password='password')
        self.realm = TestRealm(slug='500years')
        self.realm.save()
        self.agent = TestAgent(realm=self.realm, slug='bob')
        self.agent.save()
        self.client.login(username='test', password='password')

    def test_already_ready(self):
        pass

    def test_can_mark_ready_while_paused(self):
        pass

    def test_already_unready(self):
        pass

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from mock import patch, call

from .. import models
from sample_project.sample_app.models import TestRealm, TestAgent


class RealmListViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             password='password')
        self.realm = TestRealm(slug='500years')
        self.realm.save()
        self.agent = TestAgent(realm=self.realm, slug='bob')
        self.agent.save()
        self.client.login(username='test', password='password')

    def test_realm_type_does_not_exist(self):
        url = reverse('realm_list',
                      kwargs={'realm_alias': 'starsweb'})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_success(self):
        url = reverse('realm_list',
                      kwargs={'realm_alias': 'testrealm'})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class RealmRetrieveViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             password='password')
        self.realm = TestRealm(slug='500years')
        self.realm.save()
        self.agent = TestAgent(realm=self.realm, slug='bob')
        self.agent.save()
        self.client.login(username='test', password='password')

    def test_realm_type_does_not_exist(self):
        url = reverse('realm_detail',
                      kwargs={'realm_alias': 'starsweb',
                              'pk': 1})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_realm_does_not_exist(self):
        url = reverse('realm_detail',
                      kwargs={'realm_alias': 'testrealm',
                              'pk': self.realm.pk + 1})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_success(self):
        url = reverse('realm_detail',
                      kwargs={'realm_alias': 'testrealm',
                              'pk': self.realm.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('content_type'),
                         "sample_app.testrealm")


class GeneratorViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             password='password')
        self.realm = TestRealm(slug='500years')
        self.realm.save()
        self.agent = TestAgent(realm=self.realm, slug='bob')
        self.agent.save()
        self.client.login(username='test', password='password')

    def test_realm_type_does_not_exist(self):
        url = reverse('generator',
                      kwargs={'realm_alias': 'starsweb',
                              'realm_pk': 1})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(url, {}, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.put(url, {}, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_realm_does_not_exist(self):
        url = reverse('generator',
                      kwargs={'realm_alias': 'testrealm',
                              'realm_pk': self.realm.pk + 1})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(url, {}, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.put(url, {}, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_generator_does_not_exist(self):
        url = reverse('generator',
                      kwargs={'realm_alias': 'testrealm',
                              'realm_pk': self.realm.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_does_not_have_permission(self):
        generator = models.Generator(realm=self.realm)
        generator.save()

        url = reverse('generator',
                      kwargs={'realm_alias': 'testrealm',
                              'realm_pk': self.realm.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('content_type'),
                         "sample_app.testrealm")

        response = self.client.post(url, {}, follow=True)
        self.assertEqual(response.status_code, 403)

        response = self.client.put(url, {}, follow=True)
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(url, follow=True)
        self.assertEqual(response.status_code, 403)

        self.assertEqual(models.Generator.objects.count(), 1)

    def test_success(self):
        self.user.is_staff = True
        self.user.save()

        url = reverse('generator',
                      kwargs={'realm_alias': 'testrealm',
                              'realm_pk': self.realm.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(url, {'allow_pauses': True},
                                    follow=True)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('allow_pauses'), True)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('allow_pauses'), True)

        response = self.client.put(url, {'allow_pauses': False}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('allow_pauses'), False)

        response = self.client.delete(url, follow=True)
        self.assertEqual(response.status_code, 204)

        self.assertEqual(models.Generator.objects.count(), 0)


class GenerationRuleListViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             password='password')
        self.realm = TestRealm(slug='500years')
        self.realm.save()
        self.agent = TestAgent(realm=self.realm, slug='bob')
        self.agent.save()
        self.client.login(username='test', password='password')

    def test_realm_type_does_not_exist(self):
        url = reverse('generation_rules_list',
                      kwargs={'realm_alias': 'starsweb',
                              'realm_pk': 1})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(url, {}, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_realm_does_not_exist(self):
        url = reverse('generation_rules_list',
                      kwargs={'realm_alias': 'testrealm',
                              'realm_pk': self.realm.pk + 1})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(url, {}, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_generator_does_not_exist(self):
        url = reverse('generation_rules_list',
                      kwargs={'realm_alias': 'testrealm',
                              'realm_pk': self.realm.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(url, {}, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_user_does_not_have_permission(self):
        generator = models.Generator(realm=self.realm)
        generator.save()

        url = reverse('generation_rules_list',
                      kwargs={'realm_alias': 'testrealm',
                              'realm_pk': self.realm.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        response = self.client.post(url, {}, follow=True)
        self.assertEqual(response.status_code, 403)

        self.assertEqual(models.GenerationRule.objects.count(), 0)

    def test_success(self):
        generator = models.Generator(realm=self.realm)
        generator.save()
        self.user.is_staff = True
        self.user.save()

        url = reverse('generation_rules_list',
                      kwargs={'realm_alias': 'testrealm',
                              'realm_pk': self.realm.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        response = self.client.post(url, {}, follow=True)
        self.assertEqual(response.status_code, 201)

        self.assertEqual(models.GenerationRule.objects.count(), 1)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class GenerationRuleViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             password='password')
        self.realm = TestRealm(slug='500years')
        self.realm.save()
        self.agent = TestAgent(realm=self.realm, slug='bob')
        self.agent.save()
        self.client.login(username='test', password='password')
        self.generator = models.Generator(realm=self.realm)
        self.generator.save()
        self.rule = models.GenerationRule(generator=self.generator)
        self.rule.save()

    def test_realm_type_does_not_exist(self):
        url = reverse('generation_rule_detail',
                      kwargs={'realm_alias': 'starsgame',
                              'realm_pk': 1,
                              'pk': self.rule.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        response = self.client.put(url, {}, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_realm_does_not_exist(self):
        url = reverse('generation_rule_detail',
                      kwargs={'realm_alias': 'testrealm',
                              'realm_pk': self.realm.pk + 1,
                              'pk': self.rule.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        response = self.client.put(url, {}, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_generator_does_not_exist(self):
        self.generator.delete()

        url = reverse('generation_rule_detail',
                      kwargs={'realm_alias': 'testrealm',
                              'realm_pk': self.realm.pk,
                              'pk': 1})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # TODO: do we want a 403 when the generator doesn't exist?
        response = self.client.put(url, {}, follow=True)
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_rule_does_not_exist(self):
        url = reverse('generation_rule_detail',
                      kwargs={'realm_alias': 'testrealm',
                              'realm_pk': self.realm.pk,
                              'pk': self.rule.pk + 1})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # TODO: do we want a 403 when the rule doesn't exist?
        response = self.client.put(url, {}, follow=True)
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_rule_exists(self):
        url = reverse('generation_rule_detail',
                      kwargs={'realm_alias': 'testrealm',
                              'realm_pk': self.realm.pk,
                              'pk': self.rule.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('id'), self.rule.id)
        self.assertEqual(response.data.get('generator_id'),
                         self.generator.id)

    def test_user_does_not_have_permission(self):
        url = reverse('generation_rule_detail',
                      kwargs={'realm_alias': 'testrealm',
                              'realm_pk': self.realm.pk,
                              'pk': self.rule.pk})

        response = self.client.put(url, {'freq': 2}, follow=True)
        self.assertEqual(response.status_code, 403)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('freq'), 3)

    def test_user_has_permission(self):
        self.user.is_staff = True
        self.user.save()

        url = reverse('generation_rule_detail',
                      kwargs={'realm_alias': 'testrealm',
                              'realm_pk': self.realm.pk,
                              'pk': self.rule.pk})

        response = self.client.put(url, {'freq': 2}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('freq'), 2)


class AgentListViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             password='password')
        self.realm = TestRealm(slug='500years')
        self.realm.save()
        self.agent = TestAgent(realm=self.realm, slug='bob')
        self.agent.save()
        self.client.login(username='test', password='password')

    def test_realm_type_does_not_exist(self):
        realm_url = reverse('agent_list',
                            kwargs={'realm_alias': 'starsweb',
                                    'realm_pk': 1,
                                    'agent_alias': 'testagent'})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

    def test_realm_does_not_exist(self):
        realm_url = reverse('agent_list',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk + 1,
                                    'agent_alias': 'testagent'})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

    def test_generator_does_not_exist(self):
        realm_url = reverse('agent_list',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent'})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

    def test_agent_type_does_not_exist(self):
        realm_url = reverse('agent_list',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'starsrace'})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

    def test_success(self):
        generator = models.Generator(realm=self.realm)
        generator.save()

        realm_url = reverse('agent_list',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent'})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class AgentRetrieveViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             password='password')
        self.realm = TestRealm(slug='500years')
        self.realm.save()
        self.agent1 = self.realm.agents.create(slug='agent1')
        self.agent2 = self.realm.agents.create(slug='agent2')
        self.client.login(username='test', password='password')

    def test_realm_type_does_not_exist(self):
        realm_url = reverse('agent_detail',
                            kwargs={'realm_alias': 'starsgame',
                                    'realm_pk': 1,
                                    'agent_alias': 'testagent',
                                    'pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

    def test_realm_does_not_exist(self):
        realm_url = reverse('agent_detail',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk + 1,
                                    'agent_alias': 'testagent',
                                    'pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

    def test_generator_does_not_exist(self):
        realm_url = reverse('agent_detail',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

    def test_agent_type_does_not_exist(self):
        generator = models.Generator(realm=self.realm)
        generator.save()

        realm_url = reverse('agent_detail',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'starsrace',
                                    'pk': 1})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

    def test_agent_does_not_exist(self):
        generator = models.Generator(realm=self.realm)
        generator.save()

        realm_url = reverse('agent_detail',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'pk': self.agent2.pk + 1})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

    def test_unpaused_unready(self):
        generator = models.Generator(realm=self.realm)
        generator.save()

        realm_url = reverse('agent_detail',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('content_type'), 'sample_app.testagent')
        self.assertIsNone(response.data.get('pause'))
        self.assertIsNone(response.data.get('ready'))

    def test_unpaused_ready(self):
        generator = models.Generator(realm=self.realm)
        generator.save()

        ready = models.Ready(agent=self.agent1, generator=generator,
                             user=self.user)
        ready.save()

        realm_url = reverse('agent_detail',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('content_type'), 'sample_app.testagent')
        self.assertIsNone(response.data.get('pause'))
        self.assertIsNotNone(response.data.get('ready'))

    def test_paused_unready(self):
        generator = models.Generator(realm=self.realm)
        generator.save()

        pause = models.Pause(agent=self.agent1, generator=generator,
                             user=self.user)
        pause.save()

        realm_url = reverse('agent_detail',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('content_type'), 'sample_app.testagent')
        self.assertIsNotNone(response.data.get('pause'))
        self.assertIsNone(response.data.get('ready'))

    def test_paused_ready(self):
        generator = models.Generator(realm=self.realm)
        generator.save()

        pause = models.Pause(agent=self.agent1, generator=generator,
                             user=self.user)
        pause.save()
        ready = models.Ready(agent=self.agent1, generator=generator,
                             user=self.user)
        ready.save()

        realm_url = reverse('agent_detail',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('content_type'), 'sample_app.testagent')
        self.assertIsNotNone(response.data.get('pause'))
        self.assertIsNotNone(response.data.get('ready'))


class PauseViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             password='password')
        self.realm = TestRealm(slug='500years')
        self.realm.save()
        self.agent1 = self.realm.agents.create(slug='agent1')
        self.agent2 = self.realm.agents.create(slug='agent2')
        self.client.login(username='test', password='password')

    def test_realm_type_does_not_exist(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'starsgame',
                                    'realm_pk': 1,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Pause.objects.count(), 0)

    def test_realm_does_not_exist(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk + 1,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

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
                                    'agent_pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Pause.objects.count(), 0)

    def test_agent_type_does_not_exist(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        generator = models.Generator(realm=self.realm)
        generator.save()

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'starsrace',
                                    'agent_pk': 1})

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

    def test_agent_does_not_exist(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        generator = models.Generator(realm=self.realm)
        generator.save()

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent2.pk + 1})

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

        generator = models.Generator(realm=self.realm)
        generator.save()

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

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

        generator = models.Generator(realm=self.realm,
                                     allow_pauses=False)
        generator.save()
        self.agent1.user = self.user
        self.agent1.save()

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url,
            {'reason': 'laziness'},
            follow=True
        )
        self.assertEqual(response.status_code, 403)

        self.assertEqual(models.Pause.objects.count(), 0)

    def test_success(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        generator = models.Generator(realm=self.realm)
        generator.save()
        self.agent1.user = self.user
        self.agent1.save()

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url,
            {'reason': 'laziness'},
            follow=True
        )
        self.assertEqual(response.status_code, 201)

        self.assertEqual(models.Pause.objects.count(), 1)

    def test_already_paused(self):
        generator = models.Generator(realm=self.realm)
        generator.save()
        self.agent1.user = self.user
        self.agent1.save()

        pause = models.Pause(agent=self.agent1, generator=generator)
        pause.save()
        self.assertEqual(models.Pause.objects.count(), 1)

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

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
        generator = models.Generator(realm=self.realm,
                                     allow_pauses=False)
        generator.save()
        self.agent1.user = self.user
        self.agent1.save()

        pause = models.Pause(agent=self.agent1, generator=generator)
        pause.save()
        self.assertEqual(models.Pause.objects.count(), 1)

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 204)

        self.assertEqual(models.Pause.objects.count(), 0)

    def test_already_unpaused(self):
        generator = models.Generator(realm=self.realm)
        generator.save()
        self.agent1.user = self.user
        self.agent1.save()

        self.assertEqual(models.Pause.objects.count(), 0)

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Pause.objects.count(), 0)

    def test_can_pause_while_ready(self):
        generator = models.Generator(realm=self.realm)
        generator.save()
        self.agent1.user = self.user
        self.agent1.save()

        ready = models.Ready(agent=self.agent1, generator=generator)
        ready.save()
        self.assertEqual(models.Ready.objects.count(), 1)

        realm_url = reverse('pause',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

        response = self.client.post(realm_url,
            {'reason': 'laziness'},
            follow=True
        )
        self.assertEqual(response.status_code, 201)

        self.assertEqual(models.Ready.objects.count(), 1)
        self.assertEqual(models.Pause.objects.count(), 1)


class ReadyViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             password='password')
        self.realm = TestRealm(slug='500years')
        self.realm.save()
        self.agent1 = self.realm.agents.create(slug='agent1')
        self.agent2 = self.realm.agents.create(slug='agent2')
        self.client.login(username='test', password='password')

    def test_realm_type_does_not_exist(self):
        self.assertEqual(models.Ready.objects.count(), 0)

        realm_url = reverse('ready',
                            kwargs={'realm_alias': 'starsgame',
                                    'realm_pk': 1,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Ready.objects.count(), 0)

    def test_realm_does_not_exist(self):
        self.assertEqual(models.Ready.objects.count(), 0)

        realm_url = reverse('ready',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk + 1,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Ready.objects.count(), 0)

    def test_generator_does_not_exist(self):
        self.assertEqual(models.Ready.objects.count(), 0)

        realm_url = reverse('ready',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Ready.objects.count(), 0)

    def test_agent_type_does_not_exist(self):
        self.assertEqual(models.Ready.objects.count(), 0)

        generator = models.Generator(realm=self.realm)
        generator.save()

        realm_url = reverse('ready',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'starsrace',
                                    'agent_pk': 1})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Ready.objects.count(), 0)

    def test_agent_does_not_exist(self):
        self.assertEqual(models.Ready.objects.count(), 0)

        generator = models.Generator(realm=self.realm)
        generator.save()

        realm_url = reverse('ready',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent2.pk + 1})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Ready.objects.count(), 0)

    def test_user_does_not_have_permission(self):
        generator = models.Generator(realm=self.realm)
        generator.save()

        self.assertEqual(models.Ready.objects.count(), 0)

        realm_url = reverse('ready',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 403)

        self.assertEqual(models.Ready.objects.count(), 0)

        ready = models.Ready(agent=self.agent1, generator=generator)
        ready.save()

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 403)

        self.assertEqual(models.Ready.objects.count(), 1)

    def test_success(self):
        self.assertEqual(models.Ready.objects.count(), 0)

        generator = models.Generator(realm=self.realm)
        generator.save()
        self.agent1.user = self.user
        self.agent1.save()

        realm_url = reverse('ready',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 201)

        self.assertEqual(models.Ready.objects.count(), 1)

    def test_already_ready(self):
        generator = models.Generator(realm=self.realm)
        generator.save()
        self.agent1.user = self.user
        self.agent1.save()

        ready = models.Ready(agent=self.agent1, generator=generator)
        ready.save()
        self.assertEqual(models.Ready.objects.count(), 1)

        realm_url = reverse('ready',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(realm_url, follow=True)
        self.assertContains(response,
            "The fields content_type, object_id, generator must make a"
            " unique set.",
            status_code=400
        )

        self.assertEqual(models.Ready.objects.count(), 1)

    def test_can_mark_ready_while_paused(self):
        generator = models.Generator(realm=self.realm)
        generator.save()
        self.agent1.user = self.user
        self.agent1.save()

        pause = models.Pause(agent=self.agent1, generator=generator,
                             reason='laziness')
        pause.save()
        self.assertEqual(models.Ready.objects.count(), 0)
        self.assertEqual(models.Pause.objects.count(), 1)

        realm_url = reverse('ready',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 201)

        self.assertEqual(models.Ready.objects.count(), 1)
        self.assertEqual(models.Pause.objects.count(), 1)

    def test_already_unready(self):
        generator = models.Generator(realm=self.realm)
        generator.save()
        self.agent1.user = self.user
        self.agent1.save()

        self.assertEqual(models.Ready.objects.count(), 0)

        realm_url = reverse('ready',
                            kwargs={'realm_alias': 'testrealm',
                                    'realm_pk': self.realm.pk,
                                    'agent_alias': 'testagent',
                                    'agent_pk': self.agent1.pk})

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Ready.objects.count(), 0)

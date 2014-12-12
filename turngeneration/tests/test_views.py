from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase

from .. import models
from sample_project.sample_app.models import TestRealm, TestOwner


class PauseViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             password='password')
        self.realm = TestRealm(slug='500years')
        self.realm.save()
        self.owner = TestOwner(realm=self.realm, slug='bob')
        self.owner.save()
        self.client.login(username='test', password='password')

    def test_realm_does_not_exist(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        realm_url = reverse('turngeneration:pause_view',
                            kwargs={'realm_slug': 'ulf-war',
                                    'owner_slug': 'bob'},
                            current_app="sample_app")

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Pause.objects.count(), 0)

    def test_generator_does_not_exist(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        realm_url = reverse('turngeneration:pause_view',
                            kwargs={'realm_slug': '500years',
                                    'owner_slug': 'bob'},
                            current_app="sample_app")

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Pause.objects.count(), 0)

    def test_owner_does_not_exist(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        generator = models.Generator(content_object=self.realm)
        generator.save()

        realm_url = reverse('turngeneration:pause_view',
                            kwargs={'realm_slug': '500years',
                                    'owner_slug': 'duelafn'},
                            current_app="sample_app")

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(realm_url, follow=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(models.Pause.objects.count(), 0)

    def test_user_does_not_have_permission(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        generator = models.Generator(content_object=self.realm)
        generator.save()

        realm_url = reverse('turngeneration:pause_view',
                            kwargs={'realm_slug': '500years',
                                    'owner_slug': 'bob'},
                            current_app="sample_app")

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 403)

        response = self.client.post(realm_url,
            {'reason': 'laziness'},
            follow=True
        )
        self.assertEqual(response.status_code, 403)

        self.assertEqual(models.Pause.objects.count(), 0)

    def test_pauses_not_allowed(self):
        self.assertEqual(models.Pause.objects.count(), 0)

        generator = models.Generator(content_object=self.realm,
                                     allow_pauses=False)
        generator.save()
        self.owner.user = self.user
        self.owner.save()

        realm_url = reverse('turngeneration:pause_view',
                            kwargs={'realm_slug': '500years',
                                    'owner_slug': 'bob'},
                            current_app="sample_app")

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 200)

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
        self.owner.user = self.user
        self.owner.save()

        realm_url = reverse('turngeneration:pause_view',
                            kwargs={'realm_slug': '500years',
                                    'owner_slug': 'bob'},
                            current_app="sample_app")

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(realm_url,
            {'reason': 'laziness'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(models.Pause.objects.count(), 1)

    def test_already_paused(self):
        generator = models.Generator(content_object=self.realm)
        generator.save()
        self.owner.user = self.user
        self.owner.save()

        pause = models.Pause(owner=self.owner, generator=generator)
        pause.save()
        self.assertEqual(models.Pause.objects.count(), 1)

        realm_url = reverse('turngeneration:pause_view',
                            kwargs={'realm_slug': '500years',
                                    'owner_slug': 'bob'},
                            current_app="sample_app")

        response = self.client.get(realm_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(realm_url,
            {'reason': 'laziness'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have already paused.")

        self.assertEqual(models.Pause.objects.count(), 1)

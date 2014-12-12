from django.db import models


class TestRealm(models.Model):
    slug = models.CharField(max_length=16)

    def get_absolute_url(self):
        return ''


class TestOwner(models.Model):
    realm = models.ForeignKey(TestRealm, related_name='owners', null=True)
    slug = models.CharField(max_length=16)
    user = models.ForeignKey('auth.User', null=True)

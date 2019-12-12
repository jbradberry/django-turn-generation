from django.db import models


class TestRealm(models.Model):
    slug = models.CharField(max_length=16)

    def get_absolute_url(self):
        return ''

    def generate(self):
        pass


class TestAgent(models.Model):
    realm = models.ForeignKey(TestRealm, on_delete=models.SET_NULL, related_name='agents', null=True)
    slug = models.CharField(max_length=16)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)

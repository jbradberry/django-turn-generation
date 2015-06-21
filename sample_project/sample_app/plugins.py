from django.contrib.contenttypes.models import ContentType

from . import models


class TurnGeneration(object):
    realm_types = {
        'testrealm': 'sample_app.testrealm',
    }

    agent_types = {
        'testagent': 'sample_app.testagent',
    }

    permissions = {
        'turngeneration.add_generator': '_is_host',
        'turngeneration.change_generator': '_is_host',
        'turngeneration.delete_generator': '_is_host',
        'turngeneration.add_generationrule': '_is_host',
        'turngeneration.change_generationrule': '_is_host',
        'turngeneration.delete_generationrule': '_is_host',
        'turngeneration.add_pause': '_is_player',
        'turngeneration.change_pause': '_is_player',
        'turngeneration.delete_pause': '_is_player',
        'turngeneration.add_ready': '_is_player',
        'turngeneration.change_ready': '_is_player',
        'turngeneration.delete_ready': '_is_player',
    }

    def related_agents(self, realm, agent_type=None):
        ct = ContentType.objects.get_for_model(models.TestAgent)
        if agent_type is None:
            agent_type = ct
        if agent_type != ct:
            return
        return realm.agents.all()

    def _is_host(self, user, obj):
        return user.is_staff

    def _is_player(self, user, obj):
        return obj.user == user

    def auto_generate(self, realm):
        realm.generate()

    def force_generate(self, realm):
        realm.generate()

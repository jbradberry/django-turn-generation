from . import models


class TurnGeneration(object):
    slug_field = 'slug'

    slug_kwarg = 'agent_slug'
    pk_kwarg = 'agent_pk'

    def _has_permission(self, user, agent):
        return agent.user == user

    def has_pause_permission(self, user, agent):
        return self._has_permission(user, agent)

    def has_unpause_permission(self, user, agent):
        return self._has_permission(user, agent)

    def has_ready_permission(self, user, agent):
        return self._has_permission(user, agent)

    def has_unready_permission(self, user, agent):
        return self._has_permission(user, agent)

    def get_agent(self, realm, kw):
        filters = {}
        if self.slug_kwarg in kw:
            filters[self.slug_field] = kw[self.slug_kwarg]
        if self.pk_kwarg in kw:
            filters['pk'] = kw[self.pk_kwarg]

        qs = realm.agents.filter(**filters)
        if qs:
            return qs[0]

    def auto_generate(self, realm):
        realm.generate()

    def force_generate(self, realm):
        realm.generate()

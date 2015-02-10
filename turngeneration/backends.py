from . import plugins


class TurnGenerationBackend(object):
    def authenticate(self, **credentials):
        """
        Always return ``None`` to prevent authentication within this backend.
        """
        return None

    def has_perm(self, user_obj, perm, obj=None):
        if obj is None:
            return False
        plugin = plugins.get(obj._meta.app_label)
        if plugin is None:
            return False

        return plugin.has_perm(user_obj, perm, obj)
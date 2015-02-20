from . import plugins


class TurnGenerationBackend(object):
    supports_inactive_user = False

    def authenticate(self, **credentials):
        """
        Always return ``None`` to prevent authentication within this backend.
        """
        return None

    def has_perm(self, user_obj, perm, obj=None):
        if obj is None:
            return False
        plugin = plugins.get_plugin_for_model(obj)
        if plugin is None:
            return False

        return plugin.has_perm(user_obj, perm, obj)

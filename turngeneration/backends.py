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
        plugin = plugins.get_plugin_for_model(obj)
        if plugin is None:
            return False

        methodname = plugin.permissions.get(perm)
        if methodname is None:
            return False
        return getattr(plugin, methodname, None)(user_obj, obj)

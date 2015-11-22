from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from pkg_resources import iter_entry_points


OVERRIDES = getattr(settings, 'TURNGENERATION_OVERRIDES', {})

_realm_types = {}
_agent_types = {}
_plugins = {}


def _populate_realms():
    if not _realm_types:
        for ep in iter_entry_points('turngeneration.plugins'):
            plugin = ep.load()
            plugin_realm_types = dict(getattr(plugin, 'realm_types', {}))
            plugin_realm_types.update(
                OVERRIDES.get(ep.name, {}).get('realm_types', {})
            )

            _realm_types.update(
                (alias, ContentType.objects.get_by_natural_key(*ct.split('.')))
                for alias, ct in plugin_realm_types.iteritems()
                if ct
            )

            _plugins.update(
                (ct, plugin)
                for alias, ct in plugin_realm_types.iteritems()
                if ct
            )


def _populate_agents():
    if not _agent_types:
        for ep in iter_entry_points('turngeneration.plugins'):
            plugin = ep.load()
            plugin_agent_types = dict(getattr(plugin, 'agent_types', {}))
            plugin_agent_types.update(
                OVERRIDES.get(ep.name, {}).get('agent_types', {})
            )

            _agent_types.update(
                (alias, ContentType.objects.get_by_natural_key(*ct.split('.')))
                for alias, ct in plugin_agent_types.iteritems()
                if ct
            )

            _plugins.update(
                (ct, plugin)
                for alias, ct in plugin_agent_types.iteritems()
                if ct
            )


def realm_type(alias):
    return _realm_types.get(alias)


def agent_type(alias):
    return _agent_types.get(alias)


def get_plugin(name):
    plugin = _plugins.get(name)
    return None if plugin is None else plugin()


def get_plugin_for_model(obj):
    ct = '{0}.{1}'.format(obj._meta.app_label, obj._meta.model_name)
    return get_plugin(ct)


_populate_realms()
_populate_agents()

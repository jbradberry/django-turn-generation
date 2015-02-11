from pkg_resources import iter_entry_points
from django.conf import settings


OVERRIDES = getattr(settings, 'TURNGENERATION_OVERRIDES', {})

_realm_aliases = {}
_agent_aliases = {}

_realm_plugins = {}
_agent_plugins = {}


def realm_alias(name):
    if not _realm_aliases:
        for ep in iter_entry_points('turngeneration.plugins'):
            plugin = ep.load()
            plugin_realm_types = dict(getattr(plugin, 'realm_types', {}))
            plugin_realm_types.update(OVERRIDES.get(plugin.name, {}))

        _realm_aliases.update(plugin_realm_types)

    return _realm_aliases.get(name)


def realm_plugin(name):
    if not _realm_plugins:
        for ep in iter_entry_points('turngeneration.plugins'):
            plugin = ep.load()
            plugin_realm_types = dict(getattr(plugin, 'realm_types', {}))
            plugin_realm_types.update(
                OVERRIDES.get(plugin.name, {}).get('realm_types', {})
            )

        _realm_plugins.update(
            (alias, plugin)
            for alias, ct in plugin_realm_types.iteritems()
            if ct
        )

    plugin = _realm_plugins.get(name)
    return None if plugin is None else plugin()


def agent_alias(name):
    if not _agent_aliases:
        for ep in iter_entry_points('turngeneration.plugins'):
            plugin = ep.load()
            plugin_agent_types = dict(getattr(plugin, 'agent_types', {}))
            plugin_agent_types.update(OVERRIDES.get(plugin.name, {}))

        _agent_aliases.update(plugin_agent_types)

    return _agent_aliases.get(name)


def agent_plugin(name):
    if not _agent_plugins:
        for ep in iter_entry_points('turngeneration.plugins'):
            plugin = ep.load()
            plugin_agent_types = dict(getattr(plugin, 'agent_types', {}))
            plugin_agent_types.update(
                OVERRIDES.get(plugin.name, {}).get('agent_types', {})
            )

        _agent_plugins.update(
            (alias, plugin)
            for alias, ct in plugin_agent_types.iteritems()
            if ct
        )

    plugin = _agent_plugins.get(name)
    return None if plugin is None else plugin()

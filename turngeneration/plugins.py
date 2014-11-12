from pkg_resources import iter_entry_points


all_plugins = dict((ep.name, ep.load()) for ep in
                   iter_entry_points('turngeneration.plugins'))

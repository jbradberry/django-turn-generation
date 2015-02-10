from pkg_resources import iter_entry_points


entry_points = dict((ep.name, ep.load()) for ep in
                     iter_entry_points('turngeneration.plugins'))


def get(app_label):
    if app_label not in entry_points:
        return None
    return entry_points[app_label]()

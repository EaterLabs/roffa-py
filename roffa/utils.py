from docker.models.networks import Network
from docker.models.volumes import Volume


def index_by_label(objs: list, label: str, default=False) -> dict:
    if objs is None:
        return {}

    idx = {}

    for obj in objs:
        if default is False and label not in obj.labels:
            continue

        if isinstance(obj, Network) or isinstance(obj, Volume):
            labels = obj.attrs['Labels']
        else:
            labels = obj.labels

        val = labels.get(label, default)

        if val not in idx:
            idx[val] = []

        idx[val].append(obj)

    return idx


def get_handle(obj):
    from .state import Network, District, Container, Volume

    if isinstance(obj, Network):
        return get_network_handle(obj.name)

    if isinstance(obj, District):
        return get_district_handle(obj.name)

    if isinstance(obj, Container):
        return 'container [{}]'.format(obj.name)

    if isinstance(obj, Volume):
        return 'volume [{}]'.format(obj.name)

    return 'an undefined entity'


def get_district_context(from_district, curr_district):
    if from_district != curr_district:
        return ' (originating from {})'.format(get_district_handle(from_district))

    return ''


def get_network_handle(name):
    if name == '__network__':
        return 'default network'

    return 'network [{}]'.format(name)


def get_district_handle(name):
    if name == '__world__':
        return 'world'

    return 'district [{}]'.format(name)

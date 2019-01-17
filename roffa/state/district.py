from __future__ import annotations

from ..utils import index_by_label
from ..errors import RoffaConfigError


class DistrictReference:
    def __init__(self, district, name):
        self.district = district
        self.name = name

    def get_id(self):
        return '{}.{}'.format(self.district, self.name)


class DistrictNetwork(DistrictReference):
    pass


class DistrictVolume(DistrictReference):
    pass


class District:
    name = None
    networks = None
    containers = None
    volumes = None

    def __repr__(self):
        return '<District "{}" containers={}, networks={}, volumes={}>'.format(
            self.name,
            self.containers,
            self.networks,
            self.volumes
        )

    def __init__(self):
        self.networks = {}
        self.containers = {}
        self.volumes = {}

    @staticmethod
    def diff(config: District, docker: DockerDistrict, docker_api):
        from . import Container, Network
        actions = []

        if config is None:
            config = District()

        if docker is None:
            docker = DockerDistrict()

        for container in config.containers.keys() | docker.container_index.keys():
            container_config = config.containers.get(container)
            current_containers = docker.container_index.get(container, []).copy()

            for docker_cont in current_containers:
                docker_cont.amount = container_config.amount

            crawl_len = max(container_config.amount, len(current_containers))

            for i in range(0, crawl_len):
                actions += Container.diff(
                    container_config if i < container_config.amount else None,
                    current_containers[i] if i < len(current_containers) else None,
                    docker_api,
                    i + 1,
                )

        for network in config.networks.keys() | docker.networks.keys():
            network_config = config.networks.get(network)
            docker_network = docker.networks.get(network)
            actions += Network.diff(network_config, docker_network, docker_api)

        return actions

    @staticmethod
    def from_docker(name: str, containers=None, volumes=None, networks=None):
        from . import DockerContainer, Volume, Network
        dist = DockerDistrict()
        dist.name = name

        if containers is None:
            containers = []

        if volumes is None:
            volumes = []

        if networks is None:
            networks = []

        container_idx = index_by_label(containers, 'me.eater.roffa.name')

        network_idx = dict([(network.attrs['Labels']['me.eater.roffa.name'], network) for network in networks if
                            'me.eater.roffa.name' in network.attrs['Labels']])
        volume_idx = dict([(volume.attrs['Labels']['me.eater.roffa.name'], volume) for volume in volumes if
                           'me.eater.roffa.name' in volume.attrs['Labels']])

        for container_name, containers in container_idx.items():
            dist.container_index[container_name] = [DockerContainer.from_docker(name, container_name, container) for
                                                    container
                                                    in containers]

        for network_name, network in network_idx.items():
            dist.networks[network_name] = Network.from_docker(name, network_name, network)

        for volume_name, volume in volume_idx.items():
            dist.volumes[volume_name] = Volume.from_docker(name, volume_name, volume)

        return dist

    @staticmethod
    def from_config(name: str, config: dict):
        from . import Container, Volume, Network
        dist = District()
        dist.name = name
        path = 'districts["{}"]'.format(name) if name != '__world__' else 'world'

        if 'containers' in config:
            containers = config['containers']
            if not isinstance(containers, dict):
                raise RoffaConfigError.wrong_type("{}.containers".format(path), 'map', containers)

            for (container_name, container) in containers.items():
                if not isinstance(container, dict):
                    raise RoffaConfigError.wrong_type(
                        '{}.containers["{}"]'.format(path, container_name),
                        'map',
                        container
                    )

                dist.containers[container_name] = Container.from_config(name, container_name, container)

        if 'volumes' in config:
            volumes = config['volumes']

            if not isinstance(volumes, dict):
                raise RoffaConfigError.wrong_type("{}.volumes".format(path), 'map', volumes)

            for (volume_name, volume) in volumes.items():
                if not isinstance(volume, dict) and volume is not None:
                    raise RoffaConfigError.wrong_type(
                        '{}.volumes["{}"]'.format(path, volume_name),
                        'map or null',
                        volume
                    )

                dist.containers[volume_name] = Volume.from_config(name, volume_name, volume)

        if name != '__world__':
            dist.networks['__network__'] = Network.from_config(name, '__network__', {})

        if 'networks' in config:
            networks = config['networks']

            if not isinstance(networks, dict):
                raise RoffaConfigError.wrong_type("{}.networks".format(path), 'map', networks)

            for (network_name, network) in networks.items():
                if not isinstance(network, dict) and network is not None:
                    raise RoffaConfigError.wrong_type(
                        '{}.networks["{}"]'.format(path, network_name),
                        'map or null',
                        network
                    )

                dist.networks[network_name] = Network.from_config(name, network_name, network)

        return dist


class DockerDistrict(District):
    container_index = None

    def __init__(self):
        super(DockerDistrict, self).__init__()
        self.networks = {}
        self.container_index = {}

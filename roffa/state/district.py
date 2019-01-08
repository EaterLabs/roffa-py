from ..errors import RoffaConfigError


class DistrictReference:
    name = None

    def __init__(self, name):
        self.name = name


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

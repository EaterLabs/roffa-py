from __future__ import annotations

from datetime import datetime

from ..action import RemoveContainer, StartContainer, ConnectNetwork, DisconnectNetwork

from ..errors import RoffaConfigError


class Container:
    amount = 1
    name = None
    image = None
    networks = None
    volumes = None
    district = None

    def __repr__(self):
        return '<Container "{}" amount={}, image={}, networks={}, volumes={}, district={}>'.format(
            self.name,
            self.amount,
            self.image,
            self.networks,
            self.volumes,
            self.district,
        )

    def __init__(self):
        self.networks = []
        self.volumes = []

    def get_name(self):
        return '{}.{}'.format(self.district, self.name)

    def get_config(self) -> dict:
        return {
            "detach": True,
            "image": self.image,
            "name": "{}-{}".format(self.get_name(), datetime.now().strftime('%Y%m%d%H%M%S%f')),
            "labels": {
                "me.eater.roffa.district": self.district,
                "me.eater.roffa.name": self.name,
                "me.eater.roffa.managed": "yes"
            }
        }

    @staticmethod
    def diff(config: Container, docker: DockerContainer, docker_api, nth: int):
        actions = []

        if config is None:
            actions.append(RemoveContainer(docker.get_id(), docker, nth))
            return actions

        if docker is None:
            actions.append(StartContainer(config, nth))
            return

        networks = docker.container.attrs['NetworkSettings']['Networks']
        needed_networks = set(map(lambda net: net.get_id(), config.networks))

        for network in networks.keys() | needed_networks:
            if network not in networks:
                sel_net = None

                for net in config.networks:
                    if net.get_id() == network:
                        sel_net = net
                        break

                actions.append(ConnectNetwork(docker, sel_net))

            if network not in needed_networks and network not in ['bridge', 'ingress', 'none']:
                net = docker_api.networks.get(network)

                from .district import DistrictNetwork
                actions.append(DisconnectNetwork(docker, DistrictNetwork(net.attrs['Labels']['me.eater.roffa.district'],
                                                                         net.attrs['Labels']['me.eater.roffa.name'])))

        return actions

    @staticmethod
    def create_definitions(district, path, name, item, cls):
        output = {}

        if not isinstance(item, list) and not isinstance(item, dict):
            raise RoffaConfigError.wrong_type(
                '{}.{}'.format(path, name),
                'list or map',
                type(item)
            )

        if isinstance(item, list):
            for i in range(len(item)):
                network = item[i]

                if not isinstance(network, str):
                    raise RoffaConfigError.wrong_type(
                        '{}.{}[{}]'.format(path, name, i),
                        'str',
                        type(network)
                    )

                output[network] = cls(district, network)

        if isinstance(item, dict):
            for (network_name, network) in item.items():
                if network is not None:
                    raise RoffaConfigError.wrong_type(
                        '{}.{}["{}"]'.format(path, name, network_name),
                        'null',
                        type(network)
                    )

                output[network_name] = cls(district, network_name)

    @staticmethod
    def from_config(district: str, name: str, config: dict):
        from .district import DistrictNetwork, DistrictVolume

        path = ('districts["{}"]'.format(
            district) if district != '__world__' else 'world') + '.containers["{}"]'.format(
            name)
        cont = Container()
        cont.name = name
        cont.district = district

        if 'image' not in config:
            raise RoffaConfigError.missing("{}.image".format(path), 'str')

        if not isinstance(config['image'], str):
            raise RoffaConfigError.wrong_type("{}.image".format(path), 'str', config['image'])

        cont.image = config['image']

        if not isinstance(config['amount'], int):
            raise RoffaConfigError.wrong_type("{}.amount".format(path), 'int', config['amount'])

        cont.amount = config['amount']

        if 'networks' in config:
            cont.networks = Container.create_definitions(district, path, 'networks', config['networks'],
                                                         DistrictNetwork)

        cont.networks.append(DistrictNetwork(district, '__network__'))

        if 'volumes' in config:
            cont.networks = Container.create_definitions(district, path, 'volumes', config['volumes'], DistrictVolume)

        return cont


class DockerContainer(Container):
    def __init__(self, container):
        super(DockerContainer, self).__init__()
        self.container = container

    def get_id(self):
        return self.container.id

    @staticmethod
    def from_docker(district: str, name: str, container):
        cont = DockerContainer(container)
        cont.district = district
        cont.name = name

        return cont

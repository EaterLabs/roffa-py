from __future__ import annotations

from ..action import StartNetwork, RemoveNetwork
from typing import Union, Optional


class Network:
    name = None
    district = None

    def get_name(self):
        return '{}.{}'.format(self.district, self.name)

    def get_config(self):
        return {
            "name": self.get_name(),
            "driver": "bridge",
            "labels": {
                "me.eater.roffa.district": self.district,
                "me.eater.roffa.name": self.name,
                "me.eater.roffa.managed": "yes"
            }
        }

    @staticmethod
    def diff(config: Optional[Network], docker: Optional[DockerNetwork], docker_api):
        if docker is None:
            return [StartNetwork(config)]

        if config is None:
            return [RemoveNetwork(docker)]

        return []

    @staticmethod
    def from_config(district: str, name: str, config: Union[dict, None]):
        net = Network()
        net.district = district
        net.name = name
        return net

    @staticmethod
    def from_docker(district: str, name: str, network):
        net = DockerNetwork()
        net.id = network.id
        net.district = district
        net.name = name
        net.network = network
        return net


class DockerNetwork(Network):
    network = None
    id = None

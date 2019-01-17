from __future__ import annotations
import typing
from typing import List

from docker.errors import NotFound

if typing.TYPE_CHECKING:
    from ..state import Container

from .base import BaseAction
from ..utils import get_district_handle, get_handle, get_network_handle, get_district_context


class StartContainer(BaseAction):
    def __init__(self, config: Container, nth):
        super(StartContainer, self).__init__()
        self.config = config
        self.nth = nth

    def log(self):
        return 'Starting {} {}/{} in {}'.format(
            get_handle(self.config),
            self.nth,
            self.config.amount,
            get_district_handle(self.config.district)
        )

    def run(self, roffa):
        roffa.docker.containers.run(**self.config.get_config())

    def id(self):
        return '{}:{}:{}'.format(self._type, self.config.get_name(), self.nth)

    def get_requirements(self) -> List[str]:
        reqs = []

        for network in self.config.networks:
            reqs.append(StartNetwork.get_requirement(network.get_id()))

        for volume in self.config.volumes:
            reqs.append(StartVolume.get_requirement(volume.get_id()))

        return reqs


class RemoveContainer(BaseAction):
    def __init__(self, idx, container, nth):
        super(RemoveContainer, self).__init__()
        self.container_id = idx
        self.nth = nth
        self.container = container

    def log(self):
        return 'Removing {} {}/{} with id {} in {}'.format(
            get_handle(self.container),
            self.nth,
            self.container.amount,
            self.container_id,
            get_district_handle(self.container.district)
        )

    def id(self):
        return "{}:{}:{}".format(self._type, self.container.get_name(), self.nth)

    def run(self, roffa):
        container = roffa.docker.containers.get(self.container_id)

        if not container:
            raise RuntimeWarning("Container {} doesn't exist".format(self.container_id))

        container.remove(force=True)


class StartNetwork(BaseAction):
    def __init__(self, config):
        super(StartNetwork, self).__init__()
        self.config = config

    def log(self):
        return 'Creating {} for {}'.format(get_handle(self.config), get_district_handle(self.config.district))

    def id(self):
        return '{}:{}'.format(self._type, self.config.get_name())

    def run(self, roffa):
        roffa.docker.networks.create(**self.config.get_config())


class RemoveNetwork(BaseAction):
    def __init__(self, docker):
        super(RemoveNetwork, self).__init__()
        self.docker = docker

    def log(self):
        return 'Removing {} in {}'.format(get_handle(self.docker), get_district_handle(self.docker.district))

    def id(self):
        return '{}:{}'.format(self._type, self.docker.get_name())

    def run(self, roffa):
        network = roffa.docker.networks.get(self.docker.id)

        if not network:
            raise RuntimeWarning("network {} doesn't exist".format(self.docker.id))

        network.remove()


class DisconnectNetwork(BaseAction):
    def __init__(self, container, network):
        super(DisconnectNetwork, self).__init__()
        self.container = container
        self.network = network

    def log(self):
        return 'Disconnecting {}{} from {} in {}'.format(
            get_network_handle(self.network.name),
            get_district_context(self.network.district, self.container.district),
            get_handle(self.container),
            get_district_handle(self.container.district)
        )

    def id(self):
        return '{}:{}:{}'.format(self._type, self.network.get_id(), self.container.get_id())

    def run(self, roffa):
        try:
            network = roffa.docker.networks.get(self.network.get_id())
        except NotFound:
            network = None

        if not network:
            raise RuntimeWarning("{} doesn't exist".format(get_network_handle(self.network.name)))

        try:
            container = roffa.docker.containers.get(self.container.get_id())
        except NotFound:
            container = None

        if not container:
            raise RuntimeWarning("Container {} doesn't exist".format(self.container.get_id()))

        network.disconnect(container)


class ConnectNetwork(BaseAction):
    def __init__(self, container, network):
        super(ConnectNetwork, self).__init__()
        self.container = container
        self.network = network

    def log(self):
        return 'Connecting {}{} to {} in {}'.format(
            get_network_handle(self.network.name),
            get_district_context(self.network.district, self.container.district),
            get_handle(self.container),
            get_district_handle(self.container.district)
        )

    def id(self):
        return '{}:{}:{}'.format(self._type, self.network.get_id(), self.container.get_id())

    def run(self, roffa):

        try:
            network = roffa.docker.networks.get(self.network.get_id())
        except NotFound:
            network = None

        if not network:
            raise RuntimeWarning("{} doesn't exist".format(get_network_handle(self.network.name)))

        try:
            container = roffa.docker.containers.get(self.container.get_id())
        except NotFound:
            container = None

        if not container:
            raise RuntimeWarning("Container {} doesn't exist".format(self.container.get_id()))

        network.connect(container)


class StartVolume(BaseAction):
    def run(self, roffa):
        roffa.docker.volumes.create(dict(self))


class RemoveVolume(BaseAction):
    def run(self, roffa):
        volume = roffa.docker.volumes.get(self['id'])

        if not volume:
            raise RuntimeWarning("Volume {} doesn't exist".format(self['id']))

        volume.remove()

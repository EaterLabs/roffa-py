from __future__ import annotations
from typing import List, Iterator

from docker import from_env, DockerClient

from .action import BaseAction
from .utils import index_by_label
from .state import District, DockerDistrict
from .errors import RoffaConfigError


class ActionList:
    def __init__(self, list: List[str] = None):
        self.list = [] if list is None else list

    def append(self, action: str):
        if action in self.list:
            return

        self.list.append(action)

    def extend(self, actions: ActionList):
        for action in actions.list:
            self.append(action)


class ActionChain:
    def __init__(self):
        self.actions = {}

    def append(self, actions: List[BaseAction]):
        self.actions.update(dict([(action.id(), action) for action in actions]))

    def get_required(self, action: BaseAction, path=None) -> ActionList:
        actions = ActionList()
        requires = action.get_requirements()

        if path is None:
            path = []

        path = path.copy()
        path.append(action.id())

        for req in requires:
            if req in path:
                raise RuntimeError(
                    "Found circular requirement in {}, asking for {}, path: {}".format(action.id(), req,
                                                                                       ', '.join(path))
                )

            if req not in self.actions:
                continue

            actions.extend(self.get_required(self.actions[req]))

        actions.append(action.id())

        return actions

    def get_sorted(self) -> Iterator[BaseAction]:
        chain = ActionList()

        for action in self.actions.values():
            chain.extend(self.get_required(action))

        return map(lambda act: self.actions[act], chain.list)


class Roffa:
    config = None
    docker = None
    current_state = None
    actions = None

    def __init__(self, docker: DockerClient = None):
        if docker is None:
            docker = from_env()

        self.docker = docker
        self.actions = ActionChain()

    def load_config(self, config: dict):
        self.config = RoffaConfig.from_config(config)

    def collect_state(self):
        self.current_state = RoffaConfig.from_docker(self.docker)

    def collect_actions(self):
        action_list = ActionChain()
        action_list.append(RoffaConfig.diff(self.config, self.current_state, self.docker))
        self.actions = action_list

    def run_actions(self):
        actions = self.actions.get_sorted()

        for action in actions:
            item = action.log()

            if item is not None:
                print(item)

            action.run(self)


class RoffaConfig:
    districts = None
    world = None

    def __repr__(self):
        return '<RoffaConfig districts={} world={}>'.format(
            self.districts,
            self.world
        )

    def __init__(self):
        self.districts = {}
        self.world = District.from_config('__world__', {})

    def get_districts(self) -> dict:
        dists = self.districts.copy()
        dists['__world__'] = self.world
        return dists

    @staticmethod
    def diff(config: RoffaConfig, docker_config: RoffaConfig, docker_api):
        if config is None or docker_config is None:
            raise RuntimeError("config and docker config can't be null")

        actions = []

        config_districts = config.get_districts()
        docker_districts = docker_config.get_districts()

        for district in config_districts.keys() | docker_districts.keys():
            actions += District.diff(config_districts.get(district), docker_districts.get(district), docker_api)

        return actions

    @staticmethod
    def from_config(config: dict):
        instance = RoffaConfig()

        if 'districts' in config:
            if not isinstance(config['districts'], dict):
                raise RoffaConfigError.wrong_type('districts', 'map', config['districts'])

            for (name, district) in config['districts'].items():
                if not isinstance(district, dict):
                    raise RoffaConfigError.wrong_type('districts["{}"]'.format(name), 'map', district)

                instance.districts[name] = District.from_config(name, district)

        if 'world' in config:
            if not isinstance(config['world'], dict):
                raise RoffaConfigError.wrong_type('world', 'map', config['world'])

            instance.world = District.from_config('__world__', config['world'])

        return instance

    @staticmethod
    def from_docker(docker_client: DockerClient):
        _filter = {
            'label': ['me.eater.roffa.managed=yes']
        }

        containers = index_by_label(
            docker_client.containers.list(all=True, filters=_filter),
            'me.eater.roffa.district',
            '__world__'
        )

        networks = index_by_label(
            docker_client.networks.list(filters=_filter),
            'me.eater.roffa.district',
            '__world__'
        )

        volumes = index_by_label(
            docker_client.volumes.list(filters=_filter),
            'me.eater.roffa.district',
            '__world__'
        )

        instance = RoffaDockerConfig()

        for district_name in set(volumes.keys() | networks.keys() | containers.keys()):
            district = District.from_docker(district_name,
                                            containers=containers.get(district_name, []),
                                            volumes=volumes.get(district_name, []),
                                            networks=networks.get(district_name, []))

            if district_name == '__world__':
                instance.world = district
            else:
                instance.districts[district_name] = district

        return instance


class RoffaDockerConfig(RoffaConfig):
    def __init__(self):
        super().__init__()
        self.world = DockerDistrict.from_docker('__world__')

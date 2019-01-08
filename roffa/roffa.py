from .state import District
from .errors import RoffaConfigError


class Roffa:
    config = None

    def load_config(self, config: dict):
        self.config = RoffaConfig.from_config(config)


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

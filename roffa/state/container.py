from ..errors import RoffaConfigError


class Container:
    id = None
    amount = 1
    name = None
    image = None
    networks = None
    volumes = None

    def __repr__(self):
        return '<Container "{}" id={}, amount={}, image={}, networks={}, volumes={}>'.format(
            self.name,
            self.id,
            self.amount,
            self.image,
            self.networks,
            self.volumes
        )

    def __init__(self):
        self.networks = []
        self.volumes = []

    @staticmethod
    def create_definitions(path, name, item, cls):
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

                output[network] = cls(network)

        if isinstance(item, dict):
            for (network_name, network) in item.items():
                if network is not None:
                    raise RoffaConfigError.wrong_type(
                        '{}.{}["{}"]'.format(path, name, network_name),
                        'null',
                        type(network)
                    )

                output[network_name] = cls(network_name)

    @staticmethod
    def from_config(district: str, name: str, config: dict):
        from .district import DistrictNetwork, DistrictVolume

        path = ('districts["{}"]'.format(district) if district != '__world__' else 'world') + '.containers["{}"]'.format(
            name)
        cont = Container()
        cont.name = name

        if 'image' not in config:
            raise RoffaConfigError.missing("{}.image".format(path), 'str')

        if not isinstance(config['image'], str):
            raise RoffaConfigError.wrong_type("{}.image".format(path), 'str', config['image'])

        cont.image = config['image']

        if 'networks' in config:
            cont.networks = Container.create_definitions(path, 'networks', config['networks'], DistrictNetwork)

        if 'volumes' in config:
            cont.networks = Container.create_definitions(path, 'volumes', config['volumes'], DistrictVolume)

        return cont

from typing import Union


class Volume:
    id = None
    name = None

    @staticmethod
    def from_config(district: str, name: str, config: Union[dict, None]):
        net = Volume()
        net.name = name
        return net

    @staticmethod
    def from_docker(district: str, name: str, volume):
        net = Volume()
        net.id = volume.id
        net.name = name
        return net

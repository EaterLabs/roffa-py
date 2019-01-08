from typing import Union


class Network:
    id = None
    name = None

    @staticmethod
    def from_config(district: str, name: str, config: Union[dict, None]):
        net = Network()
        net.name = name
        return net

from typing import Union


class Volume:
    id = None
    name = None

    @staticmethod
    def from_config(district: str, name: str, config: Union[dict, None]):
        net = Volume()
        net.name = name
        return net

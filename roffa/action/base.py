from typing import List, Union
import re

SELECT_FIRST_AND_CAPITALS = re.compile(r'((?!^)[A-Z])')


def create_id(cls):
    return re.sub(
        SELECT_FIRST_AND_CAPITALS,
        r'_\1',
        type(cls).__name__
    ).lower()


class BaseAction:
    _type = None

    @classmethod
    def get_requirement(cls, id: str):
        return '{}:{}'.format(cls.get_id(), id)

    @classmethod
    def get_id(cls):
        return create_id(cls)

    def __init__(self, *args, **kwargs):
        if self._type is None:
            self._type = create_id(self)

    def log(self) -> Union[None, str]:
        return None

    def run(self, roffa):
        pass

    def get_requirements(self) -> List[str]:
        return []

    def id(self) -> str:
        return self._type

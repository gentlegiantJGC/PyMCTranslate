from typing import Dict


class BaseNumericalRegistry:
    def __init__(self):
        self._to_str: Dict[int, str] = {}
        self._to_int: Dict[str, int] = {}

    def register(self, key: str, value: int):
        assert isinstance(key, str) and isinstance(
            value, int
        ), "key must be a string and value must be an int"
        self._to_str[value] = key
        self._to_int[key] = value

    def __contains__(self, item):
        if isinstance(item, int):
            return item in self._to_str
        elif isinstance(item, str):
            return item in self._to_int
        return False


class NumericalRegistry(BaseNumericalRegistry):
    def __init__(self):
        super(NumericalRegistry, self).__init__()

    def private_to_str(self, value: int, default=None):
        """PRIVATE: Use the method in the Version class"""
        return self._to_str.get(value, default)

    def private_to_int(self, key: str, default=None):
        """PRIVATE: Use the method in the Version class"""
        return self._to_int.get(key, default)

from typing import Union, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from .translation_manager import TranslationManager
import json
import numpy

from PyMCTranslate.py3.registry import NumericalRegistry

"""
Biome translation pipeline
    version int
        _biome_int_to_str
    version string
        _biome_to_universal (_translation_manager.biomes first)
    universal string
        self._translation_manager.biomes.universal
    universal int
"""


class BiomeVersionManager:
    def __init__(self, config: str, translation_manager: 'TranslationManager'):
        self._translation_manager = translation_manager
        with open(config) as f:
            biome_data = json.load(f)

        # convert the biome information between int id and string id (the ones registered in TranslationManager.biomes will take precedent)
        self._biome_str_to_int = biome_data['int_map']
        self._biome_int_to_str = {d: b for b, d in biome_data['int_map'].items()}
        # convert the string id to a universal string id
        self._biome_to_universal: Dict[str, str] = biome_data['version2universal']
        self._biome_from_universal: Dict[str, str] = biome_data['universal2version']

    def to_universal(self, biome: Union[int, str]) -> int:
        if not isinstance(biome, int) and numpy.issubdtype(biome, numpy.integer):
            biome = int(biome)
        if isinstance(biome, int):
            if biome in self._translation_manager.biomes:
                biome = self._translation_manager.biomes.private_to_str(biome)
            elif biome in self._biome_int_to_str:
                biome = self._biome_int_to_str[biome]
            else:
                print(f'Could not find registered value for biome {biome}. Reverting to plains')
                biome = self.to_universal('minecraft:plains')

        # biome should now be a string
        if biome in self._biome_to_universal:
            universal_biome = self._biome_to_universal[biome]
        else:
            universal_biome = biome

        if universal_biome not in self._translation_manager.biomes.universal:
            self._translation_manager.biomes.universal.register(universal_biome)
        return self._translation_manager.biomes.universal.to_int(universal_biome)

    def from_universal(self, biome: Union[int, str]) -> int:
        if not isinstance(biome, int) and numpy.issubdtype(biome, numpy.integer):
            biome = int(biome)
        if isinstance(biome, int):
            if biome in self._translation_manager.biomes.universal:
                biome = self._translation_manager.biomes.universal.to_str(biome)
            else:
                raise Exception(f'Unregistered universal biome id {biome} found')

        # biome is now the universal string

        if biome in self._biome_from_universal:
            version_biome = self._biome_from_universal[biome]
        else:
            version_biome = biome

        if biome in self._translation_manager.biomes:
            biome = self._translation_manager.biomes.private_to_int(biome)
        elif biome in self._biome_str_to_int:
            biome = self._biome_str_to_int[biome]
        else:
            print(f'Error processing biome {biome}. Setting to plains.')
            biome = self.from_universal('minecraft:plains')  # TODO: perhaps find a way to assign default dynamically

        return biome


class BiomeWorldManager(NumericalRegistry):
    def __init__(self):
        NumericalRegistry.__init__(self)
        self.universal = UniversalBiomeRegistry()


class UniversalBiomeRegistry:
    def __init__(self):
        self._to_str: Dict[int, str] = {}
        self._to_int: Dict[str, int] = {}
        self._item_count = 0

    def register(self, key: str, value: int = None):
        if value is None:
            while self._item_count in self._to_str:
                self._item_count += 1
            value = self._item_count
        assert isinstance(key, str) and isinstance(value, int), 'key must be a string and value must be an int'
        self._to_str[value] = key
        self._to_int[key] = value

    def to_str(self, value: int, default=None):
        return self._to_str.get(value, default)

    def to_int(self, key: str, default=None):
        return self._to_int.get(key, default)

    def __contains__(self, item):
        if isinstance(item, int):
            return item in self._to_str
        elif isinstance(item, str):
            return item in self._to_int
        return False

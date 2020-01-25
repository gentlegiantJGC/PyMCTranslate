from typing import Union, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from PyMCTranslate.py3.translation_manager import TranslationManager
import numpy

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
    def __init__(self, biome_data: dict, translation_manager: 'TranslationManager'):
        self._translation_manager = translation_manager

        # convert the biome information between int id and string id (the ones registered in TranslationManager.biomes will take precedent)
        self._biome_str_to_int = biome_data['int_map']
        self._biome_int_to_str = {d: b for b, d in biome_data['int_map'].items()}
        # convert the string id to a universal string id
        self._biome_to_universal: Dict[str, str] = biome_data['version2universal']
        self._biome_from_universal: Dict[str, str] = biome_data['universal2version']

    def to_universal(self, biome: Union[int, str]) -> int:
        if not isinstance(biome, int) and numpy.issubdtype(biome.__class__, numpy.integer):
            biome = int(biome)
        if isinstance(biome, int):
            if biome in self._translation_manager.biome_registry:
                biome = self._translation_manager.biome_registry.private_to_str(biome)
            elif biome in self._biome_int_to_str:
                biome = self._biome_int_to_str[biome]
            else:
                print(f'Could not find registered value for biome {biome}. Reverting to plains')
                biome = 'minecraft:plains'

        # biome should now be a string
        if biome in self._biome_to_universal:
            universal_biome = self._biome_to_universal[biome]
        else:
            universal_biome = biome

        if universal_biome not in self._translation_manager.universal_biome_registry:
            self._translation_manager.universal_biome_registry.register(universal_biome)
        return self._translation_manager.universal_biome_registry.to_int(universal_biome)

    def from_universal(self, biome: Union[int, str]) -> int:
        if not isinstance(biome, int) and numpy.issubdtype(biome.__class__, numpy.integer):
            biome = int(biome)
        if isinstance(biome, int):
            if biome in self._translation_manager.universal_biome_registry:
                biome = self._translation_manager.universal_biome_registry.to_str(biome)
            else:
                biome = 'universal_minecraft:plains'

        # biome is now the universal string

        if biome in self._biome_from_universal:
            version_biome = self._biome_from_universal[biome]
        else:
            version_biome = biome

        if version_biome in self._translation_manager.biome_registry:
            version_biome = self._translation_manager.biome_registry.private_to_int(version_biome)
        elif version_biome in self._biome_str_to_int:
            version_biome = self._biome_str_to_int[version_biome]
        else:
            print(f'Error processing biome {version_biome}. Setting to plains.')
            version_biome = self.from_universal('minecraft:plains')  # TODO: perhaps find a way to assign default dynamically

        return version_biome

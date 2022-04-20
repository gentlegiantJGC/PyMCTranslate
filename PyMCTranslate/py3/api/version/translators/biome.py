from typing import Union, Dict, TYPE_CHECKING, List
import numpy
import logging

if TYPE_CHECKING:
    from PyMCTranslate.py3.api.translation_manager import TranslationManager

log = logging.getLogger(__name__)

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


class BiomeTranslator:
    def __init__(self, biome_data: dict, translation_manager: "TranslationManager"):
        self._translation_manager = translation_manager

        # convert the biome information between int id and string id (the ones registered in TranslationManager.biomes will take precedent)
        self._biome_str_to_int: Dict[str, int] = biome_data["int_map"]
        self._biome_int_to_str: Dict[int, str] = {
            d: b for b, d in biome_data["int_map"].items()
        }
        # convert the string id to a universal string id
        self._biome_to_universal: Dict[str, str] = biome_data["version2universal"]
        self._biome_from_universal: Dict[str, str] = biome_data["universal2version"]

        self._error_biomes = set()

    def unpack(self, biome: int) -> str:
        """Unpack the raw numerical biome value into the namespaced string format.
        This will first use any pre-registered mappings bound using TranslationManager.biome_registry.register
        If it can't be found there it will fall back to the vanilla ones.
        If it still can't be found it will fall back to plains"""
        if isinstance(biome, numpy.integer):
            biome = int(biome)
        if biome in self._translation_manager.biome_registry:
            biome_str = self._translation_manager.biome_registry.private_to_str(biome)
        elif biome in self._biome_int_to_str:
            biome_str = self._biome_int_to_str[biome]
        else:
            if biome not in self._error_biomes:
                log.warning(
                    f"Could not find registered value for biome {biome}. Reverting to plains"
                )
                self._error_biomes.add(biome)
            biome_str = "minecraft:plains"
        return biome_str

    def pack(self, biome: str) -> int:
        """Pack the namespaced string biome value into the raw numerical format
        This will first use any pre-registered mappings bound using TranslationManager.biome_registry.register
        If it can't be found there it will fall back to the vanilla ones.
        If it still can't be found it will fall back to plains"""
        if biome in self._translation_manager.biome_registry:
            biome_int = self._translation_manager.biome_registry.private_to_int(biome)
        elif biome in self._biome_str_to_int:
            biome_int = self._biome_str_to_int[biome]
        else:
            log.warning(f"Error processing biome {biome}. Setting to plains.")
            biome_int = self.pack(
                "minecraft:plains"
            )  # TODO: perhaps find a way to assign default dynamically
        return biome_int

    def to_universal(self, biome: str) -> str:
        """Convert the version namespaced string to the universal namespaced string"""
        if biome in self._biome_to_universal:
            biome = self._biome_to_universal[biome]
        return biome

    def from_universal(self, biome: str) -> str:
        """Convert the universal namespaced string to the version namespaced string"""
        if biome in self._biome_from_universal:
            biome = self._biome_from_universal[biome]
        return biome

    @property
    def biome_ids(self) -> List[str]:
        biomes = set(self._biome_str_to_int.keys())
        biomes.update(dict(self._translation_manager.biome_registry).values())
        return list(biomes)

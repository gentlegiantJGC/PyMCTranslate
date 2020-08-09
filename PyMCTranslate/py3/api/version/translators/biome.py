from typing import Union, Dict, TYPE_CHECKING
import numpy

from PyMCTranslate.py3.log import log

if TYPE_CHECKING:
    from PyMCTranslate.py3.api.translation_manager import TranslationManager

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
        self._biome_int_to_str: Dict[int, str] = {d: b for b, d in biome_data["int_map"].items()}
        # convert the string id to a universal string id
        self._biome_to_universal: Dict[str, str] = biome_data["version2universal"]
        self._biome_from_universal: Dict[str, str] = biome_data["universal2version"]

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
            log.warning(
                f"Could not find registered value for biome {biome}. Reverting to plains"
            )
            biome_str = "minecraft:plains"
        return biome_str

    def pack(self, biome: str) -> int:
        """Pack the namespaced string biome value into the raw numerical format
        This will first use any pre-registered mappings bound using TranslationManager.biome_registry.register
        If it can't be found there it will fall back to the vanilla ones.
        If it still can't be found it will fall back to plains"""
        if biome in self._translation_manager.biome_registry:
            biome_int = self._translation_manager.biome_registry.private_to_int(
                biome
            )
        elif biome in self._biome_str_to_int:
            biome_int = self._biome_str_to_int[biome]
        else:
            log.warning(f"Error processing biome {biome}. Setting to plains.")
            biome_int = self.pack(
                "minecraft:plains"
            )  # TODO: perhaps find a way to assign default dynamically
        return biome_int

    def to_universal2(self, biome: str) -> str:
        if biome in self._biome_to_universal:
            biome = self._biome_to_universal[biome]
        return biome

    def from_universal2(self, biome: str) -> str:
        if biome in self._biome_from_universal:
            biome = self._biome_from_universal[biome]
        return biome

    def to_universal(self, biome: Union[int, str]) -> int:
        if isinstance(biome, (int, numpy.integer)):
            biome_str = self.unpack(biome)

        # biome should now be a string
        universal_biome = self.to_universal2(biome_str)

        if universal_biome not in self._translation_manager.universal_biome_registry:
            self._translation_manager.universal_biome_registry.register(universal_biome)
        return self._translation_manager.universal_biome_registry.to_int(
            universal_biome
        )

    def from_universal(self, biome: Union[int, str]) -> int:
        if not isinstance(biome, int) and numpy.issubdtype(
            biome.__class__, numpy.integer
        ):
            biome = int(biome)
        if isinstance(biome, int):
            if biome in self._translation_manager.universal_biome_registry:
                biome = self._translation_manager.universal_biome_registry.to_str(biome)
            else:
                biome = "universal_minecraft:plains"

        # biome is now the universal string

        version_biome = self.from_universal2(biome)

        version_biome = self.pack(version_biome)

        return version_biome

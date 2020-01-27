import os
from typing import Union, Tuple, List, Dict, TYPE_CHECKING

from .registry import NumericalRegistry, UniversalBiomeRegistry
from PyMCTranslate import minified
from PyMCTranslate.py3.versions import Version
from PyMCTranslate.py3.util import directories

if TYPE_CHECKING:
    from PyMCTranslate.py3.versions import Version

"""
Structure:

TranslationManager
    Version : bedrock_1_7_0
    Version : java_1_12_0
    Version : java_1_13_0
    Version : universal
"""


class TranslationManager:
    """
    Container and manager for the different translation versions.
    A version in this context is a version of the game from a specific platform
    (ie a unique combination of platform and version number)
    """

    def __init__(self, json_path: str):
        """
        Call this class with the path to the mapping json files.
        Note if you are a developer using this library you can call PyMCTranslate.new_translation_manager()
        to get a new instance of this class with the default mappings set up for you.

        :param json_path: The path to the json directory
        """
        # Storage for each of the Version classes
        self._versions: Dict[str, Dict[Tuple[int, int, int], 'Version']] = {}
        # if a Version class for a specific version number does not exist the neareast will be found and stored here
        self._version_remap: Dict[
            Tuple[
                str,
                Union[Tuple[int, ...], int]
            ],
            Tuple[int, int, int]
        ] = {}

        self._biome_registry = NumericalRegistry()
        self._universal_biome_registry = UniversalBiomeRegistry()
        self._block_registry = NumericalRegistry()
        self._universal_format = None

        # Create a class for each of the versions and store them
        if minified:
            raise NotImplementedError
        else:
            for version_name in directories(os.path.join(json_path, 'versions')):
                if os.path.isfile(os.path.join(json_path, 'versions', version_name, '__init__.json')):
                    version = Version(os.path.join(json_path, 'versions', version_name), self)
                    self._versions.setdefault(version.platform, {})
                    self._versions[version.platform].setdefault(version.version_number, version)
                    self._version_remap[(version.platform, version.data_version)] = version.version_number
                    if version_name == 'universal':
                        self._universal_format = version

    @property
    def universal_format(self) -> Version:
        return self._universal_format

    @property
    def biome_registry(self) -> NumericalRegistry:
        """Use this to register custom biomes"""
        return self._biome_registry

    @property
    def universal_biome_registry(self) -> UniversalBiomeRegistry:
        """For internal use"""
        return self._universal_biome_registry

    @property
    def block_registry(self) -> NumericalRegistry:
        """Use this to register custom numerical blocks"""
        return self._block_registry

    def platforms(self) -> List[str]:
        """
        Get a list of all the platforms there are Version classes for.
        Currently these are 'java', 'bedrock' and 'universal'
        """
        return list(self._versions.keys())

    def version_numbers(self, platform: str) -> List[Tuple[int, int, int]]:
        """
        Get a list of all the version numbers there are Version classes for, for a given platform.
        :param platform: The platform name (use TranslationManager.platforms to get the valid platforms)
        :return: The a list of version numbers (tuples) for a given platform. Throws an AssertionError if the platform is not present.
        """
        assert platform in self._versions, f'The requested platform "{platform}" is not present'
        return list(self._versions[platform].keys())

    def get_version(self, platform: str, version_number: Union[int, Tuple[int, ...], List[int]]) -> 'Version':
        """
        A method to get a Version class.
        :param platform: The platform name (use TranslationManager.platforms to get the valid platforms)
        :param version_number: The version number or DataVersion (use TranslationManager.version_numbers to get version numbers for a given platforms)
        :return: The Version class for the given inputs. Throws an AssertionError if it does not exist.
        """
        if isinstance(version_number, list):
            version_number = tuple(version_number)
        assert platform in self._versions, f'The requested platform "({platform})" is not present'
        if isinstance(version_number, int) or version_number not in self._versions[platform]:
            version_number = self._get_version_number(platform, version_number)
        return self._versions[platform][version_number]

    def _get_version_number(self, platform: str, version_number: Union[int, Tuple[int, ...]]) -> Tuple[int, int, int]:
        if (platform, version_number) not in self._version_remap:
            if isinstance(version_number, int):
                previous_version = None
                next_version = None
                for version_number_, version in self._versions[platform].items():
                    if version.data_version == version_number:
                        self._version_remap[(platform, version_number)] = version_number_
                        return version_number_
                    elif version.data_version > version_number:
                        if next_version is None:
                            next_version = version.data_version, version_number_
                        elif version.data_version < next_version[0]:
                            next_version = version.data_version, version_number_
                    else:
                        if previous_version is None:
                            previous_version = version.data_version, version_number_
                        elif version.data_version > previous_version[0]:
                            previous_version = version.data_version, version_number_
                if next_version is not None:
                    self._version_remap[(platform, version_number)] = next_version[1]
                elif previous_version is not None:
                    self._version_remap[(platform, version_number)] = previous_version[1]
                else:
                    raise Exception(f'Could not find a version for DataVersion({platform}, {version_number})')

            elif isinstance(version_number, tuple):
                previous_version = None
                next_version = None
                for version_number_ in self._versions[platform].keys():
                    if version_number_ < version_number:
                        if previous_version is None:
                            previous_version = version_number_
                        elif version_number_ > previous_version:
                            previous_version = version_number_
                    elif version_number_ > version_number:
                        if next_version is None:
                            next_version = version_number_
                        elif version_number_ < next_version:
                            next_version = version_number_
                if next_version is not None and next_version[:2] == version_number[:2]:
                    self._version_remap[(platform, version_number)] = next_version
                elif previous_version is not None:
                    self._version_remap[(platform, version_number)] = previous_version
                elif version_number[:2] < (1, 12):  # TODO: this is a temporary workaround until more versions are added
                    self._version_remap[(platform, version_number)] = next_version
                else:
                    raise Exception(f'Could not find a version for Version({platform}, {version_number})')

            else:
                raise Exception(f'version number type {version_number.__class__} is not supported')
        return self._version_remap[(platform, version_number)]

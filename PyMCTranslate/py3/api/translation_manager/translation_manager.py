import os
from typing import Union, Tuple, List, Dict

from .registry import NumericalRegistry
from PyMCTranslate.py3 import log
from PyMCTranslate.py3.meta import minified
from PyMCTranslate.py3.api.version import Version

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
    The TranslationManager is a container for a number of different Version classes.

    Each Version class contains the data for a given game platform and version.

    The TranslationManager exists to be a loader and accessor for the Version classes as well as containing some extra data.

    .. important::
           This class should not be directly initiated. You should instead use ``PyMCTranslate.new_translation_manager()`` to request that a new translation manager be created.

    .. important::
       If you are using this library with Amulet an instance of this class will already exist in ``World.translation_manager``.

       If you are for some reason directly interacting with the amulet_core's ``WorldFormatWrapper`` class it too has a ``translation_manager`` attribute.
    """

    def __init__(self, json_path: str):
        """
        Call this class with the path to the mapping json files.
        .. important::
           This class should not be directly initiated. You should instead use ``PyMCTranslate.new_translation_manager()`` to request that a new translation manager be created.

        :param json_path: The path to the json directory
        """
        # Storage for each of the Version classes
        self._versions: Dict[str, Dict[Tuple[int, int, int], "Version"]] = {}
        # if a Version class for a specific version number does not exist the neareast will be found and stored here
        self._version_remap: Dict[
            Tuple[str, Union[Tuple[int, ...], int]], Tuple[int, int, int]
        ] = {}

        self._biome_registry = NumericalRegistry()
        self._block_registry = NumericalRegistry()
        self._universal_format = None

        # Create a class for each of the versions and store them
        if minified:
            init_file = "meta.json.gz"
        else:
            init_file = "__init__.json"

        versions_path = os.path.join(json_path, "versions")

        for version_name in os.listdir(versions_path):
            if os.path.isfile(os.path.join(versions_path, version_name, init_file)):
                try:
                    version = Version(os.path.join(versions_path, version_name), self)
                except:
                    log.error(
                        f"Failed loading translator for version {version_name}. Try deleting your Amulet directory and extrating the files agian.",
                        exc_info=True,
                    )
                else:
                    self._versions.setdefault(version.platform, {}).setdefault(
                        version.version_number, version
                    )

        for versions in self._versions.values():
            for version in sorted(versions.values(), key=lambda v: v.version_number):
                self._version_remap[
                    (version.platform, version.data_version)
                ] = version.version_number
                if version.platform == "universal":
                    self._universal_format = version

        if len(self._version_remap) < 28:
            raise Exception(
                "Failed to load the translators. Something has probably not been set up correctly."
            )
        if self._universal_format is None:
            raise Exception(
                "Universal format was not found. Something has probably not been set up correctly."
            )

    @property
    def universal_format(self) -> Version:
        """
        A simple way to access the Version class for the Universal format.

        :return: The Version class for the Universal format.
        """
        return self._universal_format

    @property
    def biome_registry(self) -> NumericalRegistry:
        """A class used to register the biome string name that pairs with the arbitrary numerical id stored in chunk."""
        return self._biome_registry

    @property
    def block_registry(self) -> NumericalRegistry:
        """A class used to register the block string name that pairs with the arbitrary numerical id stored in chunk.
        This is only used in worlds where the blocks ids are stored in numerical format."""
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

        :param platform: The platform name (use ``TranslationManager.platforms`` to get the valid platforms)
        :return: The a list of version numbers (tuples) for a given platform.
        :raise: Raises a KeyError if the platform is not present.
        """
        if platform not in self._versions:
            raise KeyError(f'The requested platform "{platform}" is not present')
        return sorted(self._versions[platform].keys())

    def get_version(
        self, platform: str, version_number: Union[int, Tuple[int, ...], List[int]]
    ) -> "Version":
        """
        Get a Version class for the requested platform and version number

        :param platform: The platform name (use ``TranslationManager.platforms`` to get the valid platforms)
        :param version_number: The version number or DataVersion (use ``TranslationManager.version_numbers`` to get version numbers for a given platforms)
        :return: The Version class for the given inputs.
        :raise: Raises a KeyError if it does not exist.
        """
        if isinstance(version_number, list):
            version_number = tuple(version_number)
        if platform not in self._versions:
            raise KeyError(f'The requested platform "{platform}" is not present')
        if (
            isinstance(version_number, int)
            or version_number not in self._versions[platform]
        ):
            version_number = self._get_version_number(platform, version_number)
        return self._versions[platform][version_number]

    def _get_version_number(
        self, platform: str, version_number: Union[int, Tuple[int, ...]]
    ) -> Tuple[int, int, int]:
        if (platform, version_number) not in self._version_remap:
            if isinstance(version_number, int):
                previous_version = None
                next_version = None
                for version_number_, version in self._versions[platform].items():
                    if version.data_version == version_number:
                        self._version_remap[
                            (platform, version_number)
                        ] = version_number_
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
                    self._version_remap[(platform, version_number)] = previous_version[
                        1
                    ]
                else:
                    raise KeyError(
                        f"Could not find a version for DataVersion({platform}, {version_number})"
                    )

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
                elif version_number[:2] < (
                    1,
                    12,
                ):  # TODO: this is a temporary workaround until more versions are added
                    self._version_remap[(platform, version_number)] = next_version
                else:
                    raise KeyError(
                        f"Could not find a version for Version({platform}, {version_number})"
                    )

            else:
                raise KeyError(
                    f"version number type {version_number.__class__} is not supported"
                )
        return self._version_remap[(platform, version_number)]

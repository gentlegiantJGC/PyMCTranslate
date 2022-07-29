import json
import os
from typing import Union, Tuple, TYPE_CHECKING
import glob
import warnings
import logging

from PyMCTranslate.py3.api import Block
from PyMCTranslate.py3.util.json_gz import load_json_gz
from PyMCTranslate.py3.meta import minified, json_atlas
from .translators import (
    BlockTranslator,
    EntityTranslator,
    ItemTranslator,
    BiomeTranslator,
)

if TYPE_CHECKING:
    from PyMCTranslate.py3.api.translation_manager import TranslationManager

log = logging.getLogger(__name__)

_version_data = {}

_translator_classes = {
    "block": BlockTranslator,
    "entity": EntityTranslator,
    "item": ItemTranslator,
}


class Version:
    """
    This class contains all the specification and translation files for the game version that it represents.
    There will be an instance of this class in the ``TranslationManager`` for each unique combination of platform and version number.

    .. important::
           This class should not be directly initiated. You should first create a ``TranslationManager`` class and call ``TranslationManager.get_version`` to get the required Version class.
    """

    def __init__(self, version_path: str, translation_manager: "TranslationManager"):
        self._version_path = version_path
        self._translation_manager = translation_manager
        self._block = None
        self._entity = None
        self._item = None
        self._biome = None

        if version_path not in _version_data:
            _version_data[version_path] = {}
            if minified:
                # load meta.json.gz and store in _version_data[version_path]["meta"]
                _version_data[version_path]["meta"] = {
                    key: json_atlas[value]
                    for key, value in load_json_gz(
                        os.path.join(version_path, "meta.json.gz")
                    ).items()
                }
            else:
                _version_data[version_path]["meta"] = meta = {}
                for file_name in [
                    "__init__",
                    "__waterloggable__",
                    "__always_waterlogged__",
                    "__biome_data__",
                    "__numerical_block_map__",
                ]:
                    if os.path.isfile(os.path.join(version_path, f"{file_name}.json")):
                        with open(os.path.join(version_path, f"{file_name}.json")) as f:
                            meta[file_name] = json.load(f)

        meta = _version_data[version_path]["meta"]
        # unpack the __init__.json file
        init_file = meta["__init__"]
        assert isinstance(
            init_file["platform"], str
        ), f"The platform name defined in {version_path}/__init__.json is not a string"
        self._platform = init_file["platform"]
        assert (
            isinstance(init_file["version"], list) and len(init_file["version"]) == 3
        ), f"The version number defined in {version_path}/__init__.json is incorrectly formatted"
        self._version_number = tuple(init_file["version"])
        self._data_version: int = init_file.get("data_version", 0)
        assert isinstance(init_file["block_format"], str)
        self._block_format = init_file["block_format"]
        self._has_abstract_format = self._block_format in [
            "numerical",
            "pseudo-numerical",
        ]

        self._block_extra_input = [{}, None, None, self._block_format]
        if self.has_abstract_format:
            self._block_extra_input[0] = meta["__numerical_block_map__"]

        if self.platform == "java" and "__waterloggable__" in meta:
            self._block_extra_input[1] = meta["__waterloggable__"]
            self._block_extra_input[2] = meta["__always_waterlogged__"]

        self._biome_callable = lambda: BiomeTranslator(
            meta["__biome_data__"], translation_manager
        )

    def _load_translator(self, attr, *args):
        """
        Internal method to load the data related to this class.
        This allows loading to be deferred until it is needed (if at all)
        """
        if attr not in _translator_classes:
            raise Exception(f"Unknown translator {attr}")
        if getattr(self, f"_{attr}") is None:
            if minified:
                fpath = os.path.join(self._version_path, f"{attr}.json.gz")
                if os.path.isfile(fpath):
                    database = load_json_gz(fpath)
                else:
                    log.critical(f"Could not find {attr} database")
                    database = {}
            else:
                database = {}
                for fpath in glob.iglob(
                    os.path.join(glob.escape(self._version_path), attr, "**", "*.json"),
                    recursive=True,
                ):
                    database_ = database
                    rel_path = os.path.relpath(
                        fpath, os.path.join(self._version_path, attr)
                    ).split(os.sep)
                    assert len(rel_path) == 5
                    for directory in rel_path[:-2]:
                        database_ = database_.setdefault(directory, {})
                    with open(fpath) as f:
                        database_[rel_path[-1][:-5]] = json.load(f)
            setattr(
                self,
                f"_{attr}",
                _translator_classes[attr](
                    self._translation_manager, self, database, *args
                ),
            )

    def __repr__(self):
        return f"PyMCTranslate.Version({self.platform}, {self.version_number})"

    @property
    def block_format(self) -> str:
        """
        The native format of the blocks for this game version.

        This will be one of "numerical", "pseudo-numerical", "blockstate" or "nbt-blockstate".

         "numerical" is the old storage format where both block id and data value were numerical values.

         "pseudo-numerical" is the in-between Bedrock format where block ids were namespaced strings but data was still numerical.

         "blockstate" is the new Java format where the block ids are all namespaced strings and the data is stored as properties in NBT.TAG_String format.

         "nbt-blockstate" is the new Bedrock format where the block ids are all namespaced strings and the data is stored as properties in various NBT types.

        """
        return self._block_format

    @property
    def platform(self) -> str:
        """
        The platform name of the version this class instance holds the data of.
        Currently these are 'java', 'bedrock' and 'universal'
        """
        return self._platform

    @property
    def has_abstract_format(self) -> bool:
        """Property to access if the version has a second custom blockstate format to abstract away the old numerical format.
        If this is true the ``force_blockstate`` input to various methods can be used to switch between the native and abstract format.
        If this is false the native format will be used regardless."""
        return self._has_abstract_format

    @property
    def version_number(self) -> Tuple[int, int, int]:
        """
        The version number of the version this class instance holds the data of.
        eg (1, 13, 2)
        """
        return self._version_number

    @property
    def data_version(self) -> int:
        """
        The DataVersion number of the version this class instance holds the data of.
        This is an int but is only used for Java versions beyond 1.9 snapshot 15w32a and Bedrock versions beyond 1.10. Other versions will default to 0.
        """
        return self._data_version

    @property
    def block(self) -> BlockTranslator:
        """The BlockTranslator for this version"""
        self._load_translator("block", *self._block_extra_input)
        return self._block

    @property
    def entity(self) -> EntityTranslator:
        """The EntityTranslator for this version"""
        self._load_translator("entity")
        return self._entity

    @property
    def item(self) -> ItemTranslator:
        """The ItemTranslator for this version"""
        self._load_translator("item")
        return self._item

    @property
    def biome(self) -> BiomeTranslator:
        """The BiomeTranslator for this version"""
        if self._biome is None:
            self._biome = self._biome_callable()
        return self._biome

    def is_waterloggable(self, namespace_str: str, always=False):
        warnings.warn(
            "Version.is_waterloggable is depreciated and will be removed in the future. Please use Version.block.is_waterloggable instead",
            DeprecationWarning,
        )
        return self.block.is_waterloggable(namespace_str, always)

    def ints_to_block(self, block_id: int, block_data: int) -> "Block":
        warnings.warn(
            "Version.ints_to_block is depreciated and will be removed in the future. Please use Version.block.ints_to_block instead",
            DeprecationWarning,
        )
        return self.block.ints_to_block(block_id, block_data)

    def block_to_ints(self, block: "Block") -> Union[None, Tuple[int, int]]:
        warnings.warn(
            "Version.block_to_ints is depreciated and will be removed in the future. Please use Version.block.block_to_ints instead",
            DeprecationWarning,
        )
        return self.block.block_to_ints(block)

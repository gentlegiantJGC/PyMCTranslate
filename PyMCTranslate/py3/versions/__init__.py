import json
import os
from typing import Union, Tuple, Dict, TYPE_CHECKING
import glob

from PyMCTranslate import Block, minified, json_atlas
from PyMCTranslate.py3.versions.translate import translate
from ..versions.translation_database import BlockTranslator, EntityTranslator, ItemTranslator
from .biomes import BiomeTranslator

if TYPE_CHECKING:
    from PyMCTranslate.py3.translation_manager import TranslationManager

_version_data = {}


class Version:
    """
    Container for the version data.
    There will be an instance of this class for each unique combination of platform and version number.
    This is tot to be mistaken with SubVersion which is a level deeper than this.
    """
    def __init__(self, version_path: str, translation_manager: 'TranslationManager'):
        self._version_path = version_path
        self._translation_manager = translation_manager
        self._block = None
        self._entity = None
        self._item = None

        if version_path not in _version_data:
            _version_data[version_path] = {}
            if minified:
                # load meta.json.gz and store in _version_data[version_path]["meta"]
                raise NotImplementedError
            else:
                _version_data[version_path]["meta"] = meta = {}
                for file_name in ['__init__', '__waterloggable__', '__always_waterlogged__', '__biome_data__', '__block_entity_map__', '__numerical_block_map__']:
                    if os.path.isfile(os.path.join(version_path, f'{file_name}.json')):
                        with open(os.path.join(version_path, f'{file_name}.json')) as f:
                            meta[file_name] = json.load(f)

        meta = _version_data[version_path]["meta"]
        # unpack the __init__.json file
        init_file = meta['__init__']
        assert isinstance(init_file['platform'], str), f'The platform name defined in {version_path}/__init__.json is not a string'
        self._platform = init_file['platform']
        assert isinstance(init_file['version'], list) and len(init_file['version']) == 3, f'The version number defined in {version_path}/__init__.json is incorrectly formatted'
        self._version_number = tuple(init_file['version'])
        self._data_version: int = init_file.get('data_version', 0)
        assert isinstance(init_file['block_format'], str)
        self._block_format = init_file['block_format']
        self._has_abstract_format = self._block_format in ['numerical', 'pseudo-numerical']

        if self.block_format == 'numerical':
            self._numerical_block_map_inverse: Dict[Tuple[str, str], int] = {
                tuple(block_str.split(':', 1)): block_id for block_str, block_id in meta['__numerical_block_map__'].items()
                if isinstance(block_str, str) and ':' in block_str and isinstance(block_id, int)
            }
            self._numerical_block_map: Dict[int, Tuple[str, str]] = {val: key for key, val in self._numerical_block_map_inverse.items()}
        else:
            self._numerical_block_map: Dict[int, Tuple[str, str]] = {}
            self._numerical_block_map_inverse: Dict[Tuple[str, str], int] = {}

        if self.platform == 'java' and '__waterloggable__' in meta:
            self._waterloggable = set(meta['__waterloggable__'])
            self._always_waterlogged = set(meta['__always_waterlogged__'])
        else:
            self._waterloggable = None
            self._always_waterlogged = None
        self._biome = BiomeTranslator(meta['__biome_data__'], translation_manager)

        if init_file['block_entity_format'] == "str-id":
            with open(os.path.join(version_path, '__block_entity_map__.json')) as f:
                self.block_entity_map: Dict[str: str] = json.load(f)
                self.block_entity_map_inverse: Dict[str: str] = {val: key for key, val in self.block_entity_map.items()}
        else:
            self.block_entity_map = None
            self.block_entity_map_inverse = None

    def _load_translator(self, attr):
        """
        Internal method to load the data related to this class.
        This allows loading to be deferred until it is needed (if at all)
        """
        if not hasattr(self, f'_{attr}'):
            raise Exception(f'Unknown translator {attr}')
        if getattr(self, f'_{attr}') is None:
            if minified:
                raise NotImplementedError
            else:
                database = {}
                for fpath in glob.iglob(os.path.join(self._version_path, attr, '**', '*.json'), recursive=True):
                    database_ = database
                    rel_path = os.path.relpath(fpath, os.path.join(self._version_path, attr)).split(os.sep)
                    assert len(rel_path) == 5
                    for dir in rel_path[:-2]:
                        database_ = database_.setdefault(dir, {})
                    with open(fpath) as f:
                        database_[fpath[-1][:-5]] = json.load(f)
            setattr(self, f'_{attr}', database)

    def __repr__(self):
        return f'PyMCTranslate.Version({self.platform}, {self.version_number})'

    @property
    def block_format(self) -> str:
        """
        The format of the blocks in the native SubVersion for this version.
        This will be one of 'numerical', 'pseudo-numerical', 'blockstate' or 'nbt-blockstate'
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
        """Property to access if the version has a second abstracted format"""
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
        This is an int but is only used for Java versions beyond 1.9 snapshot 15w32a. Other versions will default to 0.
        """
        return self._data_version

    @property
    def block(self) -> BlockTranslator:
        """The BlockTranslator for this version"""
        self._load_translator('block')
        return self._block

    @property
    def entity(self) -> EntityTranslator:
        """The EntityTranslator for this version"""
        self._load_translator('entity')
        return self._entity

    @property
    def item(self) -> ItemTranslator:
        """The ItemTranslator for this version"""
        self._load_translator('item')
        return self._item

    @property
    def biome(self) -> BiomeTranslator:
        """The BiomeTranslator for this version"""
        return self._biome

    # TODO: consider moving these to the block translator
    def is_waterloggable(self, namespace_str: str, always=False):
        """
        A method to check if a block can be waterlogged.
        This method is only valid for Java blockstate format worlds,
        Other formats either don't have waterlogged blocks or don't have a limit on what can be stacked.
        :param namespace_str: "<namespace>:<base_name>"
        :param always: True to check if the block does not have a waterlogged property but is always waterlogged
        :return: Bool. True if it can be waterlogged. False if not or another format.
        """
        if always:
            if isinstance(self._always_waterlogged, set):
                return namespace_str in self._always_waterlogged
        else:
            if isinstance(self._waterloggable, set):
                return namespace_str in self._waterloggable
        return False

    def ints_to_block(self, block_id: int, block_data: int) -> 'Block':
        if block_id in self._translation_manager.block_registry:
            namespace, base_name = self._translation_manager.block_registry.private_to_str(block_id).split(':', 1)
        elif block_id in self._numerical_block_map:
            namespace, base_name = self._numerical_block_map[block_id]
        else:
            return Block(namespace="minecraft", base_name="numerical", properties={"block_id": str(block_id), "block_data": str(block_data)})

        return Block(namespace=namespace, base_name=base_name, properties={"block_data": str(block_data)})

    def block_to_ints(self, block: 'Block') -> Union[None, Tuple[int, int]]:
        block_id = None
        block_data = None
        block_tuple = (block.namespace, block.base_name)
        if block.namespaced_name in self._translation_manager.block_registry:
            block_id = self._translation_manager.block_registry.private_to_int(block.namespaced_name)
        elif block_tuple in self._numerical_block_map_inverse:
            block_id = self._numerical_block_map_inverse[block_tuple]
        elif block_tuple == ("minecraft", "numerical") and "block_id" in block.properties and\
            isinstance(block.properties["block_id"], str) and block.properties["block_id"].isnumeric():
            block_id = int(block.properties["block_id"])

        if "block_data" in block.properties and isinstance(block.properties["block_data"], str) and block.properties["block_data"].isnumeric():
            block_data = int(block.properties["block_data"])

        if block_id is not None and block_data is not None:
            return block_id, block_data

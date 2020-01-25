from PyMCTranslate import Block, BlockEntity, Entity
from PyMCTranslate.py3.util import directories, files
from PyMCTranslate.py3.log import info, log_level
from PyMCTranslate.py3._translate import translate
import json
import os
from typing import Union, Tuple, List, Dict, Callable, TYPE_CHECKING
import copy
import traceback

from PyMCTranslate.py3.biomes import BiomeVersionManager

if TYPE_CHECKING:
    from PyMCTranslate.py3.translation_manager import TranslationManager


class Version:
    """
    Container for the version data.
    There will be an instance of this class for each unique combination of platform and version number.
    This is tot to be mistaken with SubVersion which is a level deeper than this.
    """
    def __init__(self, version_path: str, translation_manager: 'TranslationManager'):
        self._version_path = version_path
        self._translation_manager = translation_manager
        self._loaded = False

        # unpack the __init__.json file
        with open(os.path.join(version_path, '__init__.json')) as f:
            init_file = json.load(f)
        assert isinstance(init_file['platform'], str), f'The platform name defined in {version_path}/__init__.json is not a string'
        self._platform = init_file['platform']
        assert isinstance(init_file['version'], list) and len(init_file['version']) == 3, f'The version number defined in {version_path}/__init__.json is incorrectly formatted'
        self._version_number = tuple(init_file['version'])
        self._data_version: int = init_file.get('data_version', 0)
        assert isinstance(init_file['block_format'], str)
        self._block_format = init_file['block_format']
        self._has_abstract_format = self._block_format in ['numerical', 'pseudo-numerical']

        self._subversions = {}
        self._numerical_block_map: Dict[int, Tuple[str, str]] = {}
        self._numerical_block_map_inverse: Dict[Tuple[str, str], int] = {}
        if self.platform == 'java' and os.path.isfile(os.path.join(version_path, '__waterloggable__.json')):
            with open(os.path.join(version_path, '__waterloggable__.json')) as f:
                self._waterloggable = set(json.load(f))
            with open(os.path.join(version_path, '__always_waterlogged__.json')) as f:
                self._always_waterlogged = set(json.load(f))
        else:
            self._waterloggable = None
            self._always_waterlogged = None
        self.biomes = BiomeVersionManager(os.path.join(self._version_path, '__biome_data__.json'), translation_manager)

        if init_file['block_entity_format'] == "str-id":
            with open(os.path.join(version_path, '__block_entity_map__.json')) as f:
                self.block_entity_map: Dict[str: str] = json.load(f)
                self.block_entity_map_inverse: Dict[str: str] = {val: key for key, val in self.block_entity_map.items()}
        else:
            self.block_entity_map = None
            self.block_entity_map_inverse = None

    def _load(self):
        """
        Internal method to load the data related to this class.
        This allows loading to be deferred until it is needed (if at all)
        """
        if not self._loaded:
            if self.block_format in ['numerical', 'pseudo-numerical']:
                for block_format in ['blockstate', 'numerical']:
                    self._subversions[block_format] = SubVersion(self._translation_manager, self, os.path.join(self._version_path, 'block', block_format), block_format == 'blockstate')
                if self.block_format == 'numerical':
                    with open(os.path.join(self._version_path, '__numerical_block_map__.json')) as f:
                        self._numerical_block_map_inverse = {tuple(block_str.split(':', 1)): block_id for block_str, block_id in json.load(f).items()}
                    self._numerical_block_map = {}
                    for block_tuple, block_id in self._numerical_block_map_inverse.items():
                        assert isinstance(block_id, int) and isinstance(block_tuple, tuple) and all(isinstance(a, str) for a in block_tuple)
                        self._numerical_block_map[block_id] = block_tuple

            elif self.block_format in ['blockstate', 'nbt-blockstate']:
                self._subversions['blockstate'] = SubVersion(self._translation_manager, self, os.path.join(self._version_path, 'block', 'blockstate'), True)
            self._loaded = True

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

    def get(self, force_blockstate: bool = False) -> 'SubVersion':
        """
        A method to get a SubVersion class.
        :param force_blockstate: True to return the blockstate sub-version. False to return the native sub-version (these are sometimes the same thing)
        :return: The SubVersion class for the given inputs.
        """
        self._load()
        assert isinstance(force_blockstate, bool), 'force_blockstate must be a bool type'
        if force_blockstate:
            return self._subversions['blockstate']
        else:
            if self.block_format in ['numerical', 'pseudo-numerical']:
                return self._subversions['numerical']
            elif self.block_format in ['blockstate', 'nbt-blockstate']:
                return self._subversions['blockstate']
            else:
                raise NotImplemented

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


class SubVersion:
    """
    A class to store sub-version data.
    This is where things get a little confusing.
    Each version has a "native" format but the numerical formats (ones that rely on a data value rather than properties)
    also have an abstracted "blockstate" format.
    As such each version will always have a blockstate format but some may also have a numerical format as well.
    This class will store data for one of these sub-versions.
    """
    def __init__(self, translation_manager: 'TranslationManager', parent_version: Version, sub_version_path: str, is_blockstate: bool):
        self._translation_manager = translation_manager
        self._parent_version = parent_version
        self._is_blockstate = is_blockstate

        self._mappings = {
            "block": {
                'to_universal': {},
                'from_universal': {},
                'specification': {}
            },
            "entity": {
                'to_universal': {},
                'from_universal': {},
                'specification': {}
            }
        }
        self._cache = {  # only blocks without a block entity can be cached
            'to_universal': {

            },
            'from_universal': {

            }
        }
        assert os.path.isdir(sub_version_path), f'{sub_version_path} is not a valid path'
        for method in ['to_universal', 'from_universal', 'specification']:
            if os.path.isdir(os.path.join(sub_version_path, method)):
                for namespace in directories(os.path.join(sub_version_path, method)):
                    self._mappings["block"][method][namespace] = {}
                    for group_name in directories(os.path.join(sub_version_path, method, namespace)):
                        for block in files(os.path.join(sub_version_path, method, namespace, group_name)):
                            if block.endswith('.json'):
                                with open(os.path.join(sub_version_path, method, namespace, group_name, block)) as f:
                                    self._mappings["block"][method][namespace][block[:-5]] = json.load(f)

    def __repr__(self):
        return f'PyMCTranslate.SubVersion({self._parent_version.platform}, {self._parent_version.version_number}, {self.is_blockstate})'

    @property
    def is_blockstate(self) -> bool:
        """
        Does this sub-version store data in blockstate format
        :return: bool
        """
        return self._is_blockstate

    @property
    def is_abstract(self) -> bool:
        """
        Does the sub-version hold data related to the abstract format (True) or the native format (False)
        The formats with a numerical data value also have an abstract format implemented modeled on the blockstate format.
        Will return False for the native numerical format and blockstate if that is the native format.
        :return: bool
        """
        return self._parent_version.has_abstract_format and self.is_blockstate

    def namespaces(self, mode: str) -> List[str]:
        """
        A list of all the namespaces present in a given mode.
        :param mode:str: should be "block" or "entity"
        :return: A list of all the namespaces
        """
        return list(self._mappings[mode]['specification'].keys())

    def base_names(self, mode: str, namespace: str) -> List[str]:
        """
        A list of all the base names present in a given mode and namespace.
        :param mode:str: should be "block" or "entity"
        :param namespace: A namespace string as found using the namespaces method
        :return: A list of base names
        """
        return list(self._mappings[mode]['specification'][namespace])

    def get_specification(self, mode: str, namespace: str, base_name: str) -> dict:
        """
        Get the specification file for the requested object.
        :param mode:str: should be "block" or "entity"
        :param namespace: A namespace string as found using the namespaces method
        :param base_name: A base name string as found using the base_name method
        :return: A dictionary containing the specification for the object
        """
        try:
            return copy.deepcopy(self._mappings[mode]['specification'][namespace][base_name])
        except KeyError:
            raise KeyError(f'Specification for {mode} {namespace}:{base_name} does not exist')

    def get_mapping_to_universal(self, mode: str, namespace: str, base_name: str) -> List[dict]:
        """
        Get the mapping file for the requested object from this version format to the universal format.
        :param mode:str: should be "block" or "entity"
        :param namespace: A namespace string as found using the namespaces method
        :param base_name: A base name string as found using the base_name method
        :return: A list of mapping functions to apply to the object
        """
        try:
            return copy.deepcopy(self._mappings[mode]['to_universal'][namespace][base_name])
        except KeyError:
            raise KeyError(f'Mapping to universal for {mode} {namespace}:{base_name} does not exist')

    def get_mapping_from_universal(self, mode: str, namespace: str, base_name: str) -> List[dict]:
        """
        Get the mapping file for the requested object from the universal format to this version format.
        :param mode:str: should be "block" or "entity"
        :param namespace: A namespace string as found using the namespaces method
        :param base_name: A base name string as found using the base_name method
        :return: A list of mapping functions to apply to the object
        """
        try:
            return copy.deepcopy(self._mappings[mode]['from_universal'][namespace][base_name])
        except KeyError:
            raise KeyError(f'Mapping from universal for {mode} {namespace}:{base_name} does not exist')

    def to_universal(self, object_input: Union['Block', 'Entity'], get_block_callback: Callable = None, extra_input: 'BlockEntity' = None) -> Tuple[Union['Block', 'Entity'], Union['BlockEntity', None], bool]:
        """
        A method to translate a given Block or Entity object to the Universal format.
        :param object_input: The object to translate
        :param get_block_callback: see get_block_at function at the top of _translate for a template
        :param extra_input: secondary to the object_input a block entity can be given. This should only be used in the select block tool or plugins. Not compatible with location
        :return: output, extra_output, extra_needed
            output - a Block or Entity instance
            extra_output - None or BlockEntity if there is a BlockEntity to return (only if output is Block)
            extra_needed - bool specifying if the location is needed to fully define the output
        """
        if isinstance(object_input, Block):
            mode = 'block'
        elif isinstance(object_input, Entity):
            mode = 'entity'
        else:
            raise AssertionError('object_input must be a Block or an Entity')
        try:
            output, extra_output, extra_needed, cacheable = translate(
                object_input,
                self.get_specification(mode, object_input.namespace, object_input.base_name),
                self.get_mapping_to_universal(mode, object_input.namespace, object_input.base_name),
                self._translation_manager.get_sub_version('universal', (1, 0, 0)),
                get_block_callback,
                extra_input
            )
            return output, extra_output, extra_needed
        except Exception as e:
            info(f'Error while converting {object_input} to universal\n{e}')
            if log_level >= 3:
                traceback.print_stack()
                traceback.print_exc()
            return object_input, None, True

    def from_universal(self, object_input: Union['Block', 'Entity'], get_block_callback: Callable = None, extra_input: 'BlockEntity' = None) -> Tuple[Union['Block', 'Entity'], Union['BlockEntity', None], bool]:
        """
        A method to translate a given Block or Entity object from the Universal format to the format of this class instance.
        :param object_input: The object to translate
        :param get_block_callback: see get_block_at function at the top of _translate for a template
        :param extra_input: secondary to the object_input a block entity can be given. This should only be used in the select block tool or plugins. Not compatible with location
        :return: output, extra_output, extra_needed
            output - a Block or Entity instance
            extra_output - None or BlockEntity if there is a BlockEntity to return (only if output is Block)
            extra_needed - bool specifying if the location is needed to fully define the output
        """
        if isinstance(object_input, Block):
            mode = 'block'
        elif isinstance(object_input, Entity):
            mode = 'entity'
        else:
            raise Exception('object_input must be a Block or an Entity')
        try:
            output, extra_output, extra_needed, cacheable = translate(
                object_input,
                self._translation_manager.get_sub_version('universal', (1, 0, 0)).get_specification(mode, object_input.namespace, object_input.base_name),
                self.get_mapping_from_universal(mode, object_input.namespace, object_input.base_name),
                self,
                get_block_callback,
                extra_input
            )
            return output, extra_output, extra_needed
        except Exception as e:
            info(f'Error while converting {object_input} from universal\n{e}')
            if log_level >= 3:
                traceback.print_exc()
            return object_input, None, True

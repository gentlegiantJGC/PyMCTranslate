import json
import os
from typing import Union, Tuple, Generator, List, Dict, Callable
import copy

try:
	from amulet.api.block import Block
except:
	from PyMCTranslate.py3.api.block import Block
from PyMCTranslate.py3.helpers.objects import BlockEntity, Entity  # TODO: switch these for more full ones in API

log_level = 0  # 0 for no logs, 1 or higher for warnings, 2 or higher for info, 3 or higher for debug

"""
Structure:

TranslationManager
	Version : bedrock_1_7_0
		SubVersion : numerical
			minecraft, other_namespace
		SubVersion : blockstate
			minecraft, other_namespace
			
	Version : java_1_12_0
		SubVersion : numerical
			minecraft, other_namespace
		SubVersion : blockstate
			minecraft, other_namespace
			
	Version : java_1_13_0
		SubVersion : blockstate
			minecraft, other_namespace
			
	Version : universal
		SubVersion : blockstate
			minecraft, other_namespace
"""


def debug(msg: str):
	if log_level >= 3:
		print(msg)


def info(msg: str):
	if log_level >= 2:
		print(msg)


def warn(msg: str):
	if log_level >= 1:
		print(msg)


def directories(path: str) -> Generator[str, None, None]:
	"""
	A generator of only directories in the given directory.
	:param path: str: the path to an existing directory on the current system
	"""
	for dir_name in os.listdir(path):
		if os.path.isdir(os.path.join(path, dir_name)):
			yield dir_name


def files(path: str) -> Generator[str, None, None]:
	"""
	A generator of only files in the given directory.
	:param path: str: the path to an existing directory on the current system
	"""
	for file_name in os.listdir(path):
		if os.path.isfile(os.path.join(path, file_name)):
			yield file_name


class NumericalRegistry:
	def __init__(self):
		self._to_str: Dict[int, str] = {}
		self._to_int: Dict[str, int] = {}

	def register(self, key: str, value: int):
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
		self._version_remap: Dict[
			Tuple[
				str,
				Union[Tuple[int, ...], int]
			],
			Tuple[int, int, int]
		] = {}

		self.blocks = NumericalRegistry()

		# Create a class for each of the versions and store them
		for version_name in directories(os.path.join(json_path, 'versions')):
			if os.path.isfile(os.path.join(json_path, 'versions', version_name, '__init__.json')):
				version = Version(os.path.join(json_path, 'versions', version_name), self)
				self._versions.setdefault(version.platform, {})
				self._versions[version.platform].setdefault(version.version_number, version)
				self._version_remap[(version.platform, version.data_version)] = version.version_number

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
		if platform == 'anvil':
			platform = 'java'
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
				if next_version is not None and next_version == version_number[:3]:
					self._version_remap[(platform, version_number)] = next_version
				elif previous_version is not None:
					self._version_remap[(platform, version_number)] = previous_version
				else:
					raise Exception(f'Could not find a version for Version({platform}, {version_number})')

			else:
				raise Exception(f'version number type {version_number.__class__} is not supported')
		return self._version_remap[(platform, version_number)]

	def get_sub_version(self, platform: str, version_number: Union[int, Tuple[int, ...], List[int]], force_blockstate=False) -> 'SubVersion':
		"""
		A method to get a SubVersion class.
		:param platform: The platform name (use TranslationManager.platforms to get the valid platforms)
		:param version_number: The version number (use TranslationManager.version_numbers to get version numbers for a given platforms)
		:param force_blockstate: True to return the blockstate sub-version. False to return the native sub-version (these are sometimes the same thing)
		:return: The SubVersion class for the given inputs. Throws an AssertionError if it does not exist.
		"""
		return self.get_version(platform, version_number).get(force_blockstate)


class Version:
	"""
	Container for the version data.
	There will be an instance of this class for each unique combination of platform and version number.
	This is tot to be mistaken with SubVersion which is a level deeper than this.
	"""
	def __init__(self, version_path: str, translation_manager: TranslationManager):
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
			with open(version_path, '__waterloggable__.json') as f:
				self._waterloggable = set(json.load(f))
		else:
			self._waterloggable = None

	def _load(self):
		"""
		Internal method to load the data related to this class.
		This allows loading to be deferred until it is needed (if at all)
		"""
		if not self._loaded:
			if self.block_format in ['numerical', 'pseudo-numerical']:
				for block_format in ['blockstate', 'numerical']:
					self._subversions[block_format] = SubVersion(os.path.join(self._version_path, 'block', block_format), self._translation_manager)
				if self.block_format == 'numerical':
					with open(os.path.join(self._version_path, '__numerical_block_map__.json')) as f:
						self._numerical_block_map_inverse = {tuple(block_str.split(':', 1)): block_id for block_str, block_id in json.load(f).items()}
					self._numerical_block_map = {}
					for block_tuple, block_id in self._numerical_block_map_inverse.items():
						assert isinstance(block_id, int) and isinstance(block_tuple, tuple) and all(isinstance(a, str) for a in block_tuple)
						self._numerical_block_map[block_id] = block_tuple

			elif self.block_format in ['blockstate', 'nbt-blockstate']:
				self._subversions['blockstate'] = SubVersion(os.path.join(self._version_path, 'block', 'blockstate'), self._translation_manager)
			self._loaded = True

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

	def is_waterloggable(self, namespace_str: str):
		"""
		A method to check if a block can be waterlogged.
		This method is only valid for Java blockstate format worlds,
		Other formats either don't have waterlogged blocks or don't have a limit on what can be stacked.
		:param namespace_str: "<namespace>:<base_name>"
		:return: Bool. True if it can be waterlogged. False if not or another format.
		"""
		if isinstance(self._waterloggable, set):
			return namespace_str in self._waterloggable
		return False

	def ints_to_block(self, block_id: int, block_data: int) -> Block:
		if block_id in self._translation_manager.blocks:
			namespace, base_name = self._translation_manager.blocks.to_str(block_id).split(':', 1)
		elif block_id in self._numerical_block_map:
			namespace, base_name = self._numerical_block_map[block_id]
		else:
			return Block(namespace="minecraft", base_name="numerical", properties={"block_id": str(block_id), "block_data": str(block_data)})

		return Block(namespace=namespace, base_name=base_name, properties={"block_data": str(block_data)})

	def block_to_ints(self, block: Block) -> Union[None, Tuple[int, int]]:
		block_id = None
		block_data = None
		block_tuple = (block.namespace, block.base_name)
		if block.namespaced_name in self._translation_manager.blocks:
			block_id = self._translation_manager.blocks.to_int(block.namespaced_name)
		elif block_tuple in self._numerical_block_map_inverse:
			block_id = self._numerical_block_map_inverse[block_tuple]
		elif block_tuple == ("minecraft", "numerical") and "block_id" in block.properties and\
			isinstance(block.properties["block_id"], str) and block.properties["block_id"].isnumeric():
			block_id = int(block.properties["block_id"])

		if "block_data" in block.properties and isinstance(block.properties["block_data"], str) and block.properties["block_data"].isnumeric():
			block_data = int(block.properties["block_data"])

		if block_id is not None and block_data is not None:
			return (block_id, block_data)


class SubVersion:
	"""
	A class to store sub-version data.
	This is where things get a little confusing.
	Each version has a "native" format but the numerical formats (ones that rely on a data value rather than properties)
	also have an abstracted "blockstate" format.
	As such each version will always have a blockstate format but some may also have a numerical format as well.
	This class will store data for one of these sub-versions.
	"""
	def __init__(self, sub_version_path: str, translation_manager: TranslationManager):
		self._translation_manager = translation_manager
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
			raise KeyError(f'Specification for {mode} {namespace}:{base_name} does not exist')

	def to_universal(self, object_input: Union[Block, Entity], get_block_callback: Callable = None, extra_input: BlockEntity = None) -> Tuple[Union[Block, Entity], Union[BlockEntity, None], bool]:
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
			info(f'Failed converting blockstate to universal\n{e}')
			return object_input, None, False

	def from_universal(self, object_input: Union[Block, Entity], get_block_callback: Callable = None, extra_input: BlockEntity = None) -> Tuple[Union[Block, Entity], Union[BlockEntity, None], bool]:
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
			info(f'Failed converting blockstate from universal\n{e}')
			return object_input, None, False


from PyMCTranslate.py3._translate import translate

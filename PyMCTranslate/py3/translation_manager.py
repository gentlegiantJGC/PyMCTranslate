import json
import os
from typing import Union, Tuple, Generator, List, Dict
import copy

try:
	from amulet.api.block import Block
except:
	from .api.block import Block
from .helpers.objects import Block, BlockEntity, Entity

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
	A generator of only directories in the given directory
	:param path: str: the path to an existing directory on the current system
	"""
	for dir_name in os.listdir(path):
		if os.path.isdir(f'{path}/{dir_name}'):
			yield dir_name


def files(path: str) -> Generator[str, None, None]:
	"""
	A generator of only files in the given directory
	:param path: str: the path to an existing directory on the current system
	"""
	for file_name in os.listdir(path):
		if os.path.isfile(f'{path}/{file_name}'):
			yield file_name


class TranslationManager:
	"""
	Container for the different versions
	A version in this context is a version of the game from a specific platform (ie platform and version number need to be the same)
	"""
	def __init__(self, mappings_path: str):
		self._versions: Dict[str, Dict[Tuple[int, int, int], 'Version']] = {}

		for version_name in directories(mappings_path):
			version = Version(f'{mappings_path}/{version_name}', self)
			self._versions.setdefault(version.platform, {})
			self._versions[version.platform].setdefault(version.version_number, version)

	def platforms(self) -> List[str]:
		"""Get a list of all the platforms there are Version classes for"""
		return list(self._versions.keys())

	def version_numbers(self, platform: str) -> List[Tuple[int, int, int]]:
		"""Get a list of all the version numbers there are Version classes for for a given platform"""
		return list(self._versions[platform].keys())

	def blocks

	def _get_version(self, platform: str, version_number: Tuple[int, int, int]):
		"""Internal method to pick a """
		assert platform in self._versions and version_number in self._versions[platform]
		return self._versions[platform][version_number]

	def to_universal(
		self,
		level,
		platform: str,
		version_number: Tuple[int, int, int],
		object_input: Union[Block, Entity],
		force_blockstate: bool = False,
		location: Tuple[int, int, int] = None
	) -> Tuple[Union[Block, Entity], Union[BlockEntity, None], bool]:
		"""Convert an object to the universal format"""
		return self._get_version(
			platform,
			version_number
		).to_universal(
			level,
			object_input,
			force_blockstate,
			location
		)

	def from_universal(
		self,
		level,
		platform: str,
		version_number: Tuple[int, int, int],
		object_input: Union[Block, Entity],
		force_blockstate: bool = False,
		location: Tuple[int, int, int] = None
	) -> Tuple[Union[Block, Entity], Union[BlockEntity, None], bool]:
		"""Convert an object from the universal format"""
		return self._get_version(
			platform,
			version_number
		).from_universal(
			level,
			object_input,
			force_blockstate,
			location
		)


class Version:
	"""
	Container for the data from each game and platform version. Not to be mistaken with SubVersion
	"""
	def __init__(self, version_path: str, translation_handler: TranslationManager):
		if os.path.isfile(f'{version_path}/__init__.json'):
			with open(f'{version_path}/__init__.json') as f:
				init_file = json.load(f)
			assert isinstance(init_file['platform'], str)
			self._platform = init_file['platform']
			assert isinstance(init_file['version'], list) and len(init_file['version']) == 3
			self._version_number = tuple(init_file['version'])
			assert isinstance(init_file['block_format'], str)
			self._block_format = init_file['block_format']

			self._subversions = {}
			self.numerical_block_map: Dict[str, str] = None
			self.numerical_block_map_inverse: Dict[str, str] = None

			if self.block_format in ['numerical', 'pseudo-numerical']:
				for block_format in ['blockstate', 'numerical']:
					self._subversions[block_format] = SubVersion(f'{version_path}/block/{block_format}', translation_handler)
				if self.block_format == 'numerical':
					with open(f'{version_path}/__numerical_block_map__.json') as f:
						self.numerical_block_map_inverse = json.load(f)
					self.numerical_block_map = {}
					for block_string, block_id in self.numerical_block_map_inverse.items():
						assert isinstance(block_id, int) and isinstance(block_string, str)
						self.numerical_block_map[block_id] = block_string

			elif self.block_format == 'blockstate':
				self._subversions['blockstate'] = SubVersion(f'{version_path}/block/blockstate', translation_handler)

	@property
	def block_format(self) -> str:
		return self._block_format

	@property
	def platform(self) -> str:
		return self._platform

	@property
	def version_number(self) -> Tuple[int, int, int]:
		return self._version_number

	def get(self, force_blockstate: bool = False) -> 'SubVersion':
		assert isinstance(force_blockstate, bool), 'force_blockstate must be a bool type'
		if force_blockstate:
			return self._subversions['blockstate']
		else:
			if self.block_format in ['numerical', 'pseudo-numerical']:
				return self._subversions['numerical']
			elif self.block_format == 'blockstate':
				return self._subversions['blockstate']
			else:
				raise NotImplemented

	def to_universal(self, level, object_input: Union[Block, Entity], force_blockstate: bool = False, location: Tuple[int, int, int] = None) -> Tuple[Union[Block, Entity], Union[BlockEntity, None], bool]:
		if isinstance(object_input, Block):
			if self.block_format == 'numerical' and not force_blockstate:
				assert object_input.base_name.isnumeric(), 'For the numerical block_format base_name must be an int converted to a string'
				namespace, base_name = self.numerical_block_map[object_input.base_name].split(':')
				object_input = Block(None, namespace, base_name, object_input.properties)
		elif isinstance(object_input, Entity):
			raise NotImplemented
		else:
			raise Exception
		return self.get(force_blockstate).to_universal(level, object_input, location)

	def from_universal(self, level, object_input: Union[Block, Entity], force_blockstate: bool = False, location: Tuple[int, int, int] = None) -> Tuple[Union[Block, Entity], Union[BlockEntity, None], bool]:
		assert isinstance(object_input, (Block, Entity)), f'Input must be a Block or an Entity. Got "{type(object_input)}" instead.'

		output, extra_output, extra_needed = self.get(force_blockstate).from_universal(level, object_input, location)
		if isinstance(output, Block):
			if self.block_format == 'numerical':
				namespace, base_name = '', self.numerical_block_map_inverse[output.base_name]
				output = Block(None, namespace, base_name, object_input.properties)
		elif isinstance(object_input, Entity):
			raise NotImplemented
		else:
			raise Exception
		return output, extra_output, extra_needed


class SubVersion:
	"""
	Within each unique game version there may be more than one format
	(if it is numerical or pseudo-numerical it will have both a numerical and blockstate format)
	This is the container where that data will be stored.
	"""
	def __init__(self, sub_version_path: str, version_container: VersionContainer):
		self._version_container = version_container
		self._mappings = {
			"block": {
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
			if os.path.isdir(f'{sub_version_path}/{method}'):
				for namespace in directories(f'{sub_version_path}/{method}'):
					self._mappings["block"][method][namespace] = {}
					for group_name in directories(f'{sub_version_path}/{method}/{namespace}'):
						for block in files(f'{sub_version_path}/{method}/{namespace}/{group_name}'):
							if block.endswith('.json'):
								with open(f'{sub_version_path}/{method}/{namespace}/{group_name}/{block}') as f:
									self._mappings["block"][method][namespace][block[:-5]] = json.load(f)

	@property
	def namespaces(self) -> List[str]:
		return list(self._mappings['block']['specification'].keys())

	def block_names(self, namespace: str) -> List[str]:
		return list(self._mappings['block']['specification'][namespace])

	def get_specification(self, mode: str, namespace: str, name: str) -> dict:
		try:
			return copy.deepcopy(self._mappings[mode]['specification'][namespace][name])
		except KeyError:
			raise KeyError(f'Specification for {mode} {namespace}:{name} does not exist')

	def get_mapping_to_universal(self, mode: str, namespace: str, name: str) -> dict:
		try:
			return copy.deepcopy(self._mappings[mode]['to_universal'][namespace][name])
		except KeyError:
			raise KeyError(f'Mapping to universal for {mode} {namespace}:{name} does not exist')

	def get_mapping_from_universal(self, mode: str, namespace: str, name: str) -> dict:
		try:
			return copy.deepcopy(self._mappings[mode]['from_universal'][namespace][name])
		except KeyError:
			raise KeyError(f'Specification for {mode} {namespace}:{name} does not exist')

	def to_universal(self, level, object_input: Union[Block, Entity], location: Tuple[int, int, int] = None) -> Tuple[Union[Block, Entity], Union[BlockEntity, None], bool]:
		if isinstance(object_input, Block):
			mode = 'block'
		elif isinstance(object_input, Entity):
			mode = 'entity'
		else:
			raise AssertionError('object_input must be a Block or an Entity')
		try:
			output, extra_output, extra_needed, cacheable = convert(
				level,
				object_input,
				self.get_specification(mode, object_input.namespace, object_input.base_name),
				self.get_mapping_to_universal(mode, object_input.namespace, object_input.base_name),
				self._version_container.get('universal', (1, 0, 0)).get(),
				location
			)
			return output, extra_output, extra_needed
		except Exception as e:
			info(f'Failed converting blockstate to universal\n{e}')
			return object_input, None, False

	def from_universal(self, level, object_input: Union[Block, Entity], location: Tuple[int, int, int] = None) -> Tuple[Union[Block, Entity], Union[BlockEntity, None], bool]:
		"""

		:param level:
		:param object_input:
		:param location:
		:return:
		"""
		if isinstance(object_input, Block):
			mode = 'block'
		elif isinstance(object_input, Entity):
			raise NotImplemented
		else:
			raise Exception
		try:
			output, extra_output, extra_needed, cacheable = convert(
				level,
				object_input,
				self._version_container.get('universal', (1, 0, 0)).get().get_specification(mode, object_input.namespace, object_input.base_name),
				self.get_mapping_from_universal(mode, object_input.namespace, object_input.base_name),
				self,
				location
			)
			return output, extra_output, extra_needed
		except Exception as e:
			info(f'Failed converting blockstate from universal\n{e}')
			return object_input, None, False

from .convert import convert


if __name__ == '__main__':
	print('Loading mappings...')
	block_mappings = TranslationManager(r'..\mappings')
	print('\tFinished')
	info('==== bedrock_1_7_0 ====')
	for data in range(16):
		print(
			block_mappings.to_universal(None, 'bedrock', (1, 7, 0), Block(None, 'minecraft', 'log', {'block_data': str(data)}))[0]
		)
	info('==== java_1_12_2 ====')
	for data in range(16):
		print(
			block_mappings.to_universal(None, 'java', (1, 12, 2), Block(None, 'minecraft', '17', {'block_data': str(data)}))[0]
		)

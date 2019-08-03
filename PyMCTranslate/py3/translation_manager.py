import json
import os
from typing import Union, Tuple, Generator, List, Dict
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
	Container and manager for the different translation versions
	A version in this context is a version of the game from a specific platform
	(ie a unique combination of platform and version number)
	"""
	def __init__(self, mappings_path: str):
		"""
		Call this class with the path to the mapping json files.
		Note if you are a developer using this library you can call PyMCTranslate.new_translation_handler()
		to get a new instance of this class with the default mappings set up for you.

		:param mappings_path: The path to the mapping directory
		"""
		# Storage for each of the Version classes
		self._versions: Dict[str, Dict[Tuple[int, int, int], 'Version']] = {}

		# Create a class for each of the versions and store them
		for version_name in directories(mappings_path):
			version = Version(f'{mappings_path}/{version_name}', self)
			self._versions.setdefault(version.platform, {})
			self._versions[version.platform].setdefault(version.version_number, version)

	def platforms(self) -> List[str]:
		"""Get a list of all the platforms there are Version classes for"""
		return list(self._versions.keys())

	def version_numbers(self, platform: str) -> List[Tuple[int, int, int]]:
		"""
		Get a list of all the version numbers there are Version classes for, for a given platform
		:param platform: The platform name (use TranslationManager.platforms to get the valid platforms)
		:return: The a list of version numbers (tuples) for a given platform. Throws an AssertionError if the platform is not present.
		"""
		assert platform in self._versions, f'The requested platform "{platform}" is not present'
		return list(self._versions[platform].keys())

	def get_version(self, platform: str, version_number: Tuple[int, int, int]) -> 'Version':
		"""
		A method to get a Version class
		:param platform: The platform name (use TranslationManager.platforms to get the valid platforms)
		:param version_number: The version number (use TranslationManager.version_numbers to get version numbers for a given platforms)
		:return: The Version class for the given inputs. Throws an AssertionError if it does not exist.
		"""
		assert platform in self._versions and version_number in self._versions[platform], f'The requested version "({platform}, {version_number})" is not present'
		return self._versions[platform][version_number]

	def get_sub_version(self, platform: str, version_number: Tuple[int, int, int], force_blockstate=False) -> 'SubVersion':
		"""
		A method to get a SubVersion class
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


class SubVersion:
	"""
	A class to store sub-version data
	This is where things get a little confusing.
	Each version has a "native" format but the numerical formats (ones that rely on a data value rather than properties)
	also have an abstracted "blockstate" format.
	As such each version will always have a blockstate format but some may also have a numerical format as well.
	This class will store data for one of these sub-versions.
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

from PyMCTranslate.py3.convert import convert


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

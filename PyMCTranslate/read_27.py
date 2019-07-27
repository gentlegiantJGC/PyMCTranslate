import json
import os


"""
Structure:

VersionContainer
	Version : bedrock_1_7_0
		SubVersion : numerical
			Namespace : minecraft
			Namespace : other_namespace
		SubVersion : blockstate
			Namespace : minecraft
			Namespace : other_namespace
			
	Version : java_1_12_0
		SubVersion : numerical
			Namespace : minecraft
			Namespace : other_namespace
		SubVersion : blockstate
			Namespace : minecraft
			Namespace : other_namespace
			
	Version : java_1_13_0
		SubVersion : blockstate
			Namespace : minecraft
			Namespace : other_namespace
			
	Version : universal
		SubVersion : blockstate
			Namespace : minecraft
			Namespace : other_namespace
"""


def directories(path):
	"""
	A generator of only directories in the given directory
	:param path: the path to an existing directory on the current system
	"""
	for dir_name in os.listdir(path):
		if os.path.isdir('{}/{}'.format(path, dir_name)):
			yield dir_name


def files(path):
	"""
	A generator of only files in the given directory
	:param path: the path to an existing directory on the current system
	"""
	for file_name in os.listdir(path):
		if os.path.isfile('{}/{}'.format(path, file_name)):
			yield file_name


def get_nbt(level, location):
	return level.tileEntityAt(*location)


class VersionContainer:
	"""
	Container for the different versions
	"""
	def __init__(self, mappings_path):
		self._versions = {}

		for version_name in directories(mappings_path):
			version = Version('{}/{}'.format(mappings_path, version_name), self)

			if version.platform not in self.versions:
				self.versions[version.platform] = {}
			if version.version_number not in self.versions[version.platform]:
				self.versions[version.platform][version.version_number] = version

	@property
	def versions(self):
		return self._versions

	def get(self, platform, version_number):
		assert platform in self.versions and version_number in self.versions[platform]
		return self.versions[platform][version_number]

	def to_universal(self, level, platform, version_number, namespace, block_id, properties, force_blockstate=False, location=None):
		return self.get(platform, version_number).to_universal(level, namespace, block_id, properties, force_blockstate, location)

	def from_universal(self, level, platform, version_number, namespace, block_id, properties, force_blockstate=False):
		return self.get(platform, version_number).from_universal(level, namespace, block_id, properties, force_blockstate)


class Version:
	"""
	Container for the data from each game and platform version. Not to be mistaken with SubVersion
	"""
	def __init__(self, version_path, version_container):
		if os.path.isfile('{}/__init__.json'.format(version_path)):
			with open('{}/__init__.json'.format(version_path)) as f:
				init_file = json.load(f)
			assert isinstance(init_file['platform'], str) or isinstance(init_file['platform'], unicode)
			self._platform = init_file['platform']
			assert isinstance(init_file['version'], list) and len(init_file['version']) == 3
			self._version_number = tuple(init_file['version'])
			assert isinstance(init_file['block_format'], str) or isinstance(init_file['block_format'], unicode)
			self._format = init_file['block_format']

			self._subversions = {}
			self._numerical_map = None
			self._numerical_map_inverse = None

			if self.format in ['numerical', 'pseudo-numerical']:
				for block_format in ['blockstate', 'numerical']:
					self._subversions[block_format] = SubVersion('{}/{}'.format(version_path, block_format), version_container)
				if self.format == 'numerical':
					with open('{}/__numerical_block_map__.json'.format(version_path)) as f:
						self._numerical_map = json.load(f)
					self._numerical_map_inverse = {}
					for block_id, block_string in self._numerical_map.items():
						assert (isinstance(block_id, str) or isinstance(block_id, unicode)) and (isinstance(block_string, str) or isinstance(block_string, unicode)) and block_id.isnumeric()
						self._numerical_map_inverse[block_string] = block_id

			elif self.format == 'blockstate':
				self._subversions['blockstate'] = SubVersion(version_path, version_container)

	@property
	def format(self):
		return self._format

	@property
	def platform(self):
		return self._platform

	@property
	def version_number(self):
		return self._version_number

	def get(self, force_blockstate=False):
		if force_blockstate:
			return self._subversions['blockstate']
		else:
			if self.format in ['numerical', 'pseudo-numerical']:
				return self._subversions['numerical']
			elif self.format == 'blockstate':
				return self._subversions['blockstate']

	def to_universal(self, level, namespace, block_name, properties, force_blockstate=False, location=None):
		if self.format == 'numerical' and not force_blockstate:
			namespace, block_name = self._numerical_map[block_name].split(':')
		blockstate = self.get(force_blockstate).to_universal(level, namespace, block_name, properties, location)
		return blockstate

	def from_universal(self, level, namespace, block_name, properties, force_blockstate=False):
		blockstate = self.get(force_blockstate).from_universal(level, namespace, block_name, properties)
		if self.format == 'numerical':
			blockstate['block_name'] = self._numerical_map_inverse[blockstate['block_name']]
		return blockstate


class SubVersion:
	"""
	Within each unique game version there may be more than one block_format
	(if it is numerical or pseudo-numerical it will have both a numerical and blockstate block_format)
	This is the container where that data will be stored.
	"""
	def __init__(self, sub_version_path, version_container):
		self.namespaces = {}
		for namespace in directories(sub_version_path):
			self.namespaces[namespace] = Namespace('{}/{}'.format(sub_version_path, namespace), namespace, version_container, self)

	def to_universal(self, level, namespace, block_name, properties, location=None):
		try:
			return self.get(namespace).to_universal(level, block_name, properties, location)
		except Exception as e:
			print('Failed getting namespace. It may not exist.\n{}'.format(e))
			return {'block_name': '{}/{}'.format(namespace, block_name), 'properties': properties}

	def from_universal(self, level, namespace, block_name, properties):
		try:
			return self.get(namespace).from_universal(level, block_name, properties)
		except Exception as e:
			print('Failed getting namespace. It may not exist.\n{}'.format(e))
			return {'block_name': '{}/{}'.format(namespace, block_name), 'properties': properties}

	def get(self, namespace):
		assert namespace in self.namespaces
		return self.namespaces[namespace]


class Namespace:
	"""
	Container for each namespace
	"""
	def __init__(self, namespace_path, namespace, version_container, current_version):
		self._namespace = namespace
		self.version_container = version_container
		self.current_version = current_version
		self._blocks = {'to_universal': {}, 'from_universal': {}, 'specification': {}}
		for group_name in directories(namespace_path):
			for method in ['to_universal', 'from_universal', 'specification']:
				if os.path.isdir('{}/{}/{}'.format(namespace_path, group_name, method)):
					for block in files('{}/{}/{}'.format(namespace_path, group_name, method)):
						with open('{}/{}/{}/{}'.format(namespace_path, group_name, method, block)) as f:
							self._blocks[method][block[:-5]] = json.load(f)

	@property
	def namespace(self):
		return self._namespace

	def get_specification(self, block_name):
		return self._blocks['specification'][block_name]

	def get_mapping_to_universal(self, block_name):
		return self._blocks['to_universal'][block_name]

	def get_mapping_from_universal(self, block_name):
		return self._blocks['from_universal'][block_name]

	def to_universal(self, level, block_name, properties, location=None):
		blockstate = {'block_name': '{}:{}'.format(self.namespace, block_name), 'properties': properties}
		extra = False
		try:
			blockstate, extra = self.convert(
				level,
				blockstate,
				self._blocks['to_universal'][block_name],
				self.version_container.get('universal', (1, 0, 0)).get(),
				location
			)
			if blockstate['nbt'] != {}:
				print('universal mappings should not have nbt: {}'.format(blockstate))
			del blockstate['nbt']

		except Exception as e:
			print('Failed converting blockstate to universal\n{}'.format(e))
		return blockstate, extra

	def from_universal(self, level, block_name, properties):
		blockstate = {'block_name': '{}:{}'.format(self.namespace, block_name), 'properties': properties}
		try:
			return self.convert(
				level,
				blockstate,
				self._blocks['from_universal'][block_name],
				self.current_version
			)
		except Exception as e:
			print('Failed converting blockstate from universal\n{}'.format(e))
			return blockstate

	def convert(self, level, input_blockstate, mappings, output_version, location=None):
		"""
			A demonstration function on how to read the json files to convert into or out of the numerical block_format
			You should implement something along these lines into you own code if you want to read them.

			:param level: a view into the level to access additional data
			:param input_blockstate: the blockstate put into the converter eg {'block_name': 'minecraft:log', 'properties': {'block_data': '0'}}
			:param mappings: the mapping file for that block
			:param output_version: A way for the function to look at the specification being converted to. (used to load default properties)
			:param location: (x, y, z) only used if data beyond the blockstate is needed
			:return: The converted blockstate
		"""
		spec = self.get_specification(input_blockstate['block_name'].split(':')[-1])
		if 'nbt' in spec:
			if location is None:
				return input_blockstate, True
			else:
				nbt = get_nbt(level, location)
				input_blockstate['nbt'] = {}
				for key in spec['nbt']:
					_nbt = nbt
					path = spec['nbt'][key].get('path', []) + [spec['nbt'][key]['name'], spec['nbt'][key]['type']]
					try:
						assert _nbt.__class__.__name__ == 'TAG_Compound'
						for path_key, dtype in path:
							_nbt = _nbt[path_key]
							assert _nbt.__class__.__name__ == {
								'compound': 'TAG_Compound',
								'list': 'TAG_List',
								'byte': 'TAG_Byte',
								'short': 'TAG_Short',
								'int': 'TAG_Int',
								'long': 'TAG_Long',
								'float': 'TAG_Float',
								'double': 'TAG_Double',
								'string': 'TAG_String'
							}[dtype]
						input_blockstate['nbt'][key] = str(_nbt.value)
					except:
						input_blockstate['nbt'][key] = spec['nbt'][key]['default']

		output_blockstate, new, extra = self._convert(level, input_blockstate, mappings, output_version, location)
		for entry in ['properties', 'nbt']:
			for key, val in new[entry].items():
				output_blockstate[entry][key] = val
		return output_blockstate, extra

	def _convert(self, level, input_blockstate, mappings, output_version, location=None):
		output_blockstate = {'block_name': None, 'properties': {}, 'nbt': {}}
		new = {'properties': {}, 'nbt': {}}  # There could be multiple 'new_block' functions in the mappings so new properties are put in here and merged at the very end
		extra = False  # used to determine if extra data is required (and thus to do block by block)
		if 'new_block' in mappings:
			assert isinstance(mappings['new_block'], str) or isinstance(mappings['new_block'], unicode)
			output_blockstate['block_name'] = mappings['new_block']
			namespace, block_name = output_blockstate['block_name'].split(':')
			output_blockstate['properties'] = output_version.get(namespace).get_specification(block_name).get('defaults', {})

		if 'new_properties' in mappings:
			for key, val in mappings['new_properties'].items():
				new['properties'][key] = val

		if 'new_nbt' in mappings:
			for key, val in mappings['new_nbt'].items():
				new['nbt'][key] = val

		if 'carry_properties' in mappings:
			for key in mappings['carry_properties']:
				if key in input_blockstate['properties']:
					val = input_blockstate['properties'][key]
					if val in mappings['carry_properties'][key]:
						new['properties'][key] = val
				else:
					raise Exception('Property "{}" is not present in the input blockstate'.format(key))

		if 'multiblock' in mappings:
			if location is None:
				return output_blockstate, new, True

		if 'map_properties' in mappings:
			for key in mappings['map_properties']:
				if key in input_blockstate['properties']:
					val = input_blockstate['properties'][key]
					if val in mappings['map_properties'][key]:
						temp_blockstate, temp_new, extra = self._convert(level, input_blockstate, mappings['map_properties'][key][val], output_version)
						if extra:
							return output_blockstate, new, extra
						if temp_blockstate['block_name'] is not None:
							output_blockstate = temp_blockstate
						for entry in ['properties', 'nbt']:
							for key2, val2 in temp_new[entry].items():
								new[entry][key2] = val2
					else:
						raise Exception('Value "{}" for property "{}" is not present in the mappings'.format(val, key))
				else:
					raise Exception('Property "{}" is not present in the input blockstate'.format(key))

		'map_block_name'

		if 'map_nbt' in mappings:
			if location is None:
				return output_blockstate, new, True

		return output_blockstate, new, extra


if __name__ == '__main__':
	block_mappings = VersionContainer(r'..\versions')
	print('==== bedrock_1_7_0 ====')
	for data in range(16):
		print(
			block_mappings.to_universal(None, 'bedrock', (1, 7, 0), 'minecraft', 'log', {'block_data': str(data)})
		)
	print('==== java_1_12_2 ====')
	for data in range(16):
		print(
			block_mappings.to_universal(None, 'java', (1, 12, 2), 'minecraft', '17', {'block_data': str(data)})
		)


def perform(level, box, options):
	block_mappings = VersionContainer(r'C:\Users\james_000\Documents\GitHub\Minecraft-Universal-Block-Mappings\versions')
	print '='*20
	for x, y, z in box.positions:
		block_name = str(level.materials.idStr[level.blockAt(x, y, z)])
		if block_name == '':
			continue
		print(
			block_mappings.to_universal(level, 'bedrock', (1, 7, 0), 'minecraft', block_name, {'block_data': str(level.blockDataAt(x, y, z))})
		)

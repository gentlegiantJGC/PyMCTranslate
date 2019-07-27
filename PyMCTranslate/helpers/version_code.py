from typing import Union, Tuple
from .objects import Block, BlockEntity, Entity
from .nbt import NBT, TAG_Compound, TAG_String, TAG_Short
from ..data_version_handler import Version

"""
block formats
	numerical
	pseudo-numerical
	blockstate
	nbt-blockstate

block entity formats
	int-id
	str-id
	namespace-str-id

entity formats
	int-id
	str-id
	namespace-str-id
	namespace-str-identifier
"""


def block_from_disk(version: Version, block: Union[Tuple[int, int], NBT, str]) -> Block:
	if version.block_format == 'numerical':
		assert isinstance(block, tuple) and len(block) == 2 and all(isinstance(a, int) for a in block), 'Block must be an tuple of two integers for the numerical format'
		block, data = block
		if str(block) in version.numerical_block_map:
			namespace, base_name = version.numerical_block_map[str(block)].split(':', 1)
			return Block(
				None,
				namespace,
				base_name,
				{
					"block_data": str(data)
				}
			)
		else:
			return Block(
				None,
				'minecraft',
				'numerical',
				{
					"block_id": str(block),
					"block_data": str(data)
				}
			)

	elif version.block_format == 'pseudo-numerical':
		assert isinstance(block, NBT), 'Block must be an integer for the numerical format'
		namespace, base_name = block['name'].split(':', 1)
		return Block(
			None,
			namespace,
			base_name,
			{
				"block_data": str(block['val'])
			}
		)

	elif version.block_format == 'blockstate':
		return Block(block)
		# TODO: check if block is waterloggable
			#  if it is waterloggable and is waterlogged set the second block
			#  delete the waterlogged property
	else:
		raise AssertionError(f'Format {version.block_format} is not implemented/supported')


def blockentity_from_disk(version: Version, nbt: NBT) -> BlockEntity:
	pass


def entity_from_disk(version: Version, nbt: NBT) -> Entity:
	pass


def block_to_disk(version: Version, block: Block) -> Union[Tuple[int, int], NBT, str]:
	assert isinstance(block, Block)
	if version.block_format == 'numerical':
		if block.namespace == 'minecraft' and block.base_name == 'numerical':
			if 'block_id' in block.properties and 'block_data' in block.properties and \
				block.properties['block_id'].isnumeric() and \
				block.properties['block_data'].isnumeric():
				return int(block.properties['block_id']), int(block.properties['block_data'])
			else:
				raise NotImplemented
				# TODO: Ask for user input
		elif f'{block.namespace}:{block.base_name}' in version.numerical_block_map_inverse and \
			'block_data' in block.properties and \
			block.properties['block_data'].isnumeric():
			return int(
				version.numerical_block_map_inverse[f'{block.namespace}:{block.base_name}']
			), \
			int(
				block.properties['block_data']
			)
		else:
			raise NotImplemented
			# TODO: Ask for user input
	elif version.block_format == 'pseudo-numerical':
		if block.namespace == 'minecraft' and block.base_name == 'bedrock_string':
			if 'block_id' in block.properties and 'block_data' in block.properties and \
				block.properties['block_data'].isnumeric():
				return NBT(
					{
						"name": TAG_String(block.properties['block_id']),
						"val": TAG_Short(int(block.properties['block_data']))
					}
				)
			else:
				raise NotImplemented
				# TODO: Ask for user input
		elif 'block_data' in block.properties and block.properties['block_data'].isnumeric():
			return NBT(
				{
					"name": TAG_String(f'{block.namespace}:{block.base_name}'),
					"val": TAG_Short(int(block.properties['block_data']))
				}
			)
		else:
			raise NotImplemented
			# TODO: Ask for user input

	elif version.block_format == 'blockstate':
		return block.blockstate
		# TODO: check if there is a second block and if it is water.
			# If the block is waterloggable then set the property
	else:
		raise AssertionError(f'Format {version.block_format} is not implemented/supported')


def blockentity_to_disk(version: Version, nbt: BlockEntity) -> NBT:
	pass


def entity_to_disk(version: Version, nbt: Entity) -> NBT:
	pass

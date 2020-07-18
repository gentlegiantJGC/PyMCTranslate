import PyMCTranslate
from PyMCTranslate.py3.log import log
import itertools
import amulet_nbt as nbt
from typing import Optional, Any
from PyMCTranslate.py3.api import Block

test_block_list: Optional[list] = None

print_extra_needed = False


def in_and_out(platform_name: str, version_number: Any, version: PyMCTranslate.Version, input_blockstate: Block):
	# blockstate to universal
	try:
		universal_output, extra_output, extra_needed = version.block.to_universal(input_blockstate, force_blockstate=True)
	except:
		log.error('=' * 150)
		log.error(f'error to universal {platform_name} {version_number}')
		log.error(f'Blockstate input: {input_blockstate}')
		return
	if extra_needed or extra_output is not None:
		if print_extra_needed:
			log.error(f'skipping {platform_name} {version_number} {input_blockstate}. Needs more data')
		return

	if not universal_output.namespace.startswith('universal_'):
		log.error('=' * 150)
		log.error(f'Universal is not "universal_" {platform_name} {version_number}')
		log.error(f'Blockstate input: {input_blockstate}')
		log.error(f'Universal output: {universal_output}')

	if version.has_abstract_format:
		# universal to numerical
		try:
			numerical_output, extra_output, extra_needed = version.block.from_universal(universal_output)
		except:
			log.error('=' * 150)
			log.error(f'error from universal to numerical {platform_name} {version_number}')
			log.error(f'Blockstate input: {input_blockstate}')
			log.error(f'Universal output: {universal_output}')
			return
		if extra_needed or extra_output is not None:
			if print_extra_needed:
				log.error(f'skipping {platform_name} {version_number} {input_blockstate}. Needs more data')
			return

		# numerical to universal
		try:
			universal_output2, extra_output, extra_needed = version.block.to_universal(numerical_output)
		except:
			log.error('=' * 150)
			log.error(f'error from universal to blockstate {platform_name} {version_number}')
			log.error(f'Blockstate input: {input_blockstate}')
			log.error(f'Universal output: {universal_output}')
			log.error(f'Numerical output: {numerical_output}')
			return
		if extra_needed or extra_output is not None:
			if print_extra_needed:
				log.error(f'skipping {platform_name} {version_number} {input_blockstate}. Needs more data')
			return
	else:
		numerical_output = None
		universal_output2 = universal_output

	if not universal_output2.namespace.startswith('universal_'):
		log.error('=' * 150)
		log.error(f'Universal is not universal_ {platform_name} {version_number}')
		log.error(f'Blockstate input: {input_blockstate}')
		log.error(f'Universal output: {universal_output}')
		log.error(f'Numerical output: {numerical_output}')
		log.error(f'Universal output 2: {universal_output2}')

	# universal to blockstate
	try:
		back_out, extra_output, extra_needed = version.block.from_universal(universal_output2, force_blockstate=True)
	except:
		log.error('=' * 150)
		log.error(f'error from universal {platform_name} {version_number}')
		log.error(f'Blockstate input: {input_blockstate}')
		log.error(f'Universal output: {universal_output}')
		log.error(f'Numerical output: {numerical_output}')
		log.error(f'Universal output 2: {universal_output2}')
		return
	if str(input_blockstate) != str(back_out):
		if version.platform == 'java' and version.version_number[1] >= 13:
			props1 = input_blockstate.properties
			props2 = back_out.properties
			if 'waterlogged' in props1:
				del props1['waterlogged']
			if 'waterlogged' in props2:
				del props2['waterlogged']
			if str(Block(namespace=input_blockstate.namespace, base_name=input_blockstate.base_name, properties=props1)) \
					== \
					str(Block(namespace=back_out.namespace, base_name=back_out.base_name, properties=props2)):
				return

		log.error('=' * 150)
		log.error(f"Conversion error: {input_blockstate} != {back_out} {platform_name} {version_number}")
		log.error(f'Universal output: {universal_output}')
		log.error(f'Numerical output: {numerical_output}')
		log.error(f'Universal output 2: {universal_output2}')
		log.error(f'Blockstate: {back_out}')


def get_blockstates(version, namespace_str, base_name):
	block_specification = version.block.get_specification(namespace_str, base_name, True)
	properties = block_specification.get('properties', {})
	if len(properties) > 0:
		keys, values = zip(*properties.items())
	else:
		keys, values = (), ()
	values = tuple([nbt.from_snbt(val) for val in prop] for prop in values)

	for spec_ in itertools.product(*values):
		spec = dict(zip(keys, spec_))
		yield Block(namespace=namespace_str, base_name=base_name, properties=spec)


def main():
	translations = PyMCTranslate.new_translation_manager()

	if test_block_list is None:
		for platform_name in translations.platforms():
			for version_number in translations.version_numbers(platform_name):
				version = translations.get_version(platform_name, version_number)
				log.error(f'Checking version {platform_name} {version_number}')

				for namespace_str in version.block.namespaces(True):
					for base_name in version.block.base_names(namespace_str, True):
						for input_blockstate in get_blockstates(version, namespace_str, base_name):
							in_and_out(platform_name, version_number, version, input_blockstate)
				break
			break

	else:
		for block in test_block_list:
			platform_name, version_number, block_str = block
			namespace_str, base_name = block_str.split(':', 1)

			version = translations.get_version(platform_name, version_number)

			for input_blockstate in get_blockstates(version, namespace_str, base_name):
				in_and_out(platform_name, version_number, version, input_blockstate)


if __name__ == '__main__':
	main()

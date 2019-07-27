from reader.read import VersionContainer, Block
import itertools

if __name__ == '__main__':
	mappings = VersionContainer(r'..\mappings')
	for platform_name in mappings.platforms:
		for version_number in mappings.version_numbers(platform_name):
			version = mappings.get(platform_name, version_number)
			if not version.format == 'pseudo-numerical':
				print(f'skipping {platform_name} {version_number}. Not pseudo-numerical format')
				continue
			input_version = version.get()
			for namespace_str in input_version.namespaces:
				for block_name in input_version.block_names(namespace_str):
					block_specification = input_version.get_specification('block', namespace_str, block_name)
					properties = block_specification.get('properties', {})
					keys, values = zip(*properties.items())
					for spec_ in itertools.product(*values):
						spec = dict(zip(keys, spec_))
						input_numerical_block = Block(namespace_str, block_name, spec)
						# numerical to universal
						try:
							universal_output, extra_output, extra_needed = mappings.to_universal(None, platform_name, version_number, input_numerical_block)
						except:
							print('error to universal')
							print(f'Input numerical: {input_numerical_block}')
							continue
						if extra_needed or extra_output is not None:
							print(f'skipping {platform_name} {version_number} {input_numerical_block}. Needs more data')
							continue

						# universal to blockstate
						try:
							blockstate_output, extra_output, extra_needed = mappings.from_universal(None, platform_name, version_number, universal_output, True)
						except:
							print('error from universal to blockstate')
							print(f'Input numerical: {input_numerical_block}')
							print(f'Universal output: {universal_output}')
							continue
						if extra_needed or extra_output is not None:
							print(f'skipping {platform_name} {version_number} {input_numerical_block}. Needs more data')
							continue

						# blockstate to universal
						try:
							universal_output2, extra_output, extra_needed = mappings.to_universal(None, platform_name, version_number, blockstate_output, True)
						except:
							print('error from universal to blockstate')
							print(f'Input numerical: {input_numerical_block}')
							print(f'Universal output: {universal_output}')
							print(f'Blockstate output: {blockstate_output}')
							continue
						if extra_needed or extra_output is not None:
							print(f'skipping {platform_name} {version_number} {input_numerical_block}. Needs more data')
							continue

						# universal to numerical
						try:
							back_out, extra_output, extra_needed = mappings.from_universal(None, platform_name, version_number, universal_output)
						except:
							print('error from universal')
							print(f'Input numerical: {input_numerical_block}')
							print(f'Universal output: {universal_output}')
							print(f'Blockstate output: {blockstate_output}')
							print(f'Universal output 2: {universal_output2}')
							continue
						if str(input_numerical_block) != str(back_out):
							print(f"Conversion error: {input_numerical_block} != {back_out}")
							print(f'Universal output: {universal_output}')
							print(f'Blockstate output: {blockstate_output}')
							print(f'Universal output 2: {universal_output2}')
							print(f'Numerical: {back_out}')

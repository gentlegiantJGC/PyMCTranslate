import PyMCTranslate
from PyMCTranslate.py3.api.block import Block
import itertools

if __name__ == '__main__':
	translations = PyMCTranslate.new_translation_manager()
	for platform_name in translations.platforms():
		for version_number in translations.version_numbers(platform_name):
			version = translations.get_version(platform_name, version_number)
			blockstate_version = version.get(True)

			if version.has_abstract_format:
				numerical_version = version.get()
			else:
				numerical_version = None
			for namespace_str in blockstate_version.namespaces('block'):
				for base_name in blockstate_version.base_names('block', namespace_str):
					block_specification = blockstate_version.get_specification('block', namespace_str, base_name)
					properties = block_specification.get('properties', {})
					if len(properties) > 0:
						keys, values = zip(*properties.items())
					else:
						keys, values = (), ()
					for spec_ in itertools.product(*values):
						spec = dict(zip(keys, spec_))
						input_block = Block(namespace=namespace_str, base_name=base_name, properties=spec)
						# native to universal
						try:
							universal_output, extra_output, extra_needed = blockstate_version.to_universal(None, input_block)
						except:
							print('error to universal')
							print(f'Input numerical: {input_block}')
							continue
						if extra_needed or extra_output is not None:
							print(f'skipping {platform_name} {version_number} {input_block}. Needs more data')
							continue

						if numerical_version is not None:
							# universal to abstract
							try:
								blockstate_output, extra_output, extra_needed = numerical_version.from_universal(None, universal_output)
							except:
								print('error from universal to blockstate')
								print(f'Input numerical: {input_block}')
								print(f'Universal output: {universal_output}')
								continue
							if extra_needed or extra_output is not None:
								print(f'skipping {platform_name} {version_number} {input_block}. Needs more data')
								continue

							# blockstate to universal
							try:
								universal_output2, extra_output, extra_needed = numerical_version.to_universal(None, blockstate_output)
							except:
								print('error from universal to blockstate')
								print(f'Input numerical: {input_block}')
								print(f'Universal output: {universal_output}')
								print(f'Blockstate output: {blockstate_output}')
								continue
							if extra_needed or extra_output is not None:
								print(f'skipping {platform_name} {version_number} {input_block}. Needs more data')
								continue
						else:
							blockstate_output = None
							universal_output2 = universal_output

						# universal to numerical
						try:
							back_out, extra_output, extra_needed = blockstate_version.from_universal(None, universal_output2)
						except:
							print('error from universal')
							print(f'Input numerical: {input_block}')
							print(f'Universal output: {universal_output}')
							print(f'Blockstate output: {blockstate_output}')
							print(f'Universal output 2: {universal_output2}')
							continue
						if str(input_block) != str(back_out):
							print(f"Conversion error: {input_block} != {back_out}")
							print(f'Universal output: {universal_output}')
							print(f'Blockstate output: {blockstate_output}')
							print(f'Universal output 2: {universal_output2}')
							print(f'Numerical: {back_out}')

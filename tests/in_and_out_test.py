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
						input_blockstate = Block(namespace=namespace_str, base_name=base_name, properties=spec)
						# native to universal
						try:
							universal_output, extra_output, extra_needed = blockstate_version.to_universal(None, input_blockstate)
						except:
							print(f'error to universal {platform_name} {version_number}')
							print(f'Blockstate input: {input_blockstate}')
							continue
						if extra_needed or extra_output is not None:
							print(f'skipping {platform_name} {version_number} {input_blockstate}. Needs more data')
							continue

						if numerical_version is not None:
							# universal to abstract
							try:
								numerical_output, extra_output, extra_needed = numerical_version.from_universal(None, universal_output)
							except:
								print(f'error from universal to numerical {platform_name} {version_number}')
								print(f'Blockstate input: {input_blockstate}')
								print(f'Universal output: {universal_output}')
								continue
							if extra_needed or extra_output is not None:
								print(f'skipping {platform_name} {version_number} {input_blockstate}. Needs more data')
								continue

							# blockstate to universal
							try:
								universal_output2, extra_output, extra_needed = numerical_version.to_universal(None, numerical_output)
							except:
								print(f'error from universal to blockstate {platform_name} {version_number}')
								print(f'Blockstate input: {input_blockstate}')
								print(f'Universal output: {universal_output}')
								print(f'Numerical output: {numerical_output}')
								continue
							if extra_needed or extra_output is not None:
								print(f'skipping {platform_name} {version_number} {input_blockstate}. Needs more data')
								continue
						else:
							numerical_output = None
							universal_output2 = universal_output

						# universal to numerical
						try:
							back_out, extra_output, extra_needed = blockstate_version.from_universal(None, universal_output2)
						except:
							print(f'error from universal {platform_name} {version_number}')
							print(f'Blockstate input: {input_blockstate}')
							print(f'Universal output: {universal_output}')
							print(f'Numerical output: {numerical_output}')
							print(f'Universal output 2: {universal_output2}')
							continue
						if str(input_blockstate) != str(back_out):
							print(f"Conversion error: {input_blockstate} != {back_out} {platform_name} {version_number}")
							print(f'Universal output: {universal_output}')
							print(f'Numerical output: {numerical_output}')
							print(f'Universal output 2: {universal_output2}')
							print(f'Blockstate: {back_out}')

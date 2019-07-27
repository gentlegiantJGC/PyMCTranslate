from reader.data_version_handler import VersionContainer, Block
import itertools
import os

if __name__ == '__main__':
	block_mappings = VersionContainer(r'..\mappings')
	if not os.path.isdir('logs'):
		os.makedirs('logs')
	for platform_name in block_mappings.platforms:
		for version_number in block_mappings.version_numbers(platform_name):
			version = block_mappings.get(platform_name, version_number)
			if not version.block_format == 'pseudo-numerical':
				print(f'skipping {platform_name} {version_number}. Not pseudo-numerical format')
				continue
			input_version = version.get()
			blocks = open(f'logs/{platform_name}_{version_number}.txt', 'w')
			for namespace_str in input_version.namespaces:
				for block_name in input_version.block_names(namespace_str):
					block_specification = input_version.get_specification('block', namespace_str, block_name)
					properties = block_specification.get('properties', {})
					keys, values = zip(*properties.items())
					blocks.write(f'{namespace_str}:{block_name}\n')
					for spec_ in itertools.product(*values):
						spec = dict(zip(keys, spec_))
						try:
							output, extra_output, extra_needed = input_version.to_universal(None, Block(None, namespace_str, block_name, spec))
						except:
							output = extra_output = None
							print({'block_name': f'{namespace_str}:{block_name}', 'properties': spec})
							continue
						blocks.write(f'{output}, {extra_output}\n')
					blocks.write('\n')
			blocks.close()

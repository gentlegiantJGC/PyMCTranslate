import PyMCTranslate
from PyMCTranslate import Block
translations = PyMCTranslate.new_translation_manager()

print('==== bedrock_1_7_0 ====')
for data in range(16):
	print(
		translations.get_sub_version('bedrock', (1, 7, 0)).to_universal(Block(None, 'minecraft', 'log', {'block_data': str(data)}))[0]
	)
print('==== java_1_12_2 ====')
for data in range(16):
	print(
		translations.get_sub_version('java', (1, 12, 2)).to_universal(Block(None, 'minecraft', 'log', {'block_data': str(data)}))[0]
	)

import PyMCTranslate
from PyMCTranslate.py3.translation_manager import SubVersion

try:
    from amulet.api.block import Block
except ImportError:
    from PyMCTranslate.py3.api.block import Block

translations = PyMCTranslate.new_translation_manager()


def get_version(platform: str, version: str, force_blockstate) -> SubVersion:
    assert platform in translations.platforms(), f'Platform {platform} is not valid. Must be one of {translations.platforms()}'
    version = tuple(int(i) for i in version.split('.'))
    force_blockstate = bool(force_blockstate)
    return translations.get_sub_version(platform, version, force_blockstate)


print('Example command: "java 1.12.2 false bedrock 1.13.0 false minecraft:trapdoor[facing=south,half=top,open=false]"')

while True:
    user_input = input('type command ("n" to escape): ')
    if user_input == 'n':
        break
    user_input = user_input.split(' ')
    if not len(user_input) == 7:
        print('command format is incorrect')
        continue
    input_platform, input_version, input_force_blockstate, output_platform, output_version, output_force_blockstate, blockstate = user_input
    inp = get_version(input_platform, input_version, input_force_blockstate)
    out = get_version(output_platform, output_version, output_force_blockstate)
    block = Block(blockstate=blockstate)
    print(f'\tInput block {block}')
    ublock = inp.to_universal(block)[0]
    print(f'\tUniveral block {ublock}')
    outblock = out.from_universal(ublock)
    print(f'\tOutput block {outblock}')

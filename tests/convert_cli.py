import PyMCTranslate
from PyMCTranslate import Version, Block

translations = PyMCTranslate.new_translation_manager()


def get_version(platform: str, version: str) -> Version:
    assert platform in translations.platforms(), f'Platform {platform} is not valid. Must be one of {translations.platforms()}'
    version = tuple(int(i) for i in version.split('.'))
    return translations.get_version(platform, version)


print('Example command: "java 1.12.2 false bedrock 1.13.0 false minecraft:double_stone_slab[block_data=0]"')
print('Example command: "java 1.12.2 true bedrock 1.13.0 false minecraft:trapdoor[facing=south,half=top,open=false]"')

while True:
    user_input = input('type command ("n" to escape): ')
    if user_input == 'n':
        break
    user_input = user_input.split(' ')
    if not len(user_input) == 7:
        print('command format is incorrect')
        continue
    input_platform, input_version, input_force_blockstate, output_platform, output_version, output_force_blockstate, blockstate = user_input
    input_force_blockstate = input_force_blockstate.lower() == 'true'
    output_force_blockstate = output_force_blockstate.lower() == 'true'
    inp = get_version(input_platform, input_version)
    out = get_version(output_platform, output_version)
    block = Block(*Block.parse_blockstate_string(blockstate))
    print(f'\tInput block {block}')
    ublock = inp.block.to_universal(block, force_blockstate=input_force_blockstate)[0]
    print(f'\tUniveral block {ublock}')
    outblock = out.block.from_universal(ublock, force_blockstate=output_force_blockstate)
    print(f'\tOutput block {outblock}')

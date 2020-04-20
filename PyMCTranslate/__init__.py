import os

try:
    from amulet.api.block import Block
    from amulet.api.block_entity import BlockEntity
    from amulet.api.entity import Entity
    from amulet.api.item import Item, BlockItem
    from amulet.api.errors import ChunkLoadError
except ModuleNotFoundError:
    from PyMCTranslate.py3.amulet_objects.block import Block
    from PyMCTranslate.py3.amulet_objects.block_entity import BlockEntity
    from PyMCTranslate.py3.amulet_objects.entity import Entity
    from PyMCTranslate.py3.amulet_objects.item import Item, BlockItem
    from PyMCTranslate.py3.amulet_objects.errors import ChunkLoadError

from PyMCTranslate.py3.util import load_json_gz

pymct_dir = os.path.dirname(__file__)
try:
    with open(os.path.join(pymct_dir, 'build_number')) as f:
        build_number = int(f.read())
except:
    build_number = -1

from PyMCTranslate.py3.log import log

# have the json files been minified
minified = os.path.isdir(os.path.join(pymct_dir, 'min_json'))
if minified:
    """
    minified format
    min_json
        atlas.json.gz
        versions
            <version>
                meta.json.gz
                block.json.gz
                item.json.gz
                entity.json.gz
    """
    # load the mega_json file and unpack
    json_atlas: list = load_json_gz(os.path.join(pymct_dir, 'min_json', 'atlas.json.gz'))
    json_dir = os.path.join(pymct_dir, 'min_json')
else:
    """
    maximised format
    min_json
        versions
            <version>
                __init__.json
                <other meta files>
                block/item/entity
                    <block format>
                        <operation>
                            <namespace>
                                <group_name>
                                    <base_name>.json
    """
    json_atlas = None
    json_dir = os.path.join(pymct_dir, 'json')

from PyMCTranslate.py3.translation_manager import TranslationManager
from PyMCTranslate.py3.versions import Version
from PyMCTranslate.py3 import raw_text


def new_translation_manager() -> TranslationManager:
    """Returns a new TranslationManager with the default files.
    Each unique world should have a new TranslationManager because there is the
    functionality to register custom (mod) blocks making each handler unique."""
    return TranslationManager(json_dir)

import os
from typing import Optional

from PyMCTranslate.py3.util.json_gz import load_json_gz

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
    json_atlas: Optional[list] = load_json_gz(os.path.join(pymct_dir, 'min_json', 'atlas.json.gz'))
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

from PyMCTranslate.py3.api.translation_manager import TranslationManager
from PyMCTranslate.py3.api.version import Version


def new_translation_manager() -> TranslationManager:
    """Returns a new TranslationManager with the default files.
    Each unique world should have a new TranslationManager because there is the
    functionality to register custom (mod) blocks making each handler unique."""
    return TranslationManager(json_dir)

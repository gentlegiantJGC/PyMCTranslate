import os

try:
    from amulet.api.block import Block
    from amulet.api.block_entity import BlockEntity
    from amulet.api.entity import Entity
    from amulet.api.errors import ChunkLoadError
except ModuleNotFoundError:
    from PyMCTranslate.py3.amulet_objects.block import Block
    from PyMCTranslate.py3.amulet_objects.block_entity import BlockEntity
    from PyMCTranslate.py3.amulet_objects.entity import Entity
    from PyMCTranslate.py3.amulet_objects.errors import ChunkLoadError

from PyMCTranslate.py3.translation_manager import TranslationManager
from PyMCTranslate.py3.versions import Version, SubVersion
from PyMCTranslate.py3 import raw_text


def new_translation_manager() -> TranslationManager:
    """Returns a new TranslationManager with the default files.
    Each unique world should have a new TranslationManager because there is the
    functionality to register custom (mod) blocks making each handler unique."""
    return TranslationManager(os.path.join(os.path.dirname(__file__), 'json'))

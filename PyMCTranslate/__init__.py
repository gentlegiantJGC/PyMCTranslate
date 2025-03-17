from .py3 import (
    new_translation_manager,
    TranslationManager,
    Version,
    BlockTranslator,
    EntityTranslator,
    ItemTranslator,
    build_number,
)

from . import _version

__version__ = _version.get_versions()["version"]

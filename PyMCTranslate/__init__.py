from .py3 import (
    new_translation_manager,
    TranslationManager,
    Version,
    BlockTranslator,
    EntityTranslator,
    ItemTranslator,
    build_number,
)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

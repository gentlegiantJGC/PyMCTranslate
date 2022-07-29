import logging
from PyMCTranslate.py3.api import (
    TranslationManager,
    Version,
    BlockTranslator,
    EntityTranslator,
    ItemTranslator,
)
from PyMCTranslate.py3.meta import (
    pymct_dir,
    json_dir,
    json_atlas,
    minified,
    build_number,
)


def new_translation_manager() -> TranslationManager:
    """Returns a new TranslationManager with the default files.
    Each unique world should have a new TranslationManager because there is the
    functionality to register custom (mod) blocks making each handler unique."""
    return TranslationManager(json_dir)


# init a default logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

_log = logging.getLogger(__name__)
_log.info(f"PyMCTranslate Version {build_number}")

import os
from .py3.translation_handler import TranslationManager


def new_translation_handler() -> TranslationManager:
	"""Returns a new TranslationManager with the default files.
	Each unique world should have a new TranslationManager because there is the
	functionality to register custom (mod) blocks making each handler unique."""
	return TranslationManager(os.path.join(os.path.dirname(__file__), 'mappings'))

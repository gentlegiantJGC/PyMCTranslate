import os
from .py3.translation_handler import TranslationHandler


def new_translation_handler() -> TranslationHandler:
	"""Returns a new TranslationHandler with the default files.
	Each unique world should have a new TranslationHandler because there is the
	functionality to register custom (mod) blocks making each handler unique."""
	return TranslationHandler(os.path.join(os.path.dirname(__file__), 'mappings'))

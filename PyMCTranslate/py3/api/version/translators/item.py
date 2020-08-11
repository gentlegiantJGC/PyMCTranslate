from typing import Tuple, Union, TYPE_CHECKING

from PyMCTranslate.py3.api import Item, BlockItem
from .base import BaseTranslator

if TYPE_CHECKING:
    from PyMCTranslate.py3.api.version import Version
    from PyMCTranslate.py3.api.translation_manager import TranslationManager

BlockCoordinates = Tuple[int, int, int]


class ItemTranslator(BaseTranslator):
    def __init__(
        self,
        translation_manager: "TranslationManager",
        parent_version: "Version",
        database: dict,
        *_
    ):
        super().__init__(translation_manager, parent_version, database, "item")

    def to_universal(
        self, object_input: Union[Item, BlockItem]
    ) -> Union[Item, BlockItem]:
        raise NotImplementedError

    def from_universal(
        self, object_input: Union[Item, BlockItem]
    ) -> Union[Item, BlockItem]:
        raise NotImplementedError

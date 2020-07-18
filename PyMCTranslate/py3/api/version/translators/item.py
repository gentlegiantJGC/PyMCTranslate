from typing import Tuple, Union, TYPE_CHECKING

from PyMCTranslate.py3.api import Item, BlockItem
from .base import BaseTranslator

if TYPE_CHECKING:
    from ..version import Version

BlockCoordinates = Tuple[int, int, int]


class ItemTranslator(BaseTranslator):
    def __init__(
        self, parent_version: "Version", universal_format: "Version", database: dict
    ):
        super().__init__(parent_version, universal_format, database, "item")

    def to_universal(
        self, object_input: Union[Item, BlockItem]
    ) -> Union[Item, BlockItem]:
        raise NotImplementedError

    def from_universal(
        self, object_input: Union[Item, BlockItem]
    ) -> Union[Item, BlockItem]:
        raise NotImplementedError

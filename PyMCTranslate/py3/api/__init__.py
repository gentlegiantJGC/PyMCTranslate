from __future__ import annotations

try:
    from amulet.api.block import Block
    from amulet.api.block_entity import BlockEntity
    from amulet.api.entity import Entity
    from amulet.api.item import Item, BlockItem
    from amulet.api.errors import ChunkLoadError
except ModuleNotFoundError:
    from PyMCTranslate.py3.api.amulet_objects import (
        Block,
        BlockEntity,
        Entity,
        Item,
        BlockItem,
        ChunkLoadError,
    )

from .translation_manager import TranslationManager
from .version import Version, BlockTranslator, EntityTranslator, ItemTranslator

from typing import Tuple, Union, Callable, TYPE_CHECKING, Optional

from PyMCTranslate.py3.api import Block, BlockEntity, Entity
from PyMCTranslate.py3.log import log
from .base import BaseTranslator

if TYPE_CHECKING:
    from ..version import Version

BlockCoordinates = Tuple[int, int, int]


class BlockTranslator(BaseTranslator):
    def __init__(
            self, parent_version: "Version", universal_format: "Version", database: dict
    ):
        super().__init__(parent_version, universal_format, database, "block")
        self._cache = {  # only blocks without a block entity can be cached
            ("to_universal", False): {},
            ("to_universal", True): {},
            ("from_universal", False): {},
            ("from_universal", True): {},
        }

    def to_universal(
            self,
            block: "Block",
            block_entity: "BlockEntity" = None,
            force_blockstate: bool = False,
            block_location: BlockCoordinates = (0, 0, 0),
            get_block_callback: Callable[
                [Tuple[int, int, int]], Tuple[Block, Optional[BlockEntity]]
            ] = None,
    ) -> Tuple[Block, Optional[BlockEntity], bool]:
        """
        Translate the given Block object and optional BlockEntity from the parent Version's format to the Universal format.

        :param block: The block to translate
        :param block_entity: An optional block entity related to the block input
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same)
        :param block_location: The location of the block in the world
        :param get_block_callback: A callable with relative coordinates that returns a Block and optional BlockEntity
        :return: A Block, optional BlockEntity and a bool. The bool specifies if block_location and get_block_callback are required to fully define the output data.
        """
        assert isinstance(block, Block), "Input object must be a block"
        cache_key = ("to_universal", force_blockstate)
        if block_entity is None:
            if block in self._cache[cache_key]:
                return self._cache[cache_key][block]
        else:
            assert isinstance(
                block_entity, BlockEntity
            ), "extra_input must be None or a BlockEntity"

        try:
            input_spec = self.get_specification(
                block.namespace, block.base_name, force_blockstate
            )
            mapping = self.get_mapping_to_universal(
                block.namespace, block.base_name, force_blockstate
            )
        except KeyError:
            log.warning(
                f"Could not find translation information for {self._mode} {block} to universal in {self._parent_version}. If this is not a vanilla block ignore this message"
            )
            return block, block_entity, False

        output, extra_output, extra_needed, cacheable = self._translate(
            block,
            input_spec,
            mapping,
            self._universal_format,
            True,
            "to universal",
            get_block_callback,
            block_entity,
            block_location,
        )

        if cacheable:
            self._cache[cache_key][block] = output, extra_output, extra_needed

        return output, extra_output, extra_needed

    def from_universal(
            self,
            block: "Block",
            block_entity: "BlockEntity" = None,
            force_blockstate: bool = False,
            block_location: BlockCoordinates = (0, 0, 0),
            get_block_callback: Callable[
                [Tuple[int, int, int]], Tuple[Block, Union[None, BlockEntity]]
            ] = None,
    ) -> Union[
        Tuple[Block, Optional[BlockEntity], bool],
        Tuple[Entity, None, bool],
    ]:
        """
        Translate the given Block object from the Universal format to the parent Version's format.

        :param block: The block to translate
        :param block_entity: An optional block entity related to the block input
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same)
        :param block_location: The location of the block in the world
        :param get_block_callback: A callable with relative coordinates that returns a Block and optional BlockEntity
        :return: There are two formats that can be returned. The first is a Block, optional BlockEntity and a bool. The second is an Entity, None and a bool.
        The bool specifies if block_location and get_block_callback are required to fully define the output data.
        """
        assert isinstance(block, Block), "Input object must be a block"
        cache_key = ("from_universal", force_blockstate)
        if block_entity is None:
            if block in self._cache[cache_key]:
                return self._cache[cache_key][block]
        else:
            assert isinstance(
                block_entity, BlockEntity
            ), "extra_input must be None or a BlockEntity"

        try:
            input_spec = self._universal_format.block.get_specification(
                block.namespace, block.base_name
            )
            mapping = self.get_mapping_from_universal(
                block.namespace, block.base_name, force_blockstate
            )
        except KeyError:
            if block.namespace == "minecraft" and list(
                    block.properties.keys()
            ) == ["block_data"]:
                log.debug(
                    f"Probably just a quirk block {block} from universal in {self._parent_version}."
                )
            else:
                log.warning(
                    f"Could not find translation information for {self._mode} {block} from universal in {self._parent_version}. If this is not a vanilla block ignore this message"
                )
            return block, block_entity, False

        output, extra_output, extra_needed, cacheable = self._translate(
            block,
            input_spec,
            mapping,
            self._parent_version,
            force_blockstate,
            "from_universal",
            get_block_callback,
            block_entity,
            block_location,
        )

        if cacheable:
            self._cache[cache_key][block] = output, extra_output, extra_needed

        return output, extra_output, extra_needed

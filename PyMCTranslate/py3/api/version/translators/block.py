from typing import Tuple, Union, Callable, TYPE_CHECKING

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
        object_input: "Block",
        get_block_callback: Callable[
            [Tuple[int, int, int]], Tuple[Block, Union[None, BlockEntity]]
        ] = None,
        force_blockstate: bool = False,
        extra_input: "BlockEntity" = None,
        block_location: BlockCoordinates = (0, 0, 0),
    ) -> Union[Tuple[Block, None, bool], Tuple[Block, BlockEntity, bool]]:
        """
        A method to translate a given Block object to the Universal format.

        :param object_input: The object to translate
        :param get_block_callback: A callable with relative coordinates that returns a Block and optional BlockEntity
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same thing)
        :param extra_input: secondary to the object_input a block entity can be given. This should only be used in the select block tool or plugins. Not compatible with location
        :param block_location
        :return: output, extra_output, extra_needed
            output - a Block or Entity instance
            extra_output - None or BlockEntity if there is a BlockEntity to return (only if output is Block)
            extra_needed - bool specifying if the location is needed to fully define the output
        """
        assert isinstance(object_input, Block), "Input object must be a block"
        cache_key = ("to_universal", force_blockstate)
        if extra_input is None:
            if object_input in self._cache[cache_key]:
                return self._cache[cache_key][object_input]
        else:
            assert isinstance(
                extra_input, BlockEntity
            ), "extra_input must be None or a BlockEntity"

        try:
            input_spec = self.get_specification(
                object_input.namespace, object_input.base_name, force_blockstate
            )
            mapping = self.get_mapping_to_universal(
                object_input.namespace, object_input.base_name, force_blockstate
            )
        except KeyError:
            log.warning(
                f"Could not find translation information for {self._mode} {object_input} to universal in {self._parent_version}. If this is not a vanilla block ignore this message"
            )
            return object_input, extra_input, False

        output, extra_output, extra_needed, cacheable = self._translate(
            object_input,
            input_spec,
            mapping,
            self._universal_format,
            True,
            "to universal",
            get_block_callback,
            extra_input,
            block_location,
        )

        if cacheable:
            self._cache[cache_key][object_input] = output, extra_output, extra_needed

        return output, extra_output, extra_needed

    def from_universal(
        self,
        object_input: "Block",
        get_block_callback: Callable[
            [Tuple[int, int, int]], Tuple[Block, Union[None, BlockEntity]]
        ] = None,
        force_blockstate: bool = False,
        extra_input: "BlockEntity" = None,
        block_location: BlockCoordinates = (0, 0, 0),
    ) -> Union[
        Tuple[Block, None, bool],
        Tuple[Block, BlockEntity, bool],
        Tuple[Entity, None, bool],
    ]:
        """
        A method to translate a given Block or Entity object from the Universal format to the format of this class instance.

        :param object_input: The object to translate
        :param get_block_callback: A callable with relative coordinates that returns a Block and optional BlockEntity
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same thing)
        :param extra_input: secondary to the object_input a block entity can be given. This should only be used in the select block tool or plugins. Not compatible with location
        :param block_location:
        :return: output, extra_output, extra_needed
            output - a Block or Entity instance
            extra_output - None or BlockEntity if there is a BlockEntity to return (only if output is Block)
            extra_needed - bool specifying if the location is needed to fully define the output
        """
        assert isinstance(object_input, Block), "Input object must be a block"
        cache_key = ("from_universal", force_blockstate)
        if extra_input is None:
            if object_input in self._cache[cache_key]:
                return self._cache[cache_key][object_input]
        else:
            assert isinstance(
                extra_input, BlockEntity
            ), "extra_input must be None or a BlockEntity"

        try:
            input_spec = self._universal_format.block.get_specification(
                object_input.namespace, object_input.base_name
            )
            mapping = self.get_mapping_from_universal(
                object_input.namespace, object_input.base_name, force_blockstate
            )
        except KeyError:
            if object_input.namespace == "minecraft" and list(
                object_input.properties.keys()
            ) == ["block_data"]:
                log.debug(
                    f"Probably just a quirk block {object_input} from universal in {self._parent_version}."
                )
            else:
                log.warning(
                    f"Could not find translation information for {self._mode} {object_input} from universal in {self._parent_version}. If this is not a vanilla block ignore this message"
                )
            return object_input, extra_input, False

        output, extra_output, extra_needed, cacheable = self._translate(
            object_input,
            input_spec,
            mapping,
            self._parent_version,
            force_blockstate,
            "from_universal",
            get_block_callback,
            extra_input,
            block_location,
        )

        if cacheable:
            self._cache[cache_key][object_input] = output, extra_output, extra_needed

        return output, extra_output, extra_needed

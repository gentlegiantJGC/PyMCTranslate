from typing import Tuple, Union, TYPE_CHECKING

from PyMCTranslate.py3.api import Block, BlockEntity, Entity
from PyMCTranslate.py3.log import log
from .base import BaseTranslator

if TYPE_CHECKING:
    from ..version import Version

BlockCoordinates = Tuple[int, int, int]


class EntityTranslator(BaseTranslator):
    def __init__(
        self, parent_version: "Version", universal_format: "Version", database: dict
    ):
        super().__init__(parent_version, universal_format, database, "entity")

    def to_universal(
        self, object_input: "Entity", force_blockstate: bool = False
    ) -> Union[Tuple[Block, None], Tuple[Block, BlockEntity], Tuple[Entity, None]]:
        """
        A method to translate a given Entity object to the Universal format.

        :param object_input: The object to translate
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same thing)
        :return: output, extra_output, extra_needed
            output - a Block or Entity instance
            extra_output - None or BlockEntity if there is a BlockEntity to return (only if output is Block)
        """
        assert isinstance(object_input, Entity), "Input object must be an entity"

        try:
            input_spec = self.get_specification(
                object_input.namespace, object_input.base_name, force_blockstate
            )
            mapping = self.get_mapping_to_universal(
                object_input.namespace, object_input.base_name, force_blockstate
            )
        except KeyError:
            log.warning(
                f"Could not find translation information for {self._mode} {object_input} to universal in {self._parent_version}. If this is not a vanilla entity ignore this message"
            )
            return object_input, None

        output, extra_output, extra_needed, cacheable = self._translate(
            object_input,
            input_spec,
            mapping,
            self._universal_format,
            True,
            "to universal",
        )

        return output, extra_output

    def from_universal(
        self, object_input: "Entity", force_blockstate: bool = False
    ) -> Entity:
        """
        A method to translate a given Entity object from the Universal format to the format of this class instance.

        :param object_input: The object to translate
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same thing)
        :return: output, extra_output, extra_needed
            output - a Block or Entity instance
            extra_output - None or BlockEntity if there is a BlockEntity to return (only if output is Block)
            extra_needed - bool specifying if the location is needed to fully define the output
        """
        assert isinstance(object_input, Entity), "Input object must be a block"

        try:
            input_spec = self._universal_format.entity.get_specification(
                object_input.namespace, object_input.base_name
            )
            mapping = self.get_mapping_from_universal(
                object_input.namespace, object_input.base_name, force_blockstate
            )
        except KeyError:
            log.warning(
                f"Could not find translation information for {self._mode} {object_input} from universal in {self._parent_version}. If this is not a vanilla entity ignore this message"
            )
            return object_input

        output, _, _, _ = self._translate(
            object_input,
            input_spec,
            mapping,
            self._parent_version,
            force_blockstate,
            "from_universal",
        )

        return output

from typing import Tuple, TYPE_CHECKING, Optional, Union

from PyMCTranslate.py3.api import Entity, Block, BlockEntity
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
            self,
            entity: "Entity",
            force_blockstate: bool = False
    ) -> Entity:
        """
        A method to translate a given Entity object to the Universal format.

        :param entity: The entity to translate
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same)
        :return: The translated Entity
        """
        assert isinstance(entity, Entity), "entity must be an Entity instance"

        try:
            input_spec = self.get_specification(
                entity.namespace, entity.base_name, force_blockstate
            )
            mapping = self.get_mapping_to_universal(
                entity.namespace, entity.base_name, force_blockstate
            )
        except KeyError:
            log.warning(
                f"Could not find translation information for {self._mode} {entity} to universal in {self._parent_version}. If this is not a vanilla entity ignore this message"
            )
            return entity

        output, _, _, _ = self._translate(
            entity,
            input_spec,
            mapping,
            self._universal_format,
            True,
            "to universal",
        )

        return output

    def from_universal(
            self,
            entity: "Entity",
            force_blockstate: bool = False
    ) -> Union[Tuple[Block, Optional[BlockEntity]], Tuple[Entity, None]]:
        """
        A method to translate a given Entity object from the Universal format to the format of this class instance.

        :param entity: The entity to translate
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same)
        :return: There are two formats that can be returned. The first is a Block and an optional BlockEntity. The second is an Entity and None.
        """
        assert isinstance(entity, Entity), "entity must be an Entity instance"

        try:
            input_spec = self._universal_format.entity.get_specification(
                entity.namespace, entity.base_name
            )
            mapping = self.get_mapping_from_universal(
                entity.namespace, entity.base_name, force_blockstate
            )
        except KeyError:
            log.warning(
                f"Could not find translation information for {self._mode} {entity} from universal in {self._parent_version}. If this is not a vanilla entity ignore this message"
            )
            return entity, None

        output, extra_output, _, _ = self._translate(
            entity,
            input_spec,
            mapping,
            self._parent_version,
            force_blockstate,
            "from_universal",
        )

        return output, extra_output

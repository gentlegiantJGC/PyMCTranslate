from typing import Tuple, TYPE_CHECKING, Optional, Union, Dict, Any
import copy
import logging

import amulet_nbt
from PyMCTranslate.py3.api import Entity, Block, BlockEntity
from .base import BaseTranslator, BaseSpecification

if TYPE_CHECKING:
    from PyMCTranslate.py3.api.version import Version
    from PyMCTranslate.py3.api.translation_manager import TranslationManager

log = logging.getLogger(__name__)

BlockCoordinates = Tuple[int, int, int]
NotInit = object()


class EntitySpecification(BaseSpecification):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self._default_properties = NotInit
        self._valid_properties = NotInit
        self._nbt_identifier = NotInit
        self._default_nbt = NotInit

    @property
    def nbt_identifier(self) -> Optional[Tuple[str, str]]:
        if self._nbt_identifier is NotInit:
            self._nbt_identifier = self.get("nbt_identifier", None)
        return self._nbt_identifier

    @property
    def default_nbt(self) -> Optional[amulet_nbt.TAG_Compound]:
        if self._default_nbt is NotInit:
            snbt = self.get("snbt", None)
            if isinstance(snbt, str):
                nbt = amulet_nbt.from_snbt(snbt)
            else:
                nbt = None
            self._default_nbt = nbt
        return self._default_nbt


class EntityTranslator(BaseTranslator):
    def __init__(
        self,
        translation_manager: "TranslationManager",
        parent_version: "Version",
        database: dict,
        *_,
    ):
        super().__init__(translation_manager, parent_version, database, "entity")

    def get_specification(
        self, namespace: str, base_name: str, force_blockstate: bool = False
    ) -> EntitySpecification:
        return EntitySpecification(self._get_raw_specification(namespace, base_name))

    def to_universal(self, entity: "Entity", force_blockstate: bool = False) -> Entity:
        """
        A method to translate a given Entity object to the Universal format.

        :param entity: The entity to translate
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same)
        :return: The translated Entity
        """
        assert isinstance(entity, Entity), "entity must be an Entity instance"

        try:
            input_spec = self._get_raw_specification(
                entity.namespace, entity.base_name, force_blockstate
            )
            mapping = self.get_mapping_to_universal(
                entity.namespace, entity.base_name, force_blockstate
            )
        except KeyError:
            log.warning(
                f"Could not find translation information for {self._mode} {entity} to universal in {self._parent_version}. If this is not a vanilla entity ignore this message"
            )
            return copy.deepcopy(entity)

        output, _, _, _ = self._translate(
            copy.deepcopy(entity),
            input_spec,
            mapping,
            self._universal_format,
            True,
            "to universal",
        )

        return output

    def from_universal(
        self, entity: "Entity", force_blockstate: bool = False
    ) -> Union[Tuple[Block, Optional[BlockEntity]], Tuple[Entity, None]]:
        """
        A method to translate a given Entity object from the Universal format to the format of this class instance.

        :param entity: The entity to translate
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same)
        :return: There are two formats that can be returned. The first is a Block and an optional BlockEntity. The second is an Entity and None.
        """
        assert isinstance(entity, Entity), "entity must be an Entity instance"

        try:
            input_spec = self._universal_format.entity._get_raw_specification(
                entity.namespace, entity.base_name
            )
            mapping = self.get_mapping_from_universal(
                entity.namespace, entity.base_name, force_blockstate
            )
        except KeyError:
            log.warning(
                f"Could not find translation information for {self._mode} {entity} from universal in {self._parent_version}. If this is not a vanilla entity ignore this message"
            )
            return copy.deepcopy(entity), None

        output, extra_output, _, _ = self._translate(
            copy.deepcopy(entity),
            input_spec,
            mapping,
            self._parent_version,
            force_blockstate,
            "from_universal",
        )

        return output, extra_output

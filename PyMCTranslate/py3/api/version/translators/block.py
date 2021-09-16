from typing import Tuple, Union, Callable, TYPE_CHECKING, Optional, Dict, Any
import copy

import amulet_nbt

from PyMCTranslate.py3.api import Block, BlockEntity, Entity
from PyMCTranslate.py3.log import log
from .base import BaseTranslator, BaseSpecification

if TYPE_CHECKING:
    from PyMCTranslate.py3.api.version import Version
    from PyMCTranslate.py3.api.translation_manager import TranslationManager

BlockCoordinates = Tuple[int, int, int]
NotInit = object()


class BlockSpecification(BaseSpecification):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self._default_properties = NotInit
        self._valid_properties = NotInit
        self._nbt_identifier = NotInit
        self._default_nbt = NotInit

    @property
    def default_properties(self) -> Dict[str, amulet_nbt.AnyNBT]:
        if self._default_properties is NotInit:
            self._default_properties = {key: amulet_nbt.from_snbt(val) for key, val in self.get("defaults", {}).items()}
        return self._default_properties

    @property
    def valid_properties(self) -> Dict[str, Tuple[amulet_nbt.AnyNBT]]:
        if self._valid_properties is NotInit:
            self._valid_properties = {
                key: tuple(amulet_nbt.from_snbt(val) for val in vals)
                for key, vals in self.get("properties", {}).items()
            }
        return self._valid_properties

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


class BlockTranslator(BaseTranslator):
    def __init__(
        self,
        translation_manager: "TranslationManager",
        parent_version: "Version",
        database: dict,
        raw_numerical_block_map: Dict[str, int],
        waterloggable,
        always_waterlogged,
        block_format,
        *_,
    ):
        super().__init__(translation_manager, parent_version, database, "block")
        self._cache = {  # only blocks without a block entity can be cached
            ("to_universal", False): {},
            ("to_universal", True): {},
            ("from_universal", False): {},
            ("from_universal", True): {},
        }
        self._block_format = block_format

        if parent_version.has_abstract_format:
            self._numerical_block_map_inverse: Dict[Tuple[str, str], int] = {
                tuple(block_str.split(":", 1)): block_id
                for block_str, block_id in raw_numerical_block_map.items()
                if isinstance(block_str, str)
                and ":" in block_str
                and isinstance(block_id, int)
            }
            self._numerical_block_map: Dict[int, Tuple[str, str]] = {
                val: key for key, val in self._numerical_block_map_inverse.items()
            }
        else:
            self._numerical_block_map: Dict[int, Tuple[str, str]] = {}
            self._numerical_block_map_inverse: Dict[Tuple[str, str], int] = {}

        self._waterloggable = None
        self._always_waterlogged = None

        if waterloggable:
            self._waterloggable = set(waterloggable)
        if always_waterlogged:
            self._always_waterlogged = set(always_waterlogged)

    @property
    def block_format(self) -> str:
        """
        The native format of the blocks for this game version.

        This will be one of "numerical", "pseudo-numerical", "blockstate" or "nbt-blockstate".

         "numerical" is the old storage format where both block id and data value were numerical values.

         "pseudo-numerical" is the in-between Bedrock format where block ids were namespaced strings but data was still numerical.

         "blockstate" is the new Java format where the block ids are all namespaced strings and the data is stored as properties in NBT.TAG_String format.

         "nbt-blockstate" is the new Bedrock format where the block ids are all namespaced strings and the data is stored as properties in various NBT types.

        """
        return self._block_format

    # TODO: consider moving these to the block translator
    def is_waterloggable(self, namespace_str: str, always=False):
        """
        A method to check if a block can be waterlogged.
        This method is only valid for Java blockstate format worlds,
        Other formats either don't have waterlogged blocks or don't have a limit on what can be stacked.

        :param namespace_str: "<namespace>:<base_name>"
        :param always: True to check if the block does not have a waterlogged property but is always waterlogged. eg: seagrass
        :return: Bool. True if it can be waterlogged. False if not or another format.
        """
        if always:
            if isinstance(self._always_waterlogged, set):
                return namespace_str in self._always_waterlogged
        else:
            if isinstance(self._waterloggable, set):
                return namespace_str in self._waterloggable
        return False

    def ints_to_block(self, block_id: int, block_data: int) -> "Block":
        if block_id in self._translation_manager.block_registry:
            (
                namespace,
                base_name,
            ) = self._translation_manager.block_registry.private_to_str(block_id).split(
                ":", 1
            )
        elif block_id in self._numerical_block_map:
            namespace, base_name = self._numerical_block_map[block_id]
        else:
            return Block(
                namespace="minecraft",
                base_name="numerical",
                properties={
                    "block_id": amulet_nbt.TAG_Int(block_id),
                    "block_data": amulet_nbt.TAG_Int(block_data),
                },
            )

        return Block(
            namespace=namespace,
            base_name=base_name,
            properties={"block_data": amulet_nbt.TAG_Int(block_data)},
        )

    def block_to_ints(self, block: "Block") -> Union[None, Tuple[int, int]]:
        block_id = None
        block_data = None
        block_tuple = (block.namespace, block.base_name)
        if block.namespaced_name in self._translation_manager.block_registry:
            block_id = self._translation_manager.block_registry.private_to_int(
                block.namespaced_name
            )
        elif block_tuple in self._numerical_block_map_inverse:
            block_id = self._numerical_block_map_inverse[block_tuple]
        elif (
            block_tuple == ("minecraft", "numerical")
            and "block_id" in block.properties
            and isinstance(block.properties["block_id"], amulet_nbt.TAG_Int)
        ):
            block_id = block.properties["block_id"].value

        if "block_data" in block.properties and isinstance(
            block.properties["block_data"], amulet_nbt.TAG_Int
        ):
            block_data = block.properties["block_data"].value

        if block_id is not None and block_data is not None:
            return block_id, block_data

    def get_specification(
        self, namespace: str, base_name: str, force_blockstate: bool = False
    ) -> BlockSpecification:
        return BlockSpecification(self._get_raw_specification(namespace, base_name, force_blockstate))

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
        assert isinstance(block, Block), "block must be a Block instance"
        cache_key = ("to_universal", force_blockstate)
        if block_entity is None:
            if block in self._cache[cache_key]:
                output, extra_output, extra_needed = self._cache[cache_key][block]
                extra_output = copy.deepcopy(extra_output)
                return output, extra_output, extra_needed
        else:
            assert isinstance(
                block_entity, BlockEntity
            ), "extra_input must be None or a BlockEntity"
            block_entity = copy.deepcopy(block_entity)

        try:
            input_spec = self._get_raw_specification(
                block.namespace, block.base_name, force_blockstate
            )
            mapping = self.get_mapping_to_universal(
                block.namespace, block.base_name, force_blockstate
            )
        except KeyError:
            if self._parent_version.platform != "universal":
                self._warn_once(
                    (block,),
                    "Could not find translation information for {} {} to universal in {}. If this is not a vanilla block ignore this message",
                    self._mode,
                    block,
                    self._parent_version,
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

        return output, copy.deepcopy(extra_output), extra_needed

    def from_universal(
        self,
        block: "Block",
        block_entity: "BlockEntity" = None,
        force_blockstate: bool = False,
        block_location: BlockCoordinates = (0, 0, 0),
        get_block_callback: Callable[
            [Tuple[int, int, int]], Tuple[Block, Union[None, BlockEntity]]
        ] = None,
    ) -> Union[Tuple[Block, Optional[BlockEntity], bool], Tuple[Entity, None, bool],]:
        """
        Translate the given Block object from the Universal format to the parent Version's format.

        :param block: The block to translate
        :param block_entity: An optional block entity related to the block input
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same)
        :param block_location: The location of the block in the world
        :param get_block_callback: A callable with relative coordinates that returns a Block and optional BlockEntity
        :return: There are two formats that can be returned. The first is a Block, optional BlockEntity and a bool. The second is an Entity, None and a bool. The bool specifies if block_location and get_block_callback are required to fully define the output data.
        """
        assert isinstance(block, Block), "block must be a Block instance"
        cache_key = ("from_universal", force_blockstate)
        if block_entity is None:
            if block in self._cache[cache_key]:
                output, extra_output, extra_needed = self._cache[cache_key][block]
                if isinstance(output, Entity):
                    output = copy.deepcopy(output)
                extra_output = copy.deepcopy(extra_output)
                return output, extra_output, extra_needed
        else:
            assert isinstance(
                block_entity, BlockEntity
            ), "extra_input must be None or a BlockEntity"
            block_entity = copy.deepcopy(block_entity)

        try:
            input_spec = self._universal_format.block._get_raw_specification(
                block.namespace, block.base_name
            )
            mapping = self.get_mapping_from_universal(
                block.namespace, block.base_name, force_blockstate
            )
        except KeyError:
            if block.namespace == "minecraft" and list(block.properties.keys()) == [
                "block_data"
            ]:
                log.debug(
                    f"Probably just a quirk block {block} from universal in {self._parent_version}."
                )
            elif self._parent_version.platform != "universal":
                self._warn_once(
                    (block,),
                    "Could not find translation information for {} {} from universal in {}. If this is not a vanilla block ignore this message",
                    self._mode,
                    block,
                    self._parent_version,
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

        if isinstance(output, Entity):
            output = copy.deepcopy(output)
        extra_output = copy.deepcopy(extra_output)
        return output, extra_output, extra_needed

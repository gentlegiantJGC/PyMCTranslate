from __future__ import annotations

import copy
from sys import getsizeof
import re
from typing import Dict, Iterable, List, Tuple, Union, overload, Generator
import amulet_nbt


class Block:
    """
    Class to handle data about various blockstates and allow for extra blocks to be created and interacted with.

    .. important::
       Creating version specific block objects via the `Block()` constructor instead of using
       :meth:`api.world.World.get_block_instance` is supported but not encouraged. To avoid possible caveats of doing this,
       make sure to either only instantiate blocks with Amulet blockstate data or use
       :meth:`api.world.World.get_block_instance` instead

    Here's a few examples on how create a Block object with extra blocks:

    Creating a new Block object with the base of ``stone`` and has an extra block of ``water[level=1]``:

    >>> stone = blockstate_to_block("minecraft:stone")
    >>> water_level_1 = blockstate_to_block("minecraft:water[level=1]")
    >>> stone_with_extra_block = stone + water_level_1
    >>> repr(stone_with_extra_block)
    'Block(minecraft:stone, minecraft:water[level=1])'

    Creating a new Block object using the namespace and base_name:

    >>> granite = Block(namespace="minecraft", base_name="granite")


    Creating a new Block object with another layer of extra blocks:

    >>> stone_water_granite = stone_with_extra_block + granite # Doesn't modify any of the other objects
    >>> repr(stone_water_granite)
    'Block(minecraft:stone, minecraft:water[level=1], minecraft:granite)'


    Creating a new Block object by removing an extra block from all layers:

    *Note: This removes all instances of the Block object from extra blocks*

    >>> stone_granite = stone_water_granite - water_level_1 # Doesn't modify any of the other objects either
    >>> repr(stone_granite)
    'Block(minecraft:stone, minecraft:granite)'


    Creating a new Block object by removing a specific layer:

    >>> oak_log_axis_x = blockstate_to_block("minecraft:oak_log[axis=x]")
    >>> stone_water_granite_water_oak_log = stone_water_granite + water_level_1 + oak_log_axis_x
    >>> repr(stone_water_granite_water_oak_log)
    'Block(minecraft:stone, minecraft:water[level=1], minecraft:granite, minecraft:water[level=1], minecraft:oak_log[axis=x])'

    >>> stone_granite_water_oak_log = stone_water_granite_water_oak_log.remove_layer(0)
    >>> repr(stone_granite_water_oak_log)
    'Block(minecraft:stone, minecraft:granite, minecraft:water[level=1], minecraft:oak_log[axis=x])'

    """

    __slots__ = (
        "_namespaced_name",
        "_namespace",
        "_base_name",
        "_properties",
        "_extra_blocks",
        "_blockstate",
    )  # Reduces memory footprint

    blockstate_regex = re.compile(
        r"(?:(?P<namespace>[a-z0-9_.-]+):)?(?P<base_name>[a-z0-9/._-]+)(?:\[(?P<property_name>[a-z0-9_]+)=(?P<property_value>[a-z0-9_\"]+)(?P<properties>.*)\])?"
    )
    # blockstate_regex = re.compile(
    #     r"(?:(?P<namespace>[a-z0-9_.-]+):)?(?P<base_name>[a-z0-9/._-]+)(?:\[(?P<property_name>[a-z0-9_]+)=(?P<property_value>[a-z0-9_]+)(?P<properties>.*)\])?"
    # )

    parameters_regex = re.compile(r"(?:,(?P<name>[a-z0-9_]+)=(?P<value>[a-z0-9_\"]+))")
    # parameters_regex = re.compile(r"(?:,(?P<name>[a-z0-9_]+)=(?P<value>[a-z0-9_]+))")

    def __init__(
        self,
        namespace: str,
        base_name: str,
        properties: Dict[str, amulet_nbt.BaseValueType] = None,
        extra_blocks: Union[Block, Iterable[Block]] = None,
    ):
        self._blockstate = None
        self._namespaced_name = None
        assert (isinstance(namespace, str) or namespace is None) and isinstance(
            base_name, str
        ), f"namespace and base_name must be strings {namespace} {base_name}"
        self._namespace = namespace
        self._base_name = base_name

        if properties is None:
            properties = {}
        assert isinstance(properties, dict) and all(
            isinstance(val, amulet_nbt.BaseValueType) for val in properties.values()
        ), properties

        self._properties = properties
        self._extra_blocks = ()
        if extra_blocks:
            if isinstance(extra_blocks, Block):
                extra_blocks = [extra_blocks]
            self._extra_blocks = tuple(extra_blocks)

        self._gen_blockstate()

    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the blockstate represented by the Block object (IE: `minecraft:stone`)

        :return: The namespace:base_name of the blockstate
        """
        return self._namespaced_name

    @property
    def namespace(self) -> str:
        """
        The namespace of the blockstate represented by the Block object (IE: `minecraft`)

        :return: The namespace of the blockstate
        """
        return self._namespace

    @property
    def base_name(self) -> str:
        """
        The base name of the blockstate represented by the Block object (IE: `stone`, `dirt`)

        :return: The base name of the blockstate
        """
        return self._base_name

    @property
    def properties(self) -> Dict[str, amulet_nbt.BaseValueType]:
        """
        The mapping of properties of the blockstate represented by the Block object (IE: `{"level": "1"}`)

        :return: A dictionary of the properties of the blockstate
        """
        return copy.deepcopy(self._properties)

    @property
    def blockstate(self) -> str:
        """
        The full blockstate string of the blockstate represented by the Block object (IE: `minecraft:stone`, `minecraft:oak_log[axis=x]`)

        :return: The blockstate string
        """
        return self._blockstate

    @property
    def base_block(self) -> Block:
        """
        Returns the block without any extra blocks

        :return: A Block object
        """
        if len(self.extra_blocks) == 0:
            return self
        else:
            return Block(
                namespace=self.namespace,
                base_name=self.base_name,
                properties=self.properties,
            )

    @property
    def extra_blocks(self) -> Union[Tuple, Tuple[Block]]:
        """
        Returns a tuple of the extra blocks contained in the Block instance

        :return: A tuple of Block objects
        """
        return self._extra_blocks

    def _gen_blockstate(self):
        self._namespaced_name = self._blockstate = f"{self.namespace}:{self.base_name}"
        if self.properties:
            props = [
                f"{key}={value.to_snbt()}"
                for key, value in sorted(self.properties.items())
            ]
            self._blockstate += f"[{','.join(props)}]"
        if self.extra_blocks:
            self._blockstate += (
                f"{{{' , '.join(block.blockstate for block in self.extra_blocks)}}}"
            )

    @staticmethod
    def parse_blockstate_string(
        blockstate: str,
    ) -> Tuple[str, str, Dict[str, amulet_nbt.BaseValueType]]:
        match = Block.blockstate_regex.match(blockstate)
        namespace = match.group("namespace") or "minecraft"
        base_name = match.group("base_name")

        if match.group("property_name") is not None:
            properties = {match.group("property_name"): match.group("property_value")}
        else:
            properties = {}

        properties_string = match.group("properties")
        if properties_string is not None:
            properties_match = Block.parameters_regex.finditer(properties_string)
            for match in properties_match:
                properties[match.group("name")] = match.group("value")

        return (
            namespace,
            base_name,
            {k: amulet_nbt.from_snbt(v) for k, v in sorted(properties.items())},
        )

    def __str__(self) -> str:
        """
        :return: The base blockstate string of the Block object
        """
        return self.blockstate

    def __repr__(self) -> str:
        """
        :return: The base blockstate string of the Block object along with the blockstate strings of included extra blocks
        """
        return f"Block({', '.join([str(b) for b in (self, *self.extra_blocks)])})"

    def __len__(self):
        return len(self._extra_blocks) + 1

    def _compare_extra_blocks(self, other: Block) -> bool:
        if len(self.extra_blocks) != len(other.extra_blocks):
            return False

        if len(self.extra_blocks) == 0:
            return True

        for our_extra_block, their_extra_block in zip(
            self.extra_blocks, other.extra_blocks
        ):
            if our_extra_block != their_extra_block:
                return False

        return True

    def __eq__(self, other: Block) -> bool:
        """
        Checks the equality of this Block object to another Block object

        :param other: The Block object to check against
        :return: True if the Blocks objects are equal, False otherwise
        """
        if self.__class__ != other.__class__:
            return False

        return self.blockstate == other.blockstate and self._compare_extra_blocks(other)

    def __gt__(self, other: Block) -> bool:
        """
        Allows blocks to be sorted so numpy.unique can be used on them
        """
        if self.__class__ != other.__class__:
            return False
        return self.blockstate > other.blockstate

    def __hash__(self) -> int:
        """
        Hashes the Block object

        :return: A hash of the Block object
        """
        current_hash = hash(self.blockstate)

        if self.extra_blocks:
            current_hash = current_hash + hash(self.extra_blocks)

        return current_hash

    def __add__(self, other: Block) -> Block:
        """
        Allows for other Block objects to be added to this Block object's ``extra_blocks``

        :param other: The Block object to add to the end of this Block object's `extra_blocks`
        :return: A new Block object with the same data but with an additional Block at the end of ``extra_blocks``
        """
        if not isinstance(other, Block):
            return NotImplemented

        if (
            len(other.extra_blocks) == 0
        ):  # Reduces the amount of extra objects/references created
            other_cpy = other
        else:
            other_cpy = Block(
                namespace=other.namespace,
                base_name=other.base_name,
                properties=other.properties,
            )

        other_extras = []
        for eb in other.extra_blocks:
            if (
                len(eb.extra_blocks) == 0
            ):  # Reduces the amount of extra objects/references created
                other_extras.append(eb)
            else:
                other_extras.append(
                    Block(
                        namespace=eb.namespace,
                        base_name=eb.base_name,
                        properties=eb.properties,
                    )
                )

        return Block(
            namespace=self.namespace,
            base_name=self.base_name,
            properties=self.properties,
            extra_blocks=[*self.extra_blocks, other_cpy, *other_extras],
        )

    def __sub__(self, other: Block) -> Block:
        """
        Allows for other Block objects to be subtracted from this Block object's ``extra_blocks``

        :param other: The Block object to subtract from this Block objects' ``extra_blocks``
        :return: A new Block object without any instances of the subtracted block in ``extra_blocks``
        """
        if not isinstance(other, Block):
            return NotImplemented

        if (
            len(other.extra_blocks) == 0
        ):  # Reduces the amount of extra objects/references created
            other_cpy = other
        else:
            other_cpy = Block(
                namespace=other.namespace,
                base_name=other.base_name,
                properties=other.properties,
            )

        other_extras = []
        for eb in other.extra_blocks:
            if len(eb.extra_blocks) == 0:
                other_extras.append(eb)
            else:
                other_extras.append(
                    Block(
                        namespace=eb.namespace,
                        base_name=eb.base_name,
                        properties=eb.properties,
                    )
                )

        # Sets are unordered, so a regular set subtraction doesn't always return the order we want (it sometimes will!)
        # So we loop through all of our extra blocks and only append those to the new_extras list if they aren't in
        # extra_blocks_to_remove
        new_extras = []
        extra_blocks_to_remove = (other_cpy, *other_extras)
        for eb in self.extra_blocks:
            if eb not in extra_blocks_to_remove:
                new_extras.append(eb)

        return Block(
            namespace=self.namespace,
            base_name=self.base_name,
            properties=self.properties,
            extra_blocks=new_extras,
        )

    def __sizeof__(self):
        size = (
            getsizeof(self.namespace)
            + getsizeof(self.base_name)
            + getsizeof(self.properties)
            + getsizeof(self.blockstate)
        )
        for eb in self.extra_blocks:
            size += getsizeof(eb)
        return size


class BlockManager:
    """
    Class to handle the mappings between Block objects and their index-based internal IDs
    """

    def __init__(self):
        """
        Creates a new BlockManager object
        """
        self._index_to_block: List[Block] = []
        self._block_to_index_map: Dict[Block, int] = {}

    def __len__(self):
        return len(self._index_to_block)

    def __contains__(self, item: Block) -> bool:
        return item in self._block_to_index_map

    def blocks(self) -> Tuple[Block]:
        return tuple(self._index_to_block)

    def items(self) -> Generator[Tuple[int, Block]]:
        for index, block in enumerate(self._index_to_block):
            yield index, block

    @overload
    def __getitem__(self, item: Block) -> int:
        ...

    @overload
    def __getitem__(self, item: int) -> Block:
        ...

    def __getitem__(self, item):
        """
        If a Block object is passed to this function, it'll return the internal ID/index of the
        blockstate. If an int is given, this method will return the Block object at that specified index.

        :param item: The Block object or int to get the mapping data of
        :return: An int if a Block object was supplied, a Block object if an int was supplied
        """
        try:
            if isinstance(item, Block):
                return self._block_to_index_map[item]

            return self._index_to_block[item]
        except (KeyError, IndexError):
            raise KeyError(
                f"There is no {item} in the BlockManager. "
                f"You might want to use the `add_block` function for your blocks before accessing them."
            )

    def get_add_block(self, block: Block) -> int:
        """
        Adds a Block object to the internal Block object/ID mappings. If the Block already exists in the mappings,
        then the existing ID is returned

        :param block: The Block to add to the manager
        :return: The internal ID of the Block
        """
        if block in self._block_to_index_map:
            return self._block_to_index_map[block]

        self._block_to_index_map[block] = i = len(self._block_to_index_map)
        self._index_to_block.append(block)

        return i

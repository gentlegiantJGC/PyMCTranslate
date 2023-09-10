from __future__ import annotations

from typing import Union, Type, Sequence, Optional, Dict, List, Callable, Tuple, TypeVar, Iterator
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field

from amulet_nbt import ByteTag, ShortTag, IntTag, LongTag, FloatTag, DoubleTag, StringTag, ListTag, CompoundTag, ByteArrayTag, IntArrayTag, LongArrayTag, from_snbt, NamedTag

from PyMCTranslate.py3.api import Block, BlockEntity, Entity, ChunkLoadError

K = TypeVar("K")
V = TypeVar("V")


BlockCoordinates = Tuple[int, int, int]
PropertyValueClasses = (ByteTag, IntTag, StringTag)
PropertyValueType = Union[ByteTag, IntTag, StringTag]


@dataclass
class SrcData:
    """Input data. This must not be changed."""

    block_input: Optional[Block]
    nbt_input: Optional[NamedTag]
    get_block_callback: Optional[Callable]
    absolute_location: BlockCoordinates = (0, 0, 0)


@dataclass
class StateData:
    relative_location: BlockCoordinates = (0, 0, 0)
    nbt_path: Tuple[str, str, List[Tuple[Union[str, int], str]]] = None
    inherited_data: Tuple[Union[str, None], Union[str, None], dict, bool, bool] = None


@dataclass
class DstData:
    output_type: Optional[str] = None
    output_name: Optional[str] = None
    properties: Dict[str, PropertyValueType] = field(default_factory=dict)
    nbt: List[
        Tuple[
            str,
            str,
            List[Union[str, int], str],
            Union[str, int],
            Union[
                ByteTag,
                ShortTag,
                IntTag,
                LongTag,
                FloatTag,
                DoubleTag,
                ByteArrayTag,
                StringTag,
                ListTag,
                CompoundTag,
                IntArrayTag,
                LongArrayTag,
            ],
        ]
    ] = field(default_factory=list)
    extra_needed: bool = False
    cacheable: bool = True


class HashableMapping(Mapping[K, V]):
    """
    A hashable Mapping class.
    All values in the mapping must be hashable.
    """
    def __init__(self, mapping: Mapping):
        self._map = dict(mapping)
        self._hash = hash(frozenset(mapping.items()))

    def __getitem__(self, k: K) -> V:
        return self._map[k]

    def __len__(self) -> int:
        return len(self._map)

    def __iter__(self) -> Iterator[K]:
        return iter(self._map)

    def __hash__(self):
        return self._hash


_translation_functions: Dict[str, Type[AbstractBaseTranslationFunction]] = {}

def from_json(data) -> AbstractBaseTranslationFunction:
    if isinstance(data, (list, Sequence)):
        return TranslationFunctionSequence.from_json(data)
    elif isinstance(data, (dict, Mapping)):
        func_cls = _translation_functions[data["function"]]
        return func_cls.from_json(data)
    else:
        raise TypeError


class AbstractBaseTranslationFunction(ABC):
    Name: str = None
    _instances = {}

    @abstractmethod
    def __init__(self, data):
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        if cls.Name is None:
            raise RuntimeError(f"Name attribute has not been set for {cls}")
        if cls.Name in _translation_functions:
            raise RuntimeError(f"A translation function with name {cls.Name} already exists.")
        _translation_functions[cls.Name] = cls

    @classmethod
    @abstractmethod
    def instance(cls, data) -> AbstractBaseTranslationFunction:
        """
        Get the translation function for this data.
        This will return a cached instance if it already exists.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_json(cls, data) -> AbstractBaseTranslationFunction:
        """Get a translation function from the JSON representation."""
        raise NotImplementedError

    @abstractmethod
    def to_json(self):
        """Convert the translation function back to the JSON representation."""
        raise NotImplementedError

    @abstractmethod
    def run(self, *args, **kwargs):
        """Run the translation function"""
        raise NotImplementedError

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError


class TranslationFunctionSequence(AbstractBaseTranslationFunction):
    # class variables
    Name = "sequence"

    # instance variables
    _functions: tuple[AbstractBaseTranslationFunction]

    def __init__(self, functions: Sequence[AbstractBaseTranslationFunction]):
        self._functions = tuple(functions)
        if not all(isinstance(inst, AbstractBaseTranslationFunction) for inst in self._functions):
            raise TypeError

    @classmethod
    def instance(cls, functions: Sequence[AbstractBaseTranslationFunction]) -> TranslationFunctionSequence:
        self = cls(functions)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: list) -> TranslationFunctionSequence:
        parsed = []
        for func in data:
            parsed.append(from_json(func))

        return cls.instance(parsed)

    def to_json(self) -> list:
        return [func.to_json() for func in self._functions]

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def __hash__(self):
        return hash(self._functions)

    def __eq__(self, other):
        if not isinstance(other, TranslationFunctionSequence):
            return NotImplemented
        return self._functions == other._functions


class NewBlock(AbstractBaseTranslationFunction):
    # class variables
    Name = "new_block"

    # instance variables
    _block: str

    def __init__(self, block: str):
        if not isinstance(block, str):
            raise TypeError
        self._block = block

    @classmethod
    def instance(cls, block: str) -> NewBlock:
        self = cls(block)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: dict) -> NewBlock:
        if data.get("function") != "new_block":
            raise ValueError("Incorrect function data given.")
        return cls.instance(data["options"])

    def to_json(self) -> dict:
        return {
            "function": "new_block",
            "options": self._block
        }

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def __hash__(self):
        return hash(self._block)

    def __eq__(self, other):
        if not isinstance(other, NewBlock):
            return NotImplemented
        return self._block == other._block


class NewEntity(AbstractBaseTranslationFunction):
    # class variables
    Name = "new_entity"

    # instance variables
    _entity: str

    def __init__(self, entity: str):
        if not isinstance(entity, str):
            raise TypeError
        self._entity = entity

    @classmethod
    def instance(cls, entity: str) -> NewEntity:
        self = cls(entity)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: dict) -> NewEntity:
        if data.get("function") != "new_entity":
            raise ValueError("Incorrect function data given.")
        return cls.instance(data["options"])

    def to_json(self) -> dict:
        return {
            "function": "new_entity",
            "options": self._entity
        }

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def __hash__(self):
        return hash(self._entity)

    def __eq__(self, other):
        if not isinstance(other, NewEntity):
            return NotImplemented
        return self._entity == other._entity


class NewProperties(AbstractBaseTranslationFunction):
    # class variables
    Name = "new_properties"
    _instances = {}

    # instance variables
    _properties: HashableMapping[str, PropertyValueType]

    def __init__(self, properties: Mapping[str, PropertyValueType]):
        self._properties = HashableMapping(properties)
        if not all(isinstance(key, str) for key in self._properties.keys()):
            raise TypeError
        if not all(isinstance(value, PropertyValueClasses) for value in self._properties.values()):
            raise TypeError

    @classmethod
    def instance(cls, properties: Mapping[str, PropertyValueType]) -> NewProperties:
        self = cls(properties)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: dict) -> NewProperties:
        if data.get("function") != "new_properties":
            raise ValueError("Incorrect function data given.")
        return cls.instance({
            property_name: from_snbt(snbt)
            for property_name, snbt in data["options"].items()
        })

    def to_json(self) -> dict:
        return {
            "function": "new_properties",
            "options": {property_name: tag.to_snbt() for property_name, tag in self._properties.items()}
        }

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def __hash__(self):
        return hash(self._properties)

    def __eq__(self, other):
        if not isinstance(other, NewProperties):
            return NotImplemented
        return self._properties == other._properties


class MapProperties(AbstractBaseTranslationFunction):
    # class variables
    Name = "map_properties"
    _instances = {}

    # instance variables
    _properties: HashableMapping[str, HashableMapping[PropertyValueType, AbstractBaseTranslationFunction]]

    def __init__(self, properties: Mapping[str, Mapping[PropertyValueType, AbstractBaseTranslationFunction]]):
        hashable_properties = {}

        for prop, data in properties.items():
            if not isinstance(prop, str):
                raise TypeError
            hashable_data = HashableMapping(data)
            for val, func in hashable_data.items():
                if not isinstance(val, PropertyValueClasses):
                    raise TypeError
                if not isinstance(func, AbstractBaseTranslationFunction):
                    raise TypeError
            hashable_properties[prop] = hashable_data

        self._properties = HashableMapping(hashable_properties)

    @classmethod
    def instance(cls, properties: Mapping[str, Mapping[PropertyValueType, AbstractBaseTranslationFunction]]) -> MapProperties:
        self = cls(properties)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data) -> MapProperties:
        if data.get("function") != "map_properties":
            raise ValueError("Incorrect function data given.")
        return cls.instance({
            property_name: {
                from_snbt(snbt): from_json(func) for snbt, func in mapping.items
            }
            for property_name, mapping in data["options"].items()
        })

    def to_json(self):
        return {
            "function": "map_properties",
            "options": {
                property_name: {
                    nbt.to_snbt(): func.to_json() for nbt, func in mapping.items()
                } for property_name, mapping in self._properties.items()
            }
        }

    def run(self, *args, **kwargs):
        pass

    def __hash__(self):
        return hash(self._properties)

    def __eq__(self, other):
        if not isinstance(other, MapProperties):
            return NotImplemented
        return self._properties == other._properties


class MultiBlock(AbstractBaseTranslationFunction):
    Name = "multiblock"
    _blocks: tuple[tuple[BlockCoordinates, AbstractBaseTranslationFunction], ...]

    def __init__(self, blocks: Sequence[tuple[BlockCoordinates, AbstractBaseTranslationFunction]]):
        self._blocks = tuple(blocks)
        for coords, func in self._blocks:
            if not isinstance(coords, tuple) and len(coords) == 3 and all(isinstance(v, int) for v in coords):
                raise TypeError
            if not isinstance(func, AbstractBaseTranslationFunction):
                raise TypeError

    @classmethod
    def instance(cls, blocks: Sequence[tuple[BlockCoordinates, AbstractBaseTranslationFunction]]) -> MultiBlock:
        self = cls(blocks)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data) -> MultiBlock:
        if data.get("function") != "multiblock":
            raise ValueError("Incorrect function data given.")
        return cls.instance([
            (block["coords"], block["functions"])
            for block in data["options"].items()
        ])

    def to_json(self):
        return {
            "function": "multiblock",
            "options": [
                {
                    "coords": list(coords),
                    "functions": func.to_json()
                } for coords, func in self._blocks
            ]
        }

    def run(self, *args, **kwargs):
        pass

    def __hash__(self):
        return hash(self._blocks)

    def __eq__(self, other):
        if not isinstance(other, MultiBlock):
            return NotImplemented
        return self._blocks == other._blocks


class MapBlockName(AbstractBaseTranslationFunction):
    pass


class WalkInputNBT(AbstractBaseTranslationFunction):
    pass


class NewNBT(AbstractBaseTranslationFunction):
    pass


class CarryNBT(AbstractBaseTranslationFunction):
    pass


class MapNBT(AbstractBaseTranslationFunction):
    pass


class Code(AbstractBaseTranslationFunction):
    pass


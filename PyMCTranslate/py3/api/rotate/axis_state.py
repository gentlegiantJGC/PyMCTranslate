from typing import Dict, Tuple, Optional, List
from abc import ABC, abstractmethod

import numpy

from amulet_nbt import TAG_String

from PyMCTranslate.py3.api import Block, PropertyValueType

# This is the dictionary stored under the properties key in the specification files
from PyMCTranslate.py3.api.version.translators.block import BlockSpecification

from .rotate import BlockShapes, BaseBlockShape, RotateMode


class BaseAxisStateShape(BaseBlockShape):
    @property
    @classmethod
    @abstractmethod
    def Vectors(
        cls,
    ) -> Dict[str, Tuple[float, float, float],]:
        """A map from the property names to a vector representing that rotation"""
        raise NotImplementedError

    @property
    @classmethod
    @abstractmethod
    def Values(
        cls,
    ) -> Tuple[PropertyValueType]:
        """
        The values for each property (they must all have the same values)
        First is the default
        """
        raise NotImplementedError

    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return all(
            set(specification.valid_properties.get(prop_name, ())) == set(self.Values)
            for prop_name in self.Vectors
        )

    def transform(
        self,
        block: Block,
        transform: numpy.ndarray,
        mode: RotateMode = RotateMode.Nearest,
    ):
        if not mode:
            return block
        old_properties = block.properties
        properties = block.properties
        properties.update(dict.fromkeys(self.Vectors.keys(), self.Values[0]))

        for old_face, vector in self.Vectors.items():
            vector2 = tuple(numpy.matmul(transform, (*vector, 0)).tolist())[:-1]
            new_face = self._vector_to_face(vector2, RotateMode.Exact)
            if new_face is not None:
                properties[new_face] = old_properties[old_face]

        return Block(block.namespace, block.base_name, properties)

    def _block_to_vector(self, block: Block) -> Optional[Tuple[float, float, float]]:
        """Convert the block state to a vector representing the rotation"""
        vector = self.Vectors.get(
            tuple(block.properties.get(prop, None) for prop in self.Properties), None
        )
        if isinstance(vector, list):
            return vector[0]
        else:
            return vector

    def _vector_to_face(
        self, vector: Tuple[float, float, float], mode: RotateMode
    ) -> Optional[str]:
        """Convert a rotation vector back to the face name"""

        def dist(vec: Tuple[float, float, float]) -> float:
            return sum((a - b) ** 2 for a, b in zip(vector, vec))

        sorted_vectors: List[Tuple[str, Tuple[float, float, float]]] = sorted(
            self.Vectors.items(), key=lambda a: dist(a[1])
        )
        face, closest_vector = sorted_vectors[0]
        if mode is RotateMode.Exact and dist(closest_vector) > 0.01:
            return None
        return face


@BlockShapes.register
class AllAxisBoolShape(BaseAxisStateShape):
    Values = (TAG_String("false"), TAG_String("true"))
    Vectors = {
        "north": (0, 0, -1),
        "south": (0, 0, 1),
        "west": (-1, 0, 0),
        "east": (1, 0, 0),
        "down": (0, -1, 0),
        "up": (0, 1, 0),
    }


@BlockShapes.register
class CompasPlusAxisBoolShape(BaseAxisStateShape):
    Values = (TAG_String("false"), TAG_String("true"))
    Vectors = {
        "north": (0, 0, -1),
        "south": (0, 0, 1),
        "west": (-1, 0, 0),
        "east": (1, 0, 0),
        "up": (0, 1, 0),
    }


class BaseCompassStateShape(BaseAxisStateShape, ABC):
    Vectors = {
        "north": (0, 0, -1),
        "south": (0, 0, 1),
        "west": (-1, 0, 0),
        "east": (1, 0, 0),
    }


@BlockShapes.register
class CompassAxisBoolShape(BaseCompassStateShape):
    Values = (TAG_String("false"), TAG_String("true"))


@BlockShapes.register
class RedstoneShape(BaseCompassStateShape):
    Values = (TAG_String("none"), TAG_String("side"), TAG_String("up"))


@BlockShapes.register
class WallShape(BaseCompassStateShape):
    Values = (TAG_String("none"), TAG_String("low"), TAG_String("tall"))

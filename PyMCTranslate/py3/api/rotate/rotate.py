from typing import Dict, Tuple, Type, Set, Optional, List, Union
from abc import ABC, abstractmethod
from enum import IntEnum

import numpy

from PyMCTranslate.py3.api.version import Version
from PyMCTranslate.py3.api import Block, PropertyValueType


# This is the dictionary stored under the properties key in the specification files
from PyMCTranslate.py3.api.version.translators.block import BlockSpecification


class RotateMode(IntEnum):
    Null = 0  # Do not rotate. Return the input block
    Exact = 1  # Only rotate if an exact rotation exists
    Nearest = 2  # Choose the closest valid state


class BaseBlockShape(ABC):
    @abstractmethod
    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        """
        Can this class rotate the given block.

        :param namespace: The namespace of the block (this should always be "universal")
        :param base_name: The base name of the block
        :param specification: The specification data
        :return: True if this class can rotate the given block. False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def transform(
        self,
        block: Block,
        transform: numpy.ndarray,
        mode: RotateMode = RotateMode.Nearest,
    ):
        """
        Rotate the given block and return a new block.

        :param block: The block to rotate
        :param transform: The transformation matrix to transform the block with
        :param mode: The rotation mode (This should only be Exact or Nearest because Null was handled before calling)
        :return: The rotated block
        """
        raise NotImplementedError


class BlockShapeManager:
    """A container to store and find block shapes."""

    def __init__(self):
        self._block_shapes: List[BaseBlockShape] = []

    def register(self, block_shape: Type[BaseBlockShape]) -> Type[BaseBlockShape]:
        """
        Use this as a decorator on top of the block shape class

        :param block_shape: A subclass of BaseBlockShape
        :return: The same class that was given so that this method can be used as a decorator
        """
        self._block_shapes.append(block_shape())
        return block_shape

    def find_block_shape(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> Optional[BaseBlockShape]:
        """
        Find the block shape class that is valid for this specification.

        :param namespace: The namespace of the block (this should always be "universal")
        :param base_name: The base name of the block
        :param specification: The specification for the block.
        :return: The block class that is valid for this block.
        """
        return next(
            (
                block_shape
                for block_shape in self._block_shapes
                if block_shape.is_valid(namespace, base_name, specification)
            ),
            None,
        )


BlockShapes = BlockShapeManager()


class BaseVectorBlockShape(BaseBlockShape):
    @property
    @classmethod
    @abstractmethod
    def Properties(cls) -> Tuple[str, ...]:
        """The names of the properties used in the vector map."""
        raise NotImplementedError

    @property
    @classmethod
    @abstractmethod
    def Vectors(
        cls,
    ) -> Dict[
        Tuple[PropertyValueType, ...],
        Union[
            Tuple[float, float, float],
            List[Tuple[float, float, float]],
        ],
    ]:
        """A map from the property values to a vector representing that rotation"""
        raise NotImplementedError

    def _block_to_vector(self, block: Block) -> Optional[Tuple[float, float, float]]:
        """Convert the block state to a vector representing the rotation"""
        vector = self.Vectors.get(
            tuple(block.properties.get(prop, None) for prop in self.Properties), None
        )
        if isinstance(vector, list):
            return vector[0]
        else:
            return vector

    def _vector_to_properties(
        self, vector: Tuple[float, float, float], mode: RotateMode
    ) -> Optional[Tuple[PropertyValueType, ...]]:
        """Convert a rotation vector back into properties"""

        def dist(vec: Tuple[float, float, float]) -> float:
            return sum((a - b) ** 2 for a, b in zip(vector, vec))

        sorted_vectors: List[
            Tuple[Tuple[PropertyValueType, ...], Tuple[float, float, float]]
        ] = sorted(
            self.Vectors.items(),
            key=lambda a: (
                min([dist(v) for v in a[1]]) if isinstance(a[1], list) else dist(a[1])
            ),
        )
        properties, closest_vector = sorted_vectors[0]
        if mode is RotateMode.Exact and dist(closest_vector) > 0.01:
            return None
        return properties

    @staticmethod
    def _transform_vector(vector, transform):
        return tuple(numpy.matmul(transform, (*vector, 0)).tolist())[:-1]

    def transform(
        self,
        block: Block,
        transform: numpy.ndarray,
        mode: RotateMode = RotateMode.Nearest,
    ):
        if not mode:
            return block
        vector = self._block_to_vector(block)
        if vector is None:
            return block
        vector2 = self._transform_vector(vector, transform)
        new_properties = self._vector_to_properties(vector2, mode)
        if new_properties is None:
            return block
        properties = block.properties
        properties.update(dict(zip(self.Properties, new_properties)))

        return Block(block.namespace, block.base_name, properties)


class RotationManager:
    def __init__(self, universal_version: Version):
        self._block_shapes: Dict[str, BaseBlockShape] = {}
        for namespace in universal_version.block.namespaces():
            for base_name in universal_version.block.base_names(namespace):
                block_shape = BlockShapes.find_block_shape(
                    namespace,
                    base_name,
                    universal_version.block.get_specification(namespace, base_name),
                )
                if block_shape is not None:
                    self._block_shapes[f"{namespace}:{base_name}"] = block_shape

    def transform(
        self,
        block: Block,
        transform: numpy.ndarray,
        mode: RotateMode = RotateMode.Nearest,
    ):
        if mode == RotateMode.Null:
            return block

        blocks = []
        for sub_block in block:
            blocks.append(
                self._block_shapes[sub_block.namespaced_name].transform(
                    sub_block.base_block, transform, mode
                )
                if sub_block.namespaced_name in self._block_shapes
                else sub_block
            )

        # TODO: replace this with Block.join(blocks)
        return Block(
            blocks[0].namespace, blocks[0].base_name, blocks[0].properties, blocks[1:]
        )

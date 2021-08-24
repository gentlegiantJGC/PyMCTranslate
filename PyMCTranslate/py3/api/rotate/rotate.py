from typing import Dict, Tuple, Type, List, Set, Optional
from abc import ABC, abstractmethod
from enum import IntEnum
from PyMCTranslate.py3.api.version import Version
from PyMCTranslate.py3.api import Block


# This is the dictionary stored under the properties key in the specification files
SpecificationType = Dict[str, List[str]]


class RotateMode(IntEnum):
    Null = 0  # Do not rotate. Return the input block
    Exact = 1  # Only rotate if an exact rotation exists
    Nearest = 2  # Choose the closest valid state


class BaseBlockShape(ABC):
    @abstractmethod
    def is_valid(
        self, namespace: str, base_name: str, specification: SpecificationType
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
    def rotate(
        self,
        block: Block,
        angle: Tuple[float, float, float],
        mode: RotateMode = RotateMode.Nearest,
    ):
        """
        Rotate the given block and return a new block.

        :param block: The block to rotate
        :param angle: The amount to rotate the block
        :param mode: The rotation mode (This should only be Exact or Nearest because Null was handled before calling)
        :return: The rotated block
        """
        raise NotImplementedError


class BlockShapeManager:
    def __init__(self):
        self._block_shapes: Set[BaseBlockShape] = set()

    def register(self, block_shape: Type[BaseBlockShape]) -> Type[BaseBlockShape]:
        """
        Use this as a decorator on top of the block shape class

        :param block_shape: A subclass of BaseBlockShape
        :return: The same class that was given so that this method can be used as a decorator
        """
        self._block_shapes.add(block_shape())
        return block_shape

    def find_block_shape(
        self, namespace: str, base_name: str, specification: SpecificationType
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


@BlockShapes.register
class ExampleBlockShape(BaseBlockShape):
    def is_valid(
        self, namespace: str, base_name: str, specification: SpecificationType
    ) -> bool:
        # if something:
        #   return True
        return False

    def rotate(
        self,
        block: Block,
        angle: Tuple[float, float, float],
        mode: RotateMode = RotateMode.Nearest,
    ):
        # do some magic and return a new transformed block
        # base logic can be defined in the base class
        # if multiple classes use similar logic use the class system to your advantage and create a base class for them
        raise NotImplementedError


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
                    self._block_shapes[
                        f"{namespace}:{base_name}"
                    ] = block_shape

    def rotate(
        self,
        block: Block,
        angle: Tuple[float, float, float],
        mode: RotateMode = RotateMode.Nearest,
    ):
        if mode and block.namespaced_name in self._block_shapes:
            return self._block_shapes[block.namespaced_name].rotate(block, angle, mode)
        else:
            return block

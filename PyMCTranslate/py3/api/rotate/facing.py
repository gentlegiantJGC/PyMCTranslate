from amulet_nbt import TAG_String

# This is the dictionary stored under the properties key in the specification files
from PyMCTranslate.py3.api.version.translators.block import BlockSpecification

from .rotate import BlockShapes, BaseVectorBlockShape


@BlockShapes.register
class DoorShape(BaseVectorBlockShape):
    Properties = ("hinge", "half", "facing")
    Vectors = {
        (TAG_String("left"), TAG_String("lower"), TAG_String("east")): (2, 1, 1),
        (TAG_String("left"), TAG_String("lower"), TAG_String("north")): (1, 1, -2),
        (TAG_String("left"), TAG_String("lower"), TAG_String("south")): (-1, 1, 2),
        (TAG_String("left"), TAG_String("lower"), TAG_String("west")): (-2, 1, -1),
        (TAG_String("left"), TAG_String("upper"), TAG_String("east")): (2, -1, 1),
        (TAG_String("left"), TAG_String("upper"), TAG_String("north")): (1, -1, -2),
        (TAG_String("left"), TAG_String("upper"), TAG_String("south")): (-1, -1, 2),
        (TAG_String("left"), TAG_String("upper"), TAG_String("west")): (-2, -1, -1),
        (TAG_String("right"), TAG_String("lower"), TAG_String("east")): (2, 1, -1),
        (TAG_String("right"), TAG_String("lower"), TAG_String("north")): (-1, 1, -2),
        (TAG_String("right"), TAG_String("lower"), TAG_String("south")): (1, 1, 2),
        (TAG_String("right"), TAG_String("lower"), TAG_String("west")): (-2, 1, 1),
        (TAG_String("right"), TAG_String("upper"), TAG_String("east")): (2, -1, -1),
        (TAG_String("right"), TAG_String("upper"), TAG_String("north")): (-1, -1, -2),
        (TAG_String("right"), TAG_String("upper"), TAG_String("south")): (1, -1, 2),
        (TAG_String("right"), TAG_String("upper"), TAG_String("west")): (-2, -1, 1),
    }

    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return (
            set(specification.valid_properties.get("facing", ()))
            == {
                TAG_String("north"),
                TAG_String("south"),
                TAG_String("west"),
                TAG_String("east"),
            }
            and set(specification.valid_properties.get("half", ()))
            == {
                TAG_String("lower"),
                TAG_String("upper"),
            }
            and set(specification.valid_properties.get("hinge", ()))
            == {
                TAG_String("left"),
                TAG_String("right"),
            }
        )


@BlockShapes.register
class TrapdoorShape(BaseVectorBlockShape):
    Properties = ("open", "half", "facing")
    Vectors = {
        (TAG_String("false"), TAG_String("bottom"), TAG_String("east")): (-1, -2, 0),
        (TAG_String("false"), TAG_String("bottom"), TAG_String("north")): (0, -2, 1),
        (TAG_String("false"), TAG_String("bottom"), TAG_String("south")): (0, -2, -1),
        (TAG_String("false"), TAG_String("bottom"), TAG_String("west")): (1, -2, 0),
        (TAG_String("false"), TAG_String("top"), TAG_String("east")): (-1, 2, 0),
        (TAG_String("false"), TAG_String("top"), TAG_String("north")): (0, 2, 1),
        (TAG_String("false"), TAG_String("top"), TAG_String("south")): (0, 2, -1),
        (TAG_String("false"), TAG_String("top"), TAG_String("west")): (1, 2, 0),
        (TAG_String("true"), TAG_String("bottom"), TAG_String("east")): (-2, -1, 0),
        (TAG_String("true"), TAG_String("bottom"), TAG_String("north")): (0, -1, 2),
        (TAG_String("true"), TAG_String("bottom"), TAG_String("south")): (0, -1, -2),
        (TAG_String("true"), TAG_String("bottom"), TAG_String("west")): (2, -1, 0),
        (TAG_String("true"), TAG_String("top"), TAG_String("east")): (-2, 1, 0),
        (TAG_String("true"), TAG_String("top"), TAG_String("north")): (0, 1, 2),
        (TAG_String("true"), TAG_String("top"), TAG_String("south")): (0, 1, -2),
        (TAG_String("true"), TAG_String("top"), TAG_String("west")): (2, 1, 0),
    }

    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return (
            set(specification.valid_properties.get("facing", ()))
            == {
                TAG_String("north"),
                TAG_String("south"),
                TAG_String("west"),
                TAG_String("east"),
            }
            and set(specification.valid_properties.get("half", ()))
            == {
                TAG_String("bottom"),
                TAG_String("top"),
            }
            and set(specification.valid_properties.get("open", ()))
            == {
                TAG_String("false"),
                TAG_String("true"),
            }
        )


@BlockShapes.register
class StairShape(BaseVectorBlockShape):
    Properties = ("half", "facing")
    Vectors = {
        (half, facing): (x, y, z)
        for half, y in ((TAG_String("top"), -1), (TAG_String("bottom"), 1))
        for facing, x, z in (
            (TAG_String("north"), 0, -1),
            (TAG_String("south"), 0, 1),
            (TAG_String("west"), -1, 0),
            (TAG_String("east"), 1, 0),
        )
    }

    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return set(specification.valid_properties.get("facing", ())) == {
            TAG_String("north"),
            TAG_String("south"),
            TAG_String("west"),
            TAG_String("east"),
        } and set(specification.valid_properties.get("half", ())) == {
            TAG_String("top"),
            TAG_String("bottom"),
        }


@BlockShapes.register
class DispenserShape(BaseVectorBlockShape):
    Properties = ("facing",)
    Vectors = {
        (facing,): (x, y, z)
        for facing, x, y, z in (
            (TAG_String("north"), 0, 0, -1),
            (TAG_String("south"), 0, 0, 1),
            (TAG_String("west"), -1, 0, 0),
            (TAG_String("east"), 1, 0, 0),
            (TAG_String("up"), 0, 1, 0),
            (TAG_String("down"), 0, -1, 0),
        )
    }

    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return set(specification.valid_properties.get("facing", ())) == {
            TAG_String("north"),
            TAG_String("south"),
            TAG_String("west"),
            TAG_String("east"),
            TAG_String("up"),
            TAG_String("down"),
        }


@BlockShapes.register
class TorchShape(BaseVectorBlockShape):
    Properties = ("facing",)
    Vectors = {
        (facing,): (x, y, z)
        for facing, x, y, z in (
            (TAG_String("north"), 0, 0, -1),
            (TAG_String("south"), 0, 0, 1),
            (TAG_String("west"), -1, 0, 0),
            (TAG_String("east"), 1, 0, 0),
            (TAG_String("up"), 0, 1, 0),
        )
    }

    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return set(specification.valid_properties.get("facing", ())) == {
            TAG_String("north"),
            TAG_String("south"),
            TAG_String("west"),
            TAG_String("east"),
            TAG_String("up"),
        }


@BlockShapes.register
class HopperShape(BaseVectorBlockShape):
    Properties = ("facing",)
    Vectors = {
        (facing,): (x, y, z)
        for facing, x, y, z in (
            (TAG_String("north"), 0, 0, -1),
            (TAG_String("south"), 0, 0, 1),
            (TAG_String("west"), -1, 0, 0),
            (TAG_String("east"), 1, 0, 0),
            (TAG_String("down"), 0, -1, 0),
        )
    }

    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return set(specification.valid_properties.get("facing", ())) == {
            TAG_String("north"),
            TAG_String("south"),
            TAG_String("west"),
            TAG_String("east"),
            TAG_String("down"),
        }


@BlockShapes.register
class FurnaceShape(BaseVectorBlockShape):
    """This is a catch all if none of the above shapes match"""

    Properties = ("facing",)
    Vectors = {
        (facing,): (x, 0, z)
        for facing, x, z in (
            (TAG_String("north"), 0, -1),
            (TAG_String("south"), 0, 1),
            (TAG_String("west"), -1, 0),
            (TAG_String("east"), 1, 0),
        )
    }

    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return {
            TAG_String("north"),
            TAG_String("south"),
            TAG_String("west"),
            TAG_String("east"),
        }.issubset(set(specification.valid_properties.get("facing", ())))

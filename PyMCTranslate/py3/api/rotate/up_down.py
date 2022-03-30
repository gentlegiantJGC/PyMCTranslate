from amulet_nbt import TAG_String

# This is the dictionary stored under the properties key in the specification files
from PyMCTranslate.py3.api.version.translators.block import BlockSpecification

from .rotate import BlockShapes, BaseVectorBlockShape


@BlockShapes.register
class SlabShape(BaseVectorBlockShape):
    Properties = ("shape",)
    Vectors = {
        (TAG_String("top"),): (0, 1, 0),
        (TAG_String("bottom"),): (0, -1, 0),
    }

    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return set(specification.valid_properties.get("type", ())) == {
            TAG_String("bottom"),
            TAG_String("top"),
            TAG_String("double"),
        }


@BlockShapes.register
class DripstoneShape(BaseVectorBlockShape):
    Properties = ("vertical_direction",)
    Vectors = {
        (TAG_String("up"),): (0, 1, 0),
        (TAG_String("down"),): (0, -1, 0),
    }

    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return set(specification.valid_properties.get("vertical_direction", ())) == {
            TAG_String("up"),
            TAG_String("down"),
        }


@BlockShapes.register
class LanternShape(BaseVectorBlockShape):
    Properties = ("hanging",)
    Vectors = {
        (TAG_String("true"),): (0, 1, 0),
        (TAG_String("false"),): (0, -1, 0),
    }

    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return set(specification.valid_properties.get("hanging", ())) == {
            TAG_String("true"),
            TAG_String("false"),
        }

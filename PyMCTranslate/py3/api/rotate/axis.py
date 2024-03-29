from amulet_nbt import TAG_String

# This is the dictionary stored under the properties key in the specification files
from PyMCTranslate.py3.api.version.translators.block import BlockSpecification

from .rotate import BlockShapes, BaseVectorBlockShape


@BlockShapes.register
class PillarShape(BaseVectorBlockShape):
    Properties = ("axis",)
    Vectors = {
        (TAG_String("x"),): [(1, 0, 0), (-1, 0, 0)],
        (TAG_String("y"),): [(0, 1, 0), (0, -1, 0)],
        (TAG_String("z"),): [(0, 0, 1), (0, 0, -1)],
    }

    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return set(specification.valid_properties.get("axis", ())) == {
            TAG_String("x"),
            TAG_String("y"),
            TAG_String("z"),
        }


@BlockShapes.register
class PortalShape(BaseVectorBlockShape):
    Properties = ("axis",)
    Vectors = {
        # These vectors are intentionally the wrong way around
        (TAG_String("x"),): [(0, 0, 1), (0, 0, -1)],
        (TAG_String("z"),): [(1, 0, 0), (-1, 0, 0)],
    }

    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return set(specification.valid_properties.get("axis", ())) == {
            TAG_String("x"),
            TAG_String("z"),
        }

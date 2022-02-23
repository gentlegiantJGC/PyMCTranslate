from amulet_nbt import TAG_String

# This is the dictionary stored under the properties key in the specification files
from PyMCTranslate.py3.api.version.translators.block import BlockSpecification

from .rotate import BlockShapes, BaseVectorBlockShape


@BlockShapes.register
class RailShape(BaseVectorBlockShape):
    Properties = ("shape",)
    Vectors = {
        (TAG_String("ascending_north"),): [(0, -1, 1), (0, 1, -1)],
        (TAG_String("ascending_south"),): [(0, -1, -1), (0, 1, 1)],
        (TAG_String("ascending_west"),): [(1, -1, 0), (-1, 1, 0)],
        (TAG_String("ascending_east"),): [(-1, -1, 0), (1, 1, 0)],

        (TAG_String("east_west"),): [(1, 0, 0), (-1, 0, 0)],
        (TAG_String("north_south"),): [(0, 0, 1), (0, 0, -1)],
    }

    def is_valid(
            self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return set(specification.valid_properties.get("shape", ())) == {
            TAG_String("ascending_east"),
            TAG_String("ascending_north"),
            TAG_String("ascending_south"),
            TAG_String("ascending_west"),
            TAG_String("east_west"),
            TAG_String("north_south"),
        }


@BlockShapes.register
class RailShapePlus(BaseVectorBlockShape):
    Properties = ("shape",)
    Vectors = {
        # These vectors are intentionally the wrong way around
        (TAG_String("ascending_north"),): [(0, -1, 1), (0, 1, -1)],
        (TAG_String("ascending_south"),): [(0, -1, -1), (0, 1, 1)],
        (TAG_String("ascending_west"),): [(1, -1, 0), (-1, 1, 0)],
        (TAG_String("ascending_east"),): [(-1, -1, 0), (1, 1, 0)],

        (TAG_String("east_west"),): [(1, 0, 0), (-1, 0, 0)],
        (TAG_String("north_south"),): [(0, 0, 1), (0, 0, -1)],

        (TAG_String("north_east"),): (1, 0, -1),
        (TAG_String("north_west"),): (-1, 0, -1),
        (TAG_String("south_east"),): (1, 0, 1),
        (TAG_String("south_west"),): (-1, 0, 1),
    }

    def is_valid(
            self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return set(specification.valid_properties.get("shape", ())) == {
            # ascending
            TAG_String("ascending_east"),
            TAG_String("ascending_north"),
            TAG_String("ascending_south"),
            TAG_String("ascending_west"),
            # straight
            TAG_String("east_west"),
            TAG_String("north_south"),
            # corners
            TAG_String("north_east"),
            TAG_String("north_west"),
            TAG_String("south_east"),
            TAG_String("south_west")
        }

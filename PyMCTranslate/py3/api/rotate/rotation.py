from math import sin, cos, radians

from amulet_nbt import TAG_String

# This is the dictionary stored under the properties key in the specification files
from PyMCTranslate.py3.api.version.translators.block import BlockSpecification

from .rotate import BlockShapes, BaseVectorBlockShape


@BlockShapes.register
class BannerShape(BaseVectorBlockShape):
    Properties = ("rotation",)
    Vectors = {
        (TAG_String(str(rotation)),): (
            sin(radians(rotation * 22.5)),
            0,
            -cos(radians(rotation * 22.5)),
        )
        for rotation in range(16)
    }

    def is_valid(
        self, namespace: str, base_name: str, specification: BlockSpecification
    ) -> bool:
        return set(specification.valid_properties.get("rotation", ())) == {
            TAG_String(str(rotation)) for rotation in range(16)
        }

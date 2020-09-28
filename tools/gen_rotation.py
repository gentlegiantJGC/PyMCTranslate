import os
import json
import glob

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "PyMCTranslate", "json", "versions", "universal", "block", "blockstate", "specification", "universal_minecraft"))

RotationInvariantProperties = (
    "color",
    "material",
    "atomic_number",
    "block_light_level",
    "powered",
    "polished",
    "damage",
    "thickness",
    "leaves",
    "stage",
    "infiniburn",
    "age",
    "bites",
    "mob",
    "eggs",
    "hatch",
    "unstable",
    "underwater",
    "layers",
    "dead",
    "plant",
    "pickles",
    "delay",
    "locked",
    "charges",
    "variant",
    "no_drop",
    "snowy",
    "power",
    "eye",
    "inverted",
    "has_record",
    "chemistry_table_type",
    "lit",
    "cauldron_liquid",
    "level",
    "mode",
    "wet",
    "has_bottle_0",
    "has_bottle_1",
    "has_bottle_2",
    "signal_fire",
    "conditional",
    "occupied",
    "part",
    "honey_level",
    "toggle",
    "coral_type",
    "plant_type",
    "triggered",
    "moisture",
    "update",
    "falling",
    "flowing",
    "check_decay",
    "persistent",
    "stability_checked",
    "bottom",
    "attached",
    "disarmed",
    "suspended"
)

# '[a-z_]+'


if __name__ == '__main__':
    blocks = {}

    for path in glob.glob(os.path.join(root, "*", "*.json")):
        with open(path) as f:
            data = json.load(f)
        properties = data.get("properties", {})
        for key in RotationInvariantProperties:
            if key in properties:
                del properties[key]
        if properties:
            property_tuple = tuple((key, tuple(sorted(value))) for key, value in sorted(properties.items(), key=lambda x: x[0]))
            blocks.setdefault(property_tuple, []).append(os.path.basename(path))

    with open("blockstates.txt", "w") as f:
        f.write(
            str(blocks).replace("((", "\n\t((").replace("}", "\n}")
        )

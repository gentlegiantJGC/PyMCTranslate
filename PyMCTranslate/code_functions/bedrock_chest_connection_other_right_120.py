def main(nbt, properties, location):
    if (
        nbt[0] == "compound"
        and "pairlead" in nbt[1]
        and nbt[1]["pairlead"][0] == "byte"
        and nbt[1]["pairlead"][1] == 1
        and "pairx" in nbt[1]
        and nbt[1]["pairx"][0] == "int"
        and "pairz" in nbt[1]
        and nbt[1]["pairz"][0] == "int"
        and "minecraft:cardinal_direction" in properties
    ):
        dx = nbt[1]["pairx"][1] - location[0]
        dz = nbt[1]["pairz"][1] - location[2]
        if properties["minecraft:cardinal_direction"].py_str == "north":  # north
            if dz == 0:
                if dx == 1:
                    return {"connection": "right"}
        elif properties["minecraft:cardinal_direction"].py_str == "south":  # south
            if dz == 0:
                if dx == -1:
                    return {"connection": "right"}
        elif properties["minecraft:cardinal_direction"].py_str == "west":  # west
            if dx == 0:
                if dz == -1:
                    return {"connection": "right"}
        elif properties["minecraft:cardinal_direction"].py_str == "east":  # east
            if dx == 0:
                if dz == 1:
                    return {"connection": "right"}
    return {}

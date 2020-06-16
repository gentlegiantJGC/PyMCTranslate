def main(nbt, properties, location):
    if nbt[0] == "compound" and \
            "pairlead" in nbt[1] and nbt[1]["pairlead"][0] == "byte" and nbt[1]["pairlead"][1] == 1 and \
            "pairx" in nbt[1] and nbt[1]["pairx"][0] == "int" and \
            "pairz" in nbt[1] and nbt[1]["pairz"][0] == "int" and \
            "facing_direction" in properties:
        dx = nbt[1]["pairx"][1] - location[0]
        dz = nbt[1]["pairz"][1] - location[2]
        if properties["facing_direction"].value == 2:  # north
            if dz == 0:
                if dx == -1:
                    return {"type": "left"}
        elif properties["facing_direction"].value == 3:  # south
            if dz == 0:
                if dx == 1:
                    return {"type": "left"}
        elif properties["facing_direction"].value == 4:  # west
            if dx == 0:
                if dz == 1:
                    return {"type": "left"}
        elif properties["facing_direction"].value == 5:  # east
            if dx == 0:
                if dz == -1:
                    return {"type": "left"}
    return {}

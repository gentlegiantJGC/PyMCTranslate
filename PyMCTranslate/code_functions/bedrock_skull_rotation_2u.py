def main(nbt):
    if nbt[0] == "compound" and "Rotation" in nbt[1] and nbt[1]["Rotation"][0] == "float":
        return {
            "rotation": f"\"{int(nbt[1]['Rotation'][1] // 22.5) % 16}\""
        }
    else:
        return {
            "rotation": "\"0\""
        }

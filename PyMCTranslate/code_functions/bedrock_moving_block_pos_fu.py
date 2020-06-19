def main(nbt, location):
    if nbt[0] == "compound" and "utags" in nbt[1] and nbt[1]["utags"][0] == "compound" and \
            "pistonPosdX" in nbt[1]["utags"][1] and nbt[1]["utags"][1]["pistonPosdX"][0] == "int" and \
            "pistonPosdY" in nbt[1]["utags"][1] and nbt[1]["utags"][1]["pistonPosdY"][0] == "int" and \
            "pistonPosdZ" in nbt[1]["utags"][1] and nbt[1]["utags"][1]["pistonPosdZ"][0] == "int":
        return [
            ["", "compound", [], "pistonPosX", ["int", nbt[1]["utags"][1]["pistonPosdX"][1] + location[0]]],
            ["", "compound", [], "pistonPosY", ["int", nbt[1]["utags"][1]["pistonPosdY"][1] + location[1]]],
            ["", "compound", [], "pistonPosZ", ["int", nbt[1]["utags"][1]["pistonPosdZ"][1] + location[2]]]
        ]
    return []

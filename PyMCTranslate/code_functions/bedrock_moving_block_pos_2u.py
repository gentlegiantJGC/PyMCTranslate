def main(nbt, location):
    if nbt[0] == "compound" and \
            "pistonPosX" in nbt[1] and nbt[1]["pistonPosX"][0] == "int" and \
            "pistonPosY" in nbt[1] and nbt[1]["pistonPosY"][0] == "int" and \
            "pistonPosZ" in nbt[1] and nbt[1]["pistonPosZ"][0] == "int":
        return [
            ["", "compound", [("utags", "compound")], "pistonPosdX", ["int", nbt[1]["pistonPosX"][1] - location[0]]],
            ["", "compound", [("utags", "compound")], "pistonPosdY", ["int", nbt[1]["pistonPosY"][1] - location[1]]],
            ["", "compound", [("utags", "compound")], "pistonPosdZ", ["int", nbt[1]["pistonPosZ"][1] - location[2]]]
        ]
    return []

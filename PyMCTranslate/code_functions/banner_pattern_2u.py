def main(nbt):
    if (
        nbt[0] == "compound"
        and "Patterns" in nbt[1]
        and nbt[1]["Patterns"][0] == "list"
    ):
        return [
            [
                "",
                "compound",
                [("utags", "compound"), ("Patterns", "list"), (index, "compound")],
                "Color",
                ["int", 15 - pattern[1]["Color"][1]],
            ]
            for index, pattern in enumerate(nbt[1]["Patterns"][1])
            if pattern[0] == "compound"
            and "Color" in pattern[1]
            and pattern[1]["Color"][0] == "int"
        ]
    else:
        return []

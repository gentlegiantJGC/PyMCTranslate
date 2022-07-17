def main(properties, location):
    x, _, z = location
    if properties["facing"].py_str == "north":  # north
        return [
            ["", "compound", [], "pairlead", ["byte", 1]],
            ["", "compound", [], "pairx", ["int", x - 1]],
            ["", "compound", [], "pairz", ["int", z]],
        ]
    elif properties["facing"].py_str == "south":  # south
        return [
            ["", "compound", [], "pairlead", ["byte", 1]],
            ["", "compound", [], "pairx", ["int", x + 1]],
            ["", "compound", [], "pairz", ["int", z]],
        ]
    elif properties["facing"].py_str == "west":  # west
        return [
            ["", "compound", [], "pairlead", ["byte", 1]],
            ["", "compound", [], "pairx", ["int", x]],
            ["", "compound", [], "pairz", ["int", z + 1]],
        ]
    elif properties["facing"].py_str == "east":  # east
        return [
            ["", "compound", [], "pairlead", ["byte", 1]],
            ["", "compound", [], "pairx", ["int", x]],
            ["", "compound", [], "pairz", ["int", z - 1]],
        ]
    return []

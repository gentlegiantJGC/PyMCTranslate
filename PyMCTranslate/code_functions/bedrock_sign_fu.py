def main(nbt):
    # ["compound", {"Text": ["string", ""]}]
    if nbt[0] == "compound" and "utags" in nbt[1] and nbt[1]["utags"][0] == "compound":
        text = []
        for l in range(1, 5):
            key = f'Text{l}'
            if key in nbt[1]["utags"][1] and nbt[1]["utags"][1][key][0] == "string":
                text.append(nbt[1]["utags"][1][key][1])
            else:
                text.append("")
    else:
        text = [""] * 4
    text = '\n'.join(text)

    return [["", "compound", [], "Text", ["string", text]]]

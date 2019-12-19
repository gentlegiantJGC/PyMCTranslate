def main(nbt):
    # ["compound", {"Text": ["string", ""]}]
    text = []
    if nbt[0] == "compound" and "Text" in nbt[1] and nbt[1]["Text"][0] == "string":
        lines = nbt[1]["Text"][1].split('\n')
        lines += [""] * (4-len(lines))
        for l in range(1, 5):
            text.append(["", "compound", [("utags", "compound")], f"Text{l}", ["string", lines[l]]])
    else:
        for l in range(1, 5):
            text.append(["", "compound", [("utags", "compound")], "Text" + str(l), ["string", ""]])
    return text

from PyMCTranslate.py3.raw_text import section_string_to_raw_text


def main(nbt):
    raw_text = '""'

    if nbt[0] == "compound" and "CustomName" in nbt[1] and nbt[1]["CustomName"][0] == "string":
        text = nbt[1]["CustomName"][1]
        if text:
            raw_text = section_string_to_raw_text(text)

    return [
        ["", "compound", [("utags", "compound")], "CustomName", ["string", raw_text]]
    ]

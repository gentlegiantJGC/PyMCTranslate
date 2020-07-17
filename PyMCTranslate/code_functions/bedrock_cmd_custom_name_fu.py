from PyMCTranslate.py3.util.raw_text import raw_text_to_section_string


def main(nbt):
    text = ''

    if nbt[0] == "compound" and \
            "utags" in nbt[1] and nbt[1]["utags"][0] == "compound" and \
            "CustomName" in nbt[1]["utags"][0] and nbt[1]["utags"][0]["CustomName"][0] == "string":
        text = raw_text_to_section_string(nbt[1]["utags"][0]["CustomName"][1])

    return [["", "compound", [], "Text", ["string", text]]]

from PyMCTranslate.py3.util.raw_text import raw_text_list_to_section_string


def pack_text(messages):
    lines = []
    for line_number in range(len(messages)):
        tag = messages[line_number]
        if tag[0] == "string":
            lines.append(tag[1])
        else:
            lines.append('{"text":""}')

    return raw_text_list_to_section_string(lines)


def main(nbt):
    front_text = ""

    if nbt[0] == "compound" and "utags" in nbt[1] and nbt[1]["utags"][0] == "compound":
        utags = nbt[1]["utags"][1]
        if (
            "front_text" in utags
            and utags["front_text"][0] == "compound"
            and "messages" in utags["front_text"][1]
            and utags["front_text"][1]["messages"][0] == "list"
        ):
            front_text = pack_text(utags["front_text"][1]["messages"][1])

    return [["", "compound", [], "Text", ["string", front_text]]]

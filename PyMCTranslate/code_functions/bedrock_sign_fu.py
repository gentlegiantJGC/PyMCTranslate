from PyMCTranslate.py3.raw_text import raw_text_list_to_section_string


def main(nbt):
    # ["compound", {"Text": ["string", ""]}]
    if nbt[0] == "compound" and "utags" in nbt[1] and nbt[1]["utags"][0] == "compound":
        lines = []
        line_number = 1
        more_lines = True
        while more_lines:
            key = f'Text{line_number}'
            if key in nbt[1]["utags"][1] and nbt[1]["utags"][1][key][0] == "string":
                lines.append(nbt[1]["utags"][1][key][1])
            elif line_number <= 4:
                lines.append('{"text":""}')
            else:
                more_lines = False
            line_number += 1

        text = raw_text_list_to_section_string(lines)
    else:
        text = ''

    return [["", "compound", [], "Text", ["string", text]]]

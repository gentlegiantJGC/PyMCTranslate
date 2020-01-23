from PyMCTranslate.py3.raw_text import section_string_to_raw_text_list


def main(nbt):
    processed_text = []

    if nbt[0] == "compound" and "Text" in nbt[1] and nbt[1]["Text"][0] == "string":
        text = nbt[1]["Text"][1]
        if text:
            processed_text = section_string_to_raw_text_list(text)

    return [
        ["", "compound", [("utags", "compound")], f"Text{line_num + 1}", ["string", line]] for line_num, line in enumerate(processed_text)
    ]

from PyMCTranslate.py3.util.raw_text import section_string_to_raw_text_list


def main(nbt):
    out = []

    if nbt[0] == "compound" and "Text" in nbt[1] and nbt[1]["Text"][0] == "string":
        text = nbt[1]["Text"][1]
        if text:
            for line_num, line in enumerate(section_string_to_raw_text_list(text)):
                out.append(
                    [
                        "",
                        "compound",
                        [
                            ("utags", "compound"),
                            ("front_text", "compound"),
                            ("messages", "list"),
                        ],
                        line_num,
                        ["string", line],
                    ]
                )

    return out

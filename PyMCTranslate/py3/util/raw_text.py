import json
from typing import List, Union

# section_string is a raw string containing section (§) codes
# raw text is a stringified json object

code_to_colour_map = {
    "0": "black",
    "1": "dark_blue",
    "2": "dark_green",
    "3": "dark_aqua",
    "4": "dark_red",
    "5": "dark_purple",
    "6": "gold",
    "7": "gray",
    "8": "dark_gray",
    "9": "blue",
    "a": "green",
    "b": "aqua",
    "c": "red",
    "d": "light_purple",
    "e": "yellow",
    "f": "white",
}

colour_to_code_map = {val: key for key, val in code_to_colour_map.items()}


def section_string_to_raw_text_list(section_str: str) -> List[str]:
    # convert section_string to list of raw text each element represting one line
    # split input string around newlines and call section_string_to_raw_text for each element
    return [section_string_to_raw_text(line) for line in section_str.split("\n")]


def section_string_to_raw_text(section_str: str) -> str:
    # convert section_string to raw text (including new lines) in string form
    colour = ""
    obfuscated = False
    bold = False
    italic = False
    # strikethrough and underline do not seem to work but they are added anyway
    strikethrough = False
    underline = False

    buffer = []
    processed_text = []
    col = 0

    def append_section():
        nonlocal buffer
        if buffer:
            if obfuscated or bold or italic or strikethrough or underline or colour:
                line_part = {"text": "".join(buffer)}
                for key, val in {
                    "obfuscated": obfuscated,
                    "bold": bold,
                    "italic": italic,
                    "strikethrough": strikethrough,
                    "underlined": underline,
                    "color": colour,
                }.items():
                    if val:
                        line_part[key] = val

                processed_text.append(line_part)
            else:
                processed_text.append("".join(buffer))
            buffer = []

    while col < len(section_str):
        if section_str[col] == "§":
            append_section()
            col += 1
            if col < len(section_str):
                if section_str[col] in code_to_colour_map:
                    colour = code_to_colour_map[section_str[col]]
                    col += 1
                elif section_str[col] == "k":  # obfuscated
                    obfuscated = True
                    col += 1
                elif section_str[col] == "l":  # bold
                    bold = True
                    col += 1
                elif section_str[col] == "m":  # strikethrough
                    strikethrough = True
                    col += 1
                elif section_str[col] == "n":  # underlined
                    underline = True
                    col += 1
                elif section_str[col] == "o":  # italic
                    italic = True
                    col += 1
                elif section_str[col] == "r":  # reset
                    obfuscated = False
                    bold = False
                    strikethrough = False
                    underline = False
                    italic = False
                    colour = ""
                    col += 1
        else:
            buffer.append(section_str[col])
            col += 1

    append_section()
    return json.dumps(processed_text)


def minify_raw_text(obj):
    if isinstance(obj, list):
        if len(obj) == 1:
            return minify_raw_text(obj[0])
        else:
            return [minify_raw_text(o) for o in obj]
    return obj


def raw_text_list_to_section_string(raw_text_list: List[str]) -> str:
    # convert list of raw texts to section_string
    # call raw_text_to_section_string for each element and merge with a newline
    return "\n".join(raw_text_to_section_string(line) for line in raw_text_list)


def raw_text_to_section_string(raw_text: str) -> str:
    # convert raw text to section string
    raw_text_obj = deserialise_raw_text(raw_text)
    colour = ""
    obfuscated = False
    bold = False
    italic = False
    strikethrough = False
    underline = False

    text = []

    for section in raw_text_obj:
        # if a colour is not specified but one was already present
        # or one was specified but is invalid
        if (
            ("color" not in section and colour)
            or ("color" in section and section["color"] not in colour_to_code_map)
            or any(  # or one of these properties is false where it was true before
                not section.get(key, False) and prop
                for key, prop in {
                    "obfuscated": obfuscated,
                    "bold": bold,
                    "italic": italic,
                    "strikethrough": strikethrough,
                    "underlined": underline,
                }.items()
            )
        ):
            colour = ""
            obfuscated = False
            bold = False
            italic = False
            strikethrough = False
            underline = False
            text.append("§r")

        if (
            "color" in section
            and section["color"] in colour_to_code_map
            and section["color"] != colour
        ):
            colour = section["color"]
            text.append(f'§{colour_to_code_map[section["color"]]}')

        if section.get("obfuscated", False) and not obfuscated:
            obfuscated = True
            text.append("§k")
        if section.get("bold", False) and not bold:
            bold = True
            text.append("§l")
        if section.get("italic", False) and not italic:
            italic = True
            text.append("§o")
        if section.get("strikethrough", False) and not strikethrough:
            strikethrough = True
            text.append("§m")
        if section.get("underlined", False) and not underline:
            underline = True
            text.append("§n")

        if "text" in section:
            text.append(section["text"])

    return "".join(text)


def deserialise_raw_text(line: str) -> List[dict]:
    try:
        line = json.loads(line)
    except:
        return [{"text": ""}]
    return _deserialise_raw_text(line)


def _deserialise_raw_text(line: Union[str, dict, list]) -> List[dict]:
    if isinstance(line, str):
        return [{"text": line}]
    elif isinstance(line, list):
        out_line = []
        for section in line:
            out_line += _deserialise_raw_text(section)
        return out_line
    elif isinstance(line, dict):
        out_line = [line]
        if "extra" in line:
            out_line += _deserialise_raw_text(line["extra"])
        return out_line
    return [{"text": ""}]

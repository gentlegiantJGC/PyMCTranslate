import json
from typing import List, Union, overload, Literal

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
    # convert section_string to list of raw text each element representing one line
    return _section_string_to_raw_text(section_str, True)


def section_string_to_raw_text(section_str: str) -> str:
    return _section_string_to_raw_text(section_str, False)


@overload
def _section_string_to_raw_text(
    section_str: str, split_newline: Literal[True]
) -> list[str]: ...


@overload
def _section_string_to_raw_text(
    section_str: str, split_newline: Literal[False]
) -> str: ...


def _section_string_to_raw_text(section_str, split_newline=False):
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
    processed_texts = []

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

    index = 0
    section_str_len = len(section_str)
    while index < section_str_len:
        char = section_str[index]
        if char == "§":
            append_section()
            index += 1
            if index < section_str_len:
                char = section_str[index]
                if char in code_to_colour_map:
                    colour = code_to_colour_map[char]
                    index += 1
                elif char == "k":  # obfuscated
                    obfuscated = True
                    index += 1
                elif char == "l":  # bold
                    bold = True
                    index += 1
                elif char == "m":  # strikethrough
                    strikethrough = True
                    index += 1
                elif char == "n":  # underlined
                    underline = True
                    index += 1
                elif char == "o":  # italic
                    italic = True
                    index += 1
                elif char == "r":  # reset
                    obfuscated = False
                    bold = False
                    strikethrough = False
                    underline = False
                    italic = False
                    colour = ""
                    index += 1
        elif split_newline and char == "\n":
            append_section()
            processed_texts.append(processed_text)
            processed_text = []
            index += 1
        else:
            buffer.append(section_str[index])
            index += 1

    append_section()
    if split_newline:
        if processed_text:
            processed_texts.append(processed_text)
        return list(map(json.dumps, processed_texts))
    else:
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

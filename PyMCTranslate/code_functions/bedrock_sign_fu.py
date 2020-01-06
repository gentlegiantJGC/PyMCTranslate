import json
from typing import Union, List

colour_map = {
    'black': '0',
    'dark_blue': '1',
    'dark_green': '2',
    'dark_aqua': '3',
    'dark_red': '4',
    'dark_purple': '5',
    'gold': '6',
    'gray': '7',
    'dark_gray': '8',
    'blue': '9',
    'green': 'a',
    'aqua': 'b',
    'red': 'c',
    'light_purple': 'd',
    'yellow': 'e',
    'white': 'f'
}


def deserialise_line(line: str) -> List[dict]:
    try:
        line = json.loads(line)
    except:
        return [{"text": ""}]
    return _deserialise_line(line)


def _deserialise_line(line: Union[str, dict, list]) -> List[dict]:
    if isinstance(line, str):
        return [{"text": line}]
    elif isinstance(line, list):
        out_line = []
        for section in line:
            out_line += _deserialise_line(section)
        return out_line
    elif isinstance(line, dict):
        out_line = [line]
        if 'extra' in line:
            out_line += _deserialise_line(line['extra'])
        return out_line
    return [{"text": ""}]


def line_to_string(line: str) -> str:
    line = deserialise_line(line)
    colour = ""
    obfuscated = False
    bold = False
    italic = False
    strikethrough = False
    underline = False

    text = []

    for section in line:
            # if a colour is not specified but one was already present
            # or one was specified but is invalid
        if ('color' not in section and colour) or ('color' in section and section['color'] not in colour_map) or \
                any(  # or one of these properties is false where it was true before
                    not section.get(key, False) and prop for key, prop in {
                        "obfuscated": obfuscated,
                        "bold": bold,
                        "italic": italic,
                        "strikethrough": strikethrough,
                        "underlined": underline
                    }.items()
                ):
            colour = ""
            obfuscated = False
            bold = False
            italic = False
            strikethrough = False
            underline = False
            text.append('§r')

        if 'color' in section and section['color'] in colour_map and section['color'] != colour:
            colour = section["color"]
            text.append(f'§{colour_map[section["color"]]}')

        if section.get("obfuscated", False) and not obfuscated:
            obfuscated = True
            text.append('§k')
        if section.get("bold", False) and not bold:
            bold = True
            text.append('§l')
        if section.get("italic", False) and not italic:
            italic = True
            text.append('§o')
        if section.get("strikethrough", False) and not strikethrough:
            strikethrough = True
            text.append('§m')
        if section.get("underlined", False) and not underline:
            underline = True
            text.append('§n')

        if 'text' in section:
            text.append(section['text'])

    return ''.join(text)


def main(nbt):
    # ["compound", {"Text": ["string", ""]}]
    if nbt[0] == "compound" and "utags" in nbt[1] and nbt[1]["utags"][0] == "compound":
        lines = []
        line_number = 1
        while True:
            key = f'Text{line_number}'
            if key in nbt[1]["utags"][1] and nbt[1]["utags"][1][key][0] == "string":
                lines.append(nbt[1]["utags"][1][key][1])
            elif line_number <= 4:
                lines.append('{"text":""}')
            else:
                break
            line_number += 1

        text = '\n'.join([line_to_string(line) for line in lines])
    else:
        text = ''

    return [["", "compound", [], "Text", ["string", text]]]

import json


def serialise_from_bedrock(obj) -> str:
    obj = _serialise_from_bedrock(obj)
    if not isinstance(obj, str):
        obj = json.dumps(obj)
    return obj


def _serialise_from_bedrock(obj):
    if isinstance(obj, list):
        if len(obj) == 1:
            return _serialise_from_bedrock(obj[0])
        else:
            return [_serialise_from_bedrock(o) for o in obj]
    return obj


colour_map = {
    '0': 'black',
    '1': 'dark_blue',
    '2': 'dark_green',
    '3': 'dark_aqua',
    '4': 'dark_red',
    '5': 'dark_purple',
    '6': 'gold',
    '7': 'gray',
    '8': 'dark_gray',
    '9': 'blue',
    'a': 'green',
    'b': 'aqua',
    'c': 'red',
    'd': 'light_purple',
    'e': 'yellow',
    'f': 'white'
}


def main(nbt):
    processed_text = []

    if nbt[0] == "compound" and "Text" in nbt[1] and nbt[1]["Text"][0] == "string":
        text = nbt[1]["Text"][1]
        if len(text):
            colour = ""
            obfuscated = False
            bold = False
            italic = False
            # strikethrough and underline do not seem to work but they are added anyway
            strikethrough = False
            underline = False

            buffer = []
            col = 0
            line = 0

            def append_section():
                nonlocal buffer
                if buffer:
                    if obfuscated or bold or italic or strikethrough or underline or colour:
                        line_part = {
                            "text": ''.join(buffer)
                        }
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

                        processed_text[line].append(line_part)
                    else:
                        processed_text[line].append(''.join(buffer))
                    buffer = []

            while col < len(text):
                while line >= len(processed_text):
                    processed_text.append([])

                if text[col] == '§':
                    append_section()
                    col += 1
                    if text[col] in colour_map:
                        colour = colour_map[text[col]]
                        col += 1
                    elif text[col] == 'k':  # obfuscated
                        obfuscated = True
                        col += 1
                    elif text[col] == 'l':  # bold
                        bold = True
                        col += 1
                    elif text[col] == 'm':  # strikethrough
                        strikethrough = True
                        col += 1
                    elif text[col] == 'n':  # underlined
                        underline = True
                        col += 1
                    elif text[col] == 'o':  # italic
                        italic = True
                        col += 1
                    elif text[col] == 'r':  # reset
                        obfuscated = False
                        bold = False
                        strikethrough = False
                        underline = False
                        italic = False
                        colour = ""
                        col += 1

                elif text[col] == '\n':
                    append_section()
                    col += 1
                    line += 1

                else:
                    buffer.append(text[col])
                    col += 1

            append_section()

    return [
        ["", "compound", [("utags", "compound")], f"Text{line_num + 1}", ["string", serialise_from_bedrock(line)]] for line_num, line in enumerate(processed_text)
    ]

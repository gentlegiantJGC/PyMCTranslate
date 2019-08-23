# Block Specification JSON Files

Each block must have a specification JSON file attached to it with the name being <block_name>.json (without the namespace).

This must be in the following format. (If an entry is empty it may be omitted but the file must still be present)

```json
{
  "properties": {},
  "defaults": {},
  "nbt": {}
}
```

## Properties

The "properties" key stores a dictionary which maps from property_name to a list of valid options for that property. (all options must be in string form)

The "defaults" key stores a dictionary mapping property_name to the default value for that property. The keys in "properties" and "defaults" must be the same and the default value for each property should be in the list of valid options.

Example: (Universal's cake.json)
```json
{
  "properties": {
    "bites": [
      "0",
      "1",
      "2",
      "3",
      "4",
      "5",
      "6"
    ]
  },
  "defaults": {
    "bites": "0"
  },
  "nbt": {}
}
```

## NBT

The "nbt" entry is a bit more complicated. It is a dictionary mapping from a name (<internal_name>) to another dictionary. This name (<internal_name>) is what the nbt value will be stored under in the input blockstate and can be different to what it is stored as in the actual NBT.

```json
{
  "properties": {},
  "defaults": {},
  "nbt": {
    "<internal_name>": {
      "path": [
        ["<key1>", "<data_type_1>"],
        ["<key2>", "<data_type_2>"]
      ],
      "name": "<nbt_key_name>",
      "type": "<datatype>",
      "default": "<default_value>",
      "options": [
        "<val1>",
        "<val2>"
      ]
    }
  }
}
```

"path": A list of lists containing the path and datatypes to get to the NBT value from the root NBT.

  * "<data_type_1>" should be the string datatype of `nbt[<key1>]` (valid options further down)
  * keys can be string or int depending on if the parent is a compound or list
  * null or undefined to look in the root
    
"name": the key the NBT data is stored under (not to be confused with <internal_name>)

"type": the datatype of the NBT data (valid options are 'byte', 'short', 'int', 'long', 'float', 'double', 'string')

"default": if the value cannot be found then this value will be used instead (must be a string. Will be cast to the output datatype when needed)

"options": a list of all the valid options the nbt tag can hold. Used to create selection dialogues for the user. Undefined or null for an unlimited input based on the datatype.

Example:
```json
{
  "properties": {},
  "defaults": {},
  "nbt": {
    "powered": {
      "name": "powered",
      "type": "byte",
      "options": ["0", "1"],
      "default": "0"
    }
  }
}
```

# Block Mapping JSON Files

Each block should have a JSON file associated with it that converts from the version format to the universal format and back again. For more information on how to read these files see [this file](reader/README.md). This file will document the format of the actual file.

The below is an example that uses all the functions. If a function is not being used it does not need to be written.

```json
{
  "new_block": "<namespace>:<block_name>",
  "new_properties": {},
  "map_properties": {},
  "carry_properties": {},
  "new_nbt": {},
  "map_nbt": {},  
  "multiblock": {},
  "map_block_name": {}
}
```

## new_block

Loads the default properties and nbt from the specification of the block defined and overwrites the previous output block (does not overwrite seperatly added properties or nbt)

At every end point in the mappings a new block should have been defined. If one isn't the input block is returned as the output

`"new_block": "<namespace>:<block_name>"`

## new_properties

Add the given properties with the given values to the output blockstate

```
"new_properties": {
  "<property>": "<val>",
  "<property>": "<val>"
}
```

## map_properties

Based on the property value from the input blockstate run selected functions. The arrows show where further functions can be nested.

```
"map_properties": {
  "<property>": {
    "val1": {
      =>
    },
    "val2": {
      =>
    }
  }
}
```

## carry_properties

For each property in the dictionary if that property's value in the input blockstate is in the list then it is carried over to the output blockstate.

```
"carry_properties": {
  "<property>": ["val1", "val2", ...],
  "<property>": ["val1", "val2", ...]
}
```

## new_nbt

The same as new_properties but with nbt instead of properties

```
"new_nbt": {
  "<internal_name>": "<val>",
  "<internal_name>": "<val>"
}
```

## map_nbt

The same as map_properties but with nbt instead of properties

```
"map_nbt": {
  "<internal_name>": {
    "val1": {
      =>
    },
    "val2": {
      =>
    }
  }
}
```

## multiblock

The most complicated of the functions. Loads up the input blockstate of the block relative to the input block based on the "coords" key and runs further functions using this new blockstate and location.

```
"multiblock": {
  "coords": [dx, dy, dz],
  =>
},
```

can also be a list to do multiple multiblock mappings for the same block.

```
"multiblock": [
  {
    "coords": [dx, dy, dz],
    =>
  },
  {
    "coords": [dx, dy, dz],
    =>
  }
]
```

## map_block_name

Much the same concept as map_properties and map_nbt but with the input block name.

```
"map_block_name": {
  "<namespace>:<block_name>": {
    =>
  },
  "<namespace>:<block_name>": {
    =>
  }
}
```

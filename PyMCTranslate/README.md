# Reader

This is a simple runthrough of how to read the mappings and convert a block. For a code implimentation see [read.py](data_version_handler.py) which may be more up to date. It is advised to pre-load all these files rather than reading them from disk each time.


## Folder Structure
The folders are structured like this: (See [the compiler](/compiler) for more info)

~~~~
- <version_name>
    - block
        - blockstate  (this is always present for all formats. Either the actual format or implemented to mirror the numerical format.)
            (directory with the same format as numerical below)
        - numerical   (this is only present for numerical and psudo-numerical formats)
            - specification   (contains JSON files defining the specification for each file eg valid properties and nbt)
                - <namespace>
                    - <group_name>  (used to split up blocks under the same namespace. EG for chemistry blocks in Bedrock that can be disabled)
                        <block_name>.json
                    - <group_name2> ('vanilla' should be the default group name)
                - <namespace2>
                    
            - to_universal  (the mappings to convert from the version format to the universal format)
                - <namespace>
                    - <group_name>
                        <block_name>.json
                    - <group_name2>
                - <namespace2>
            
            - from_universal  (the mappings to convert from the universal format to the version format)
                - <namespace>  (These namespaces and group_names refer to the universal system.
                                Namespaces should follow the format universal_{namespace})
                    - <group_name>
                        <block_name>.json
                    - <group_name2>
                - <namespace2>
    __init__.json
    __numerical_block_map__.json (needed only for the "numerical" format)
~~~~

## Setting up for Conversion to Universal

1. Find the version for the format the block is coming from. Check the 'format' key in the `__init__.json` file.

2. If the format is numerical then look up the numerical id in `__numerical_block_map__.json` to convert to a string id (used to put meaning to the numbers).

    * Pass if psudo-numerical or blockstate format.
    
3. Split the block id string about the ':' character (there should only be 1) to give `<namespace>` and `<block_name>`.

4. Find the specification for the block and load in any missing properties from the defaults. It may also have NBT that needs to be loaded.
    * For numerical and psudo-numerical in `<version_name>/block/numerical/specification/<namespace>/<group_name>/<block_name>.json` (it should only be found in one group_name and it should really be loaded beforehand so this isn't an issue)
    * For blockstate in `<version_name>/block/blockstate/specification/<namespace>/<group_name>/<block_name>.json`
    
5. Find the mappings to_universal in a similar way to the specification in 4. See 'Reading Mappings' below to do the actual conversion.


## Setting up for a Conversion from Universal

1. Split the block id string about the ':' character (there should only be 1) to give `<namespace>` and `<block_name>`.

2. Find the specification for the block and load in any missing properties from the defaults.
    * `universal/block/blockstate/specification/<namespace>/<group_name>/<block_name>.json`

3. Find the mappings from_universal. See 'Reading Mappings' below to do the actual conversion.
    * For numerical and psudo-numerical in `<version_name>/block/numerical/from_universal/<namespace>/<group_name>/<block_name>.json` (it should only be found in one group_name and it should really be loaded beforehand so this isn't an issue)
    * For blockstate in `<version_name>/block/blockstate/from_universal/<namespace>/<group_name>/<block_name>.json` (also present for the numerical formats to replace the numerical format)


## Reading Mappings

See the [mappings documentation](/mappings_documentation.md) for info on the specification and mapping formats. The below will explain how to read them.

(This assumes it is being done individual block by individual block but for most blocks the mapping will only be dependent on the blockstate so all blocks with the same blockstate can be done at once)

1. Create an empty __output_blockstate__ like this {"block_name": null, "properties": {}, "nbt": {}}

2. Create another dictionary storing __new__ properties and nbt like this {"properties": {}, "nbt": {}}   (properties added straight to the blockstate may get overwritten)

3. If "new_block" in mappings

    * find the specification in the output format and overwrite the __output_blockstate__ with its default properties
    
4. If "new_properties" in mappings

    * load all the defined new properties into __new__
    
5. If "new_nbt" in mappings

    * load all the defined new nbt into __new__
    
6. If "carry_properties" in mappings

    * for all keys in "carry_properties" if that property is in the input blockstate and the value of that property is in the list then carry it to the __new__ properties

7. If "multiblock" in mappings (this requires knowing the location of the block and the ability to reach back into the world)

    * should be a dictionary of a list of dictionaries. Do this for all the dictionaries.

    * get the block in the input format at location "coords" relative to the current location.
    
    * go to the top with the new block, block location and dictionary as the new mapping.
    
    * merge any data created into __new__ and overwrite __output_blockstate__ if the one returned is not null
    
8. If "map_properties" in mappings

    * for all keys in "map_properties" if that property is in the input blockstate and the value of that property is in the dictionary then take the resulting dictionary as the mappings and the current input block and go to the top.
    
    * merge any data created into __new__ and overwrite __output_blockstate__ if the one returned is not null
    
9. If "map_block_name" in mappings

    * look up the input block name in the mappings. If present go to the top with the new mappings and the current input block.
   
    * merge any data created into __new__ and overwrite __output_blockstate__ if the one returned is not null
    
10. If "map_nbt" in mappings (when setting up for conversion the nbt should have been loaded from the world)

    * the same as 8 but with nbt rather than properties
    
11. Return the __output_blockstate__ and __new__ (but don't merge them here)

Some of the mapping functions allow nesting so there should be another function that calls the above and at the very end merges __new__ into __output_blockstate__ and that is the final blockstate in the output version.

Note that sometimes the mappings will fail perhaps because an invalid input blockstate is given. In these cases the input blockstate should be given as the output so that if converted back to the input version no data will be lost. The user can also be asked what they want done with it.
    
## Feature Set

When converting from version to universal all bar "new_nbt" can be used. The universal format should not contain any nbt data. Store it as a property instead.

When converting from universal to version format "map_nbt" and "multiblock" may not be used. The universal blockstate should be self contained and not require external data.




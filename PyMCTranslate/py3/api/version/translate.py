from typing import Union, Tuple, List, Dict, Callable, TYPE_CHECKING, Type, Optional

import amulet_nbt
from amulet_nbt import (
    NBTFile,
    TAG_Byte,
    TAG_Short,
    TAG_Int,
    TAG_Long,
    TAG_Float,
    TAG_Double,
    TAG_Byte_Array,
    TAG_String,
    TAG_List,
    TAG_Compound,
    TAG_Int_Array,
    TAG_Long_Array,
)

from PyMCTranslate.py3.api import Block, BlockEntity, Entity, ChunkLoadError
from PyMCTranslate.py3.log import log
from PyMCTranslate.py3.api.version import code_functions

if TYPE_CHECKING:
    from numpy import ndarray
    from PyMCTranslate.py3.api.version import Version

BlockCoordinates = Tuple[int, int, int]


def get_block_at(
    relative_location: BlockCoordinates,
) -> Tuple[Union[Block, None], Union[BlockEntity, None]]:
    """A callback to access data from the world
	Implement a function with this specification and give it to the translate function
	to have the code reach back into the world if required.
	"""
    return None, None


AnyNBTClass = Union[
    Type[TAG_Byte],
    Type[TAG_Short],
    Type[TAG_Int],
    Type[TAG_Long],
    Type[TAG_Float],
    Type[TAG_Double],
    Type[TAG_Byte_Array],
    Type[TAG_String],
    Type[TAG_List],
    Type[TAG_Compound],
    Type[TAG_Int_Array],
    Type[TAG_Long_Array],
]


_datatype_to_nbt: Dict[str, AnyNBTClass] = {
    "byte": TAG_Byte,
    "short": TAG_Short,
    "int": TAG_Int,
    "long": TAG_Long,
    "float": TAG_Float,
    "double": TAG_Double,
    "byte_array": TAG_Byte_Array,
    "string": TAG_String,
    "list": TAG_List,
    "compound": TAG_Compound,
    "int_array": TAG_Int_Array,
    "long_array": TAG_Long_Array,
}

_nbt_to_datatype = {
    "TAG_Byte": "byte",
    "TAG_Short": "short",
    "TAG_Int": "int",
    "TAG_Long": "long",
    "TAG_Float": "float",
    "TAG_Double": "double",
    "TAG_Byte_Array": "byte_array",
    "TAG_String": "string",
    "TAG_List": "list",
    "TAG_Compound": "compound",
    "TAG_Int_Array": "int_array",
    "TAG_Long_Array": "long_array",
}

_int_to_nbt = [
    None,
    TAG_Byte,
    TAG_Short,
    TAG_Int,
    TAG_Long,
    TAG_Float,
    TAG_Double,
    TAG_Byte_Array,
    TAG_String,
    TAG_List,
    TAG_Compound,
    TAG_Int_Array,
    TAG_Long_Array,
]
_int_to_datatype = [
    None,
    "byte",
    "short",
    "int",
    "long",
    "float",
    "double",
    "byte_array",
    "string",
    "list",
    "compound",
    "int_array",
    "long_array",
]


def datatype_to_nbt(datatype: str) -> AnyNBTClass:
    return _datatype_to_nbt[datatype]


def nbt_to_datatype(nbt: amulet_nbt.BaseValueType) -> str:
    return _nbt_to_datatype[nbt.__class__.__name__]


def index_nbt(
    nbt: NBTFile, nbt_path: Tuple[str, str, List[Tuple[Union[str, int], str]]]
):
    outer_name, outer_type, nbt_path = nbt_path
    if (
        not isinstance(nbt, NBTFile)
        or nbt.name != outer_name
        or not isinstance(nbt.value, datatype_to_nbt(outer_type))
    ):
        return None
    nbt = nbt.value

    for path, nbt_type in nbt_path:
        if isinstance(path, int) and isinstance(nbt, TAG_List) and len(nbt) > path:
            nbt = nbt[path]
        elif isinstance(path, str) and isinstance(nbt, TAG_Compound) and path in nbt:
            nbt = nbt[path]
        else:
            return None
    return nbt


def nbt_from_list(
    outer_name: str,
    outer_type: str,
    nbt_list: List[
        Tuple[
            str,
            str,
            List[Tuple[Union[str, int], str]],
            Union[str, int],
            Union[
                TAG_Byte,
                TAG_Short,
                TAG_Int,
                TAG_Long,
                TAG_Float,
                TAG_Double,
                TAG_Byte_Array,
                TAG_String,
                TAG_List,
                TAG_Compound,
                TAG_Int_Array,
                TAG_Long_Array,
            ],
        ]
    ],
    default_template: str = None,
) -> NBTFile:

    if default_template is not None:
        nbt_object = amulet_nbt.from_snbt(default_template)
    else:
        nbt_object = datatype_to_nbt(outer_type)()

    for nbt_entry in nbt_list:
        outer_name_, outer_type_, nbt_path, data_path, data = nbt_entry
        if outer_name == outer_name_ and outer_type == outer_type_:
            nbt_temp: Union[
                TAG_Byte,
                TAG_Short,
                TAG_Int,
                TAG_Long,
                TAG_Float,
                TAG_Double,
                TAG_Byte_Array,
                TAG_String,
                TAG_List,
                TAG_Compound,
                TAG_Int_Array,
                TAG_Long_Array,
            ] = nbt_object
            for path, nbt_type in nbt_path:
                # if the nested NBT object does not exist then create it
                if isinstance(nbt_temp, TAG_Compound):
                    if (
                        path not in nbt_temp
                        or nbt_to_datatype(nbt_temp[path]) != nbt_type
                    ):
                        nbt_temp[path] = datatype_to_nbt(nbt_type)()

                elif isinstance(nbt_temp, TAG_List):
                    # if the list is a different type to nbt_type replace it with nbt_type
                    if (
                        _int_to_datatype[int(nbt_temp.list_data_type)] != nbt_type
                        and len(nbt_temp) > 0
                    ):
                        nbt_temp.list_data_type = datatype_to_nbt(nbt_type).tag_id
                        for index in range(len(nbt_temp)):
                            nbt_temp[index] = datatype_to_nbt(nbt_type)()

                    # pad out the list to the length of path
                    if path + 1 > len(nbt_temp):
                        # pad out the list to the length of the index
                        for _ in range(path + 1 - len(nbt_temp)):
                            nbt_temp.insert(datatype_to_nbt(nbt_type)())
                    # we now should have a TAG_List of the same type as nbt_type and length as path

                nbt_temp = nbt_temp[path]

            if isinstance(nbt_temp, TAG_Compound):
                nbt_temp[data_path] = data

            elif isinstance(nbt_temp, TAG_List):
                # if the list is a different type to data replace it with type(data)
                if nbt_temp.list_data_type != data.tag_id and len(nbt_temp) > 0:
                    nbt_temp.list_data_type = data.tag_id
                    for index in range(len(nbt_temp)):
                        nbt_temp[index] = data.__class__()

                # pad out the list to the length of path
                if data_path + 1 > len(nbt_temp):
                    # pad out the list to the length of the index
                    for _ in range(data_path + 1 - len(nbt_temp)):
                        nbt_temp.append(data.__class__())
                # we now should have a TAG_List of the same type as nbt_type and length as data_path
                nbt_temp[data_path] = data

            # TODO:
            # elif isinstance(nbt_temp, TAG_Byte_Array) and isinstance(data, TAG_Byte):
            # 	# pad to the length of data_path if less than the current length
            # 	# nbt_temp[data_path] = data.value
            # elif isinstance(nbt_temp, TAG_Int_Array) and isinstance(data, TAG_Int):
            # elif isinstance(nbt_temp, TAG_Long_Array) and isinstance(data, TAG_Long):

    return NBTFile(nbt_object, outer_name)


def translate(
    object_input: Union[Block, Entity],
    input_spec: dict,
    mappings: List[dict],
    output_version: "Version",
    force_blockstate: bool,
    get_block_callback: Callable[
        [BlockCoordinates], Tuple[Block, Union[None, BlockEntity]]
    ] = None,
    extra_input: BlockEntity = None,
    pre_populate_defaults: bool = True,
    block_location: Optional[BlockCoordinates] = None,
) -> Tuple[Union[Block, Entity], Union[BlockEntity, None], bool, bool]:
    """
		A function to translate the object input to the output version

		:param object_input: the Block or Entity object to be converted
		:param input_spec: the specification for the object_input from the input block_format
		:param mappings: the mapping file for the input_object
		:param output_version: A way for the function to look at the specification being converted to. (used to load default properties)
		:param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same thing)
		:param get_block_callback: see get_block_at function at the top for a template
		:param extra_input: secondary to the object_input a block entity can be given. This should only be used in the select block tool or plugins. Not compatible with location
		:param pre_populate_defaults: should the nbt structure (if exists) be populated with the default values
		:param block_location: optional coordinate of where the block is in the world. Used in very few situations.
		:return: output, extra_output, extra_needed, cacheable
			extra_needed: a bool to specify if more data is needed beyond the object_input
			cacheable: a bool to specify if the result can be cached to reduce future processing
			Block, None, bool, bool
			Block, BlockEntity, bool, bool
			Entity, None, bool, bool
	"""

    if block_location is not None:
        block_location = (  # force block locations to be ints
            int(block_location[0]),
            int(block_location[1]),
            int(block_location[2]),
        )

    # set up for the _translate function which does the actual conversion
    if isinstance(object_input, Block):
        block_input = object_input

        if (
            extra_input is None
            and "snbt" in input_spec
            and get_block_callback is not None
        ):
            # if the callback function is defined then load the BlockEntity from the world
            extra_input = get_block_callback((0, 0, 0))[1]
            if extra_input is None:
                # if BlockEntity is still None create it based off the specification
                namespace, base_name = input_spec["nbt_identifier"]
                extra_input = BlockEntity(
                    namespace,
                    base_name,
                    0,
                    0,
                    0,
                    NBTFile(amulet_nbt.from_snbt(input_spec["snbt"])),
                )
            nbt_input = extra_input.nbt

        elif extra_input is not None:
            # if the BlockEntity is already defined in extra_input continue with that
            assert isinstance(extra_input, BlockEntity)
            nbt_input = extra_input.nbt
        else:
            # if callback and extra_input are both None then continue with the mapping as normal but without the BlockEntity.
            # The mappings will do as much as it can and will return the extra_needed flag as True telling the caller to run with callback if possible
            nbt_input = None

    elif isinstance(object_input, Entity):
        assert (
            extra_input is None
        ), "When an Entity is the first input the extra input must be None"
        block_input = None
        nbt_input = object_input.nbt
    else:
        raise Exception

    # run the conversion
    output_name, output_type, new_data, extra_needed, cacheable = _translate(
        block_input, nbt_input, mappings, get_block_callback, block_location
    )

    # sort out the outputs from the _translate function
    extra_output = None
    if output_type == "block":
        # we should have a block output
        # create the block object based on output_name and new['properties']
        namespace, base_name = output_name.split(":", 1)
        spec = output_version.block.get_specification(
            namespace, base_name, force_blockstate
        )
        properties = spec.get("defaults", {})

        # cast to NBT
        properties = {
            prop: amulet_nbt.from_snbt(val) for prop, val in properties.items()
        }

        for key, val in new_data["properties"].items():
            properties[key] = val
        output = Block(namespace, base_name, properties)

        if "snbt" in spec:
            namespace, base_name = spec.get("nbt_identifier", ["unknown", "unknown"])

            if pre_populate_defaults:
                nbt = nbt_from_list(
                    spec.get("outer_name", ""),
                    spec.get("outer_type", "compound"),
                    new_data["nbt"],
                    spec.get("snbt", "{}"),
                )

            else:
                nbt = nbt_from_list(
                    spec.get("outer_name", ""),
                    spec.get("outer_type", "compound"),
                    new_data["nbt"],
                )

            extra_output = BlockEntity(namespace, base_name, 0, 0, 0, nbt)
            # not quite sure how to handle coordinates here.
            # it makes sense to me to have the wrapper program set the coordinates so none are missed.
        elif new_data["nbt"]:
            log.warning(
                f"New nbt present but no output block entity\nin:{object_input.blockstate}\nout:{output.blockstate}"
            )

    elif output_type == "entity":
        # we should have an entity output
        # create the entity object based on output_name and new['nbt']
        namespace, base_name = output_name.split(":", 1)
        spec = output_version.entity.get_specification(
            namespace, base_name, force_blockstate
        )

        if pre_populate_defaults:
            nbt = nbt_from_list(
                spec.get("outer_name", ""),
                spec.get("outer_type", "compound"),
                new_data["nbt"],
                spec.get("snbt", "{}"),
            )

        else:
            nbt = nbt_from_list(
                spec.get("outer_name", ""),
                spec.get("outer_type", "compound"),
                new_data["nbt"],
            )

        output = Entity(namespace, base_name, 0.0, 0.0, 0.0, nbt)

    else:
        raise Exception("No output object given.")
    return output, extra_output, extra_needed, cacheable


def _translate(
    block_input: Union[Block, None],
    nbt_input: Union[NBTFile, None],
    mappings: List[dict],
    get_block_callback: Callable = None,
    absolute_location: BlockCoordinates = (0, 0, 0),
    relative_location: BlockCoordinates = (0, 0, 0),
    nbt_path: Tuple[str, str, List[Tuple[Union[str, int], str]]] = None,
    inherited_data: Tuple[Union[str, None], Union[str, None], dict, bool, bool] = None,
) -> Tuple[Union[str, None], Union[str, None], dict, bool, bool]:
    """
	:param block_input:
	:param nbt_input:
	:param mappings:
	:param get_block_callback:
	:param absolute_location:
	:param relative_location:
	:param inherited_data:
	:return:
		output_name - string of the object being output
		output_type - string of the type output name is (should be 'block' or 'entity')
		new - a dictionary that looks like this {'properties': {}, 'nbt': []}
		extra_needed - bool. Specifies if more data is needed (ie if the block callback needs to be given to do a full map)
		cacheable - bool. Specifies if the input object is cachable. Only true for simple Blocks without BlockEntities
	"""
    output_name: Optional[str]

    if inherited_data is not None:
        output_name, output_type, new_data, extra_needed, cacheable = inherited_data
    else:
        output_name = None
        output_type = None
        new_data = {
            "properties": {},
            "nbt": [],
        }  # There could be multiple 'new_block' functions in the mappings so new properties are put in here and merged at the very end
        new_data["nbt"]: List[
            Tuple[
                str,
                str,
                List[Union[str, int], str],
                Union[str, int],
                Union[
                    TAG_Byte,
                    TAG_Short,
                    TAG_Int,
                    TAG_Long,
                    TAG_Float,
                    TAG_Double,
                    TAG_Byte_Array,
                    TAG_String,
                    TAG_List,
                    TAG_Compound,
                    TAG_Int_Array,
                    TAG_Long_Array,
                ],
            ]
        ]
        """
		new['nbt'] = [
			[
				[
					[path0, type0],
					[path1, type1],
					...
				],
				path_n,
				NBT
			],
			...
		]
		"""
        extra_needed = False  # used to determine if extra data is required (and thus to do block by block)
        cacheable = True  # cacheable until proven otherwise

    for translate_function in mappings:
        function_name = translate_function["function"]

        if "new_block" == function_name:
            # {
            # 	"function": "new_block",
            # 	"options": "<namespace>:<base_name>"
            # }
            output_name = translate_function["options"]
            output_type = "block"

        elif "new_entity" == function_name:
            # {
            # 	"function": "new_entity",
            # 	"options": "<namespace>:<base_name>"
            # }
            output_name = translate_function["options"]
            output_type = "entity"

        elif "new_properties" == function_name:
            # {
            # 	"function": "new_properties",
            # 	"options": {
            # 		"<property_name>": "<SNBT>",  # eg "val", "54b"
            # 	}
            # }
            for key, val in translate_function["options"].items():
                new_data["properties"][key] = amulet_nbt.from_snbt(val)

        elif "carry_properties" == function_name:
            # {
            # 	"function": "carry_properties",
            # 	"options": {
            # 		"<property_name>": ["<property_value"],
            # 		"<nbt_property_name>": ['<SNBT>']
            # 	}
            # }
            assert isinstance(block_input, Block), "The block input is not a block"
            for key in translate_function["options"]:
                if key in block_input.properties:
                    val = block_input.properties[key]
                    if isinstance(val, amulet_nbt.BaseValueType):
                        hash_val = val.to_snbt()
                    else:
                        continue
                    if hash_val in translate_function["options"][key]:
                        new_data["properties"][key] = val

        elif "map_properties" == function_name:
            # {
            # 	"function": "map_properties",
            # 	"options": {
            # 		"<property_name>": {
            # 			"<SNBT>": [
            # 				<functions>
            # 			]
            # 		}
            # 	}
            # }
            assert isinstance(block_input, Block), "The block input is not a block"
            for key in translate_function["options"]:
                if key in block_input.properties:
                    val = block_input.properties[key]
                    if isinstance(val, amulet_nbt.BaseValueType):
                        val = val.to_snbt()
                    else:
                        continue
                    if val in translate_function["options"][key]:
                        (
                            output_name,
                            output_type,
                            new_data,
                            extra_needed,
                            cacheable,
                        ) = _translate(
                            block_input,
                            nbt_input,
                            translate_function["options"][key][val],
                            get_block_callback,
                            absolute_location,
                            relative_location,
                            nbt_path,
                            (
                                output_name,
                                output_type,
                                new_data,
                                extra_needed,
                                cacheable,
                            ),
                        )

        elif "multiblock" == function_name:
            # {
            # 	"function": "multiblock",
            # 	"options": [
            # 		{
            # 			"coords": [dx, dy, dz],
            # 			"functions": <functions>
            # 		}
            # 	]
            # }
            cacheable = False
            if get_block_callback is None:
                extra_needed = True
            else:
                multiblocks = translate_function["options"]
                if isinstance(multiblocks, dict):
                    multiblocks = [multiblocks]
                for multiblock in multiblocks:
                    new_location = (
                        relative_location[0] + multiblock["coords"][0],
                        relative_location[1] + multiblock["coords"][1],
                        relative_location[2] + multiblock["coords"][2],
                    )
                    new_absolute_location = (
                        absolute_location[0] + multiblock["coords"][0],
                        absolute_location[1] + multiblock["coords"][1],
                        absolute_location[2] + multiblock["coords"][2],
                    )
                    try:
                        block_input_, nbt_input_ = get_block_callback(new_location)
                        if nbt_input_ is not None:
                            nbt_input_ = nbt_input_.nbt
                        (
                            output_name,
                            output_type,
                            new_data,
                            extra_needed,
                            cacheable,
                        ) = _translate(
                            block_input_,
                            nbt_input_,
                            multiblock["functions"],
                            get_block_callback,
                            new_absolute_location,
                            new_location,
                            nbt_path,
                            (
                                output_name,
                                output_type,
                                new_data,
                                extra_needed,
                                cacheable,
                            ),
                        )
                    except ChunkLoadError:
                        continue

        elif "map_block_name" == function_name:
            # {
            # 	"function": "map_block_name",
            # 	"options": {
            # 		"<namespace>:<base_name>": [
            # 			<functions>
            # 		]
            # 	}
            # }
            assert isinstance(
                block_input, Block
            ), f"The block input {block_input} is not a block"
            block_name = f"{block_input.namespace}:{block_input.base_name}"
            if block_name in translate_function["options"]:
                (
                    output_name,
                    output_type,
                    new_data,
                    extra_needed,
                    cacheable,
                ) = _translate(
                    block_input,
                    nbt_input,
                    translate_function["options"][block_name],
                    get_block_callback,
                    absolute_location,
                    relative_location,
                    nbt_path,
                    (output_name, output_type, new_data, extra_needed, cacheable),
                )

        elif "walk_input_nbt" == function_name:
            # This is a special function unlike the others. See _convert_walk_input_nbt for more information
            # {
            # 	"function": "walk_input_nbt",
            #   "outer_name": "",  # defaults to this if undefined
            # 	"options": {
            # 		"type": "<nbt type>",  # check that the nbt is of this type
            # 		"self_default": [],  # if the type is different run these functions : defaults to [{"function": "carry_nbt"}] which carries everything
            # 	    "functions": [],  # functions to run if defined
            #
            # 		"keys": {  # only for compound type
            # 	        str: {nested options format}
            # 		},
            #       "index": {  # only for list or array types
            # 	        str(<int>): {nested options format}     (type should not be defined for nested array types)
            # 	    },
            # 	    "nested_default": []  # only for compound, list or array types.
            # 	        If nested key/index is not in respective dictionary run these functions on them.
            #           If undefined defaults to [{"function": "carry_nbt"}] which carries everything
            # 	}
            # }
            cacheable = False
            if nbt_input is None:
                extra_needed = True
            else:
                custom_nbt_path = translate_function.get("path", [])
                if custom_nbt_path:
                    nbt_temp = index_nbt(nbt_input, ("", "compound", custom_nbt_path))
                    if nbt_temp is None:
                        log.error(f"Expected nbt data at {custom_nbt_path}")
                    elif not isinstance(
                        nbt_temp, datatype_to_nbt(custom_nbt_path[-1][-1])
                    ):
                        log.error(
                            f"Expected nbt data at {custom_nbt_path} to be an {custom_nbt_path[-1][-1]} tag but got {nbt_temp.__class__.__name__}"
                        )
                    else:
                        (
                            output_name,
                            output_type,
                            new_data,
                            extra_needed,
                            cacheable,
                        ) = _convert_walk_input_nbt(
                            block_input,
                            nbt_input,
                            translate_function["options"],
                            get_block_callback,
                            absolute_location,
                            relative_location,
                            ("", "compound", custom_nbt_path),
                            (
                                output_name,
                                output_type,
                                new_data,
                                extra_needed,
                                cacheable,
                            ),
                        )

                else:
                    (
                        output_name,
                        output_type,
                        new_data,
                        extra_needed,
                        cacheable,
                    ) = _convert_walk_input_nbt(
                        block_input,
                        nbt_input,
                        translate_function["options"],
                        get_block_callback,
                        absolute_location,
                        relative_location,
                        nbt_path,
                        (output_name, output_type, new_data, extra_needed, cacheable),
                    )

        elif "new_nbt" == function_name:
            # when used outside walk_input_nbt
            # {
            # 	"function": "new_nbt",
            # 	"options": [
            # 		{
            #           "outer_name": "",  # defaults to this if undefined
            #           "outer_type": "compound",  # defaults to this if undefined
            # 			"path": [ # optional. Defaults to the root
            # 				[ < path1 >: Union[str, int], < datatype1 >: str]
            # 			]
            # 			"key": <key>: str or int,
            # 			"value": "<SNBT>"
            # 		}
            # 	]
            # }

            # when used inside walk_input_nbt
            # {
            # 	"function": "new_nbt",
            # 	"options": [
            # 		{
            #           "outer_name": "",  # defaults to this if undefined
            #           "outer_type": "compound",  # defaults to this if undefined
            # 			"path": [ # optional. [] to be the root, undefined to be the input path
            # 				[ < path1 >: Union[str, int], < datatype1 >: str]
            # 			]
            # 			"key": <key>: Union[str, int],
            # 			"value": "<SNBT>"
            # 		}
            # 	]
            # }

            new_nbts = translate_function["options"]
            if isinstance(new_nbts, dict):
                new_nbts = [new_nbts]

            for new_nbt in new_nbts:
                if "path" in new_nbt:
                    path = new_nbt["path"]
                elif nbt_path is None:
                    path = []
                else:
                    path = nbt_path[2]

                outer_name = new_nbt.get("outer_name", "")
                outer_type = new_nbt.get("outer_type", "compound")

                new_data["nbt"].append(
                    (
                        outer_name,
                        outer_type,
                        path,
                        new_nbt["key"],
                        amulet_nbt.from_snbt(new_nbt["value"]),
                    )
                )

        elif "carry_nbt" == function_name:
            # only works within walk_input_nbt
            # {
            # 	"function": "carry_nbt",
            # 	"options": {
            # 		"outer_name": "",  # defaults to this if undefined
            # 		"outer_type": "compound",  # defaults to this if undefined
            # 		"path": [  # [] to be the root, undefined to be the input path
            # 			[ <path1>: Union[str, int], <datatype1>: str],
            # 			...
            # 		],
            # 		"key": <key>: Union[str, int]  # undefined to remain under the same key/index
            # 		"type": <type>: str  # undefined to remain as the input type
            # 	}
            # }
            cacheable = False
            if nbt_input is None:
                extra_needed = True
            elif nbt_path is not None:
                nbt = index_nbt(nbt_input, nbt_path)
                if nbt is None:
                    raise Exception(
                        "This code should not be run because it should be caught by other code before it gets here."
                    )
                val = nbt.value

                options = translate_function.get("options", {})
                outer_name = options.get("outer_name", "")
                outer_type = options.get("outer_type", "compound")
                path = options.get("path", nbt_path[2][:-1])
                key = options.get("key", nbt_path[2][-1][0])
                nbt_type = options.get("type", nbt_path[2][-1][1])

                # TODO: some kind of check to make sure that the input data type nbt_path[-1][1] can be cast to nbt_type
                #  perhaps this should be done in the compiler rather than at runtime
                new_data["nbt"].append(
                    (outer_name, outer_type, path, key, datatype_to_nbt(nbt_type)(val))
                )

        elif "map_nbt" == function_name:
            # {
            # 	"function": "map_nbt",
            # 	"options": {  # based on the input nbt value at path (should only be used with end stringable datatypes)
            # 		"cases": {},  # if the data is in here then do the nested functions
            # 		"default": []  # if the data is not in cases or cases is not defined then do these functions
            # 	}
            # }

            cacheable = False
            if nbt_input is None:
                extra_needed = True
            elif nbt_path is not None:
                run_default = True
                if "cases" in translate_function["options"]:
                    nbt = index_nbt(nbt_input, nbt_path)
                    nbt_hash = nbt.to_snbt()
                    if nbt_hash in translate_function["options"]["cases"]:
                        (
                            output_name,
                            output_type,
                            new_data,
                            extra_needed,
                            cacheable,
                        ) = _translate(
                            block_input,
                            nbt_input,
                            translate_function["options"]["cases"][nbt_hash],
                            get_block_callback,
                            absolute_location,
                            relative_location,
                            nbt_path,
                            (
                                output_name,
                                output_type,
                                new_data,
                                extra_needed,
                                cacheable,
                            ),
                        )
                        run_default = False

                if run_default and "default" in translate_function["options"]:
                    (
                        output_name,
                        output_type,
                        new_data,
                        extra_needed,
                        cacheable,
                    ) = _translate(
                        block_input,
                        nbt_input,
                        translate_function["options"]["default"],
                        get_block_callback,
                        absolute_location,
                        relative_location,
                        nbt_path,
                        (output_name, output_type, new_data, extra_needed, cacheable),
                    )

        elif "code" == function_name:
            # {
            # 	"function": "code",  # when all the other functions fail you this should do what you need. Use as sparingly as possible
            # 	"options": {
            # 		"input": ["namespace", "base_name", "properties", "nbt"],  # all of these inputs and output are optional. Change these lists to modify
            # 		"output": ["output_name", "output_type", "new_properties", "new_nbt"],
            # 		"function": "function_name"  # this links to a lua funciton in the lua directory with the file name function_name.lua
            # 	}
            # }

            # this function was originally designed to be lua code but I have now switched it to python because lua is hard :(
            # Might swap back one day
            # this would be in function_name.py
            # def main(namespace, base_name, properties, nbt)
            #   return "minecraft:air", "block", {"property_name": "property_name"}, []

            # usage examples:
            #   splitting and merging strings in signs

            cacheable = False

            options = translate_function["options"]

            function_inputs = []
            for inp in options.get("input", []):
                if inp == "namspace":
                    function_inputs.append(block_input.namespace)
                elif inp == "base_name":
                    function_inputs.append(block_input.base_name)
                elif inp == "properties":
                    function_inputs.append(block_input.properties)
                elif inp == "nbt":
                    if nbt_input is None:
                        extra_needed = True
                        function_inputs.append(["compound", {}])
                    else:
                        function_inputs.append(objectify_nbt(nbt_input))
                elif inp == "location":
                    function_inputs.append(absolute_location)

            function_output = code_functions.run(options["function"], function_inputs)
            if not isinstance(function_output, tuple):
                function_output = (function_output,)

            for out, out_name in zip(function_output, options["output"]):
                if out_name == "output_name":
                    assert isinstance(out, str)
                    output_name = out
                elif out_name == "output_type":
                    assert isinstance(out, str)
                    output_type = out
                elif out_name == "new_properties":
                    assert isinstance(out, dict)
                    for key, val in out.items():
                        new_data["properties"][key] = amulet_nbt.from_snbt(val)
                elif out_name == "new_nbt":
                    assert isinstance(out, list)
                    for val in out:
                        assert len(val) == 5
                        new_data["nbt"].append(
                            tuple(val[:4]) + (unobjectify_nbt(val[4]),)
                        )

    return output_name, output_type, new_data, extra_needed, cacheable


def objectify_nbt(nbt: NBTFile) -> Tuple[str, dict]:
    return _objectify_nbt(nbt.value)


def _objectify_nbt(nbt: amulet_nbt.AnyNBT) -> Tuple[str, Union[dict, list, int, str]]:
    nbt_type = nbt_to_datatype(nbt)
    nbt_data = nbt.value
    if isinstance(nbt_data, dict):
        return nbt_type, {key: _objectify_nbt(nbt_) for key, nbt_ in nbt_data.items()}
    elif isinstance(nbt_data, list):
        return nbt_type, [_objectify_nbt(nbt_) for nbt_ in nbt_data]
    elif isinstance(nbt_data, (int, float, str)):
        return nbt_type, nbt_data
    else:  # numpy array
        return nbt_type, list(nbt)


def unobjectify_nbt(nbt: Tuple[str, Union[dict, list, int, str, "ndarray"]]):
    nbt_type, nbt = nbt
    nbt_class = datatype_to_nbt(nbt_type)
    if nbt_type == "compound":
        return nbt_class({key: unobjectify_nbt(val) for key, val in nbt.items()})
    elif nbt_type == "list":
        return nbt_class([unobjectify_nbt(val) for val in nbt])
    elif nbt_type in [
        "byte",
        "short",
        "int",
        "long",
        "float",
        "double",
        "string",
        "byte_array",
        "int_array",
        "long_array",
    ]:
        return nbt_class(nbt)


def _convert_walk_input_nbt(
    block_input: Union[Block, None],
    nbt_input: Union[NBTFile, None],
    mappings: dict,
    get_block_callback: Callable,
    absolute_location: BlockCoordinates = (0, 0, 0),
    relative_location: BlockCoordinates = (0, 0, 0),
    nbt_path: Tuple[str, str, List[Tuple[Union[str, int], str]]] = None,
    inherited_data: Tuple[Union[str, None], Union[str, None], dict, bool, bool] = None,
) -> Tuple[Union[str, None], Union[str, None], dict, bool, bool]:
    if nbt_path is None:
        nbt_path = ("", "compound", [])
    if inherited_data is not None:
        output_name, output_type, new_data, extra_needed, cacheable = inherited_data
    else:
        output_name = None
        output_type = None
        new_data = {
            "properties": {},
            "nbt": [],
        }  # There could be multiple 'new_block' functions in the mappings so new properties are put in here and merged at the very end
        new_data["nbt"]: List[
            List[
                str,
                str,
                List[Union[str, int], str],
                Union[str, int],
                Union[
                    TAG_Byte,
                    TAG_Short,
                    TAG_Int,
                    TAG_Long,
                    TAG_Float,
                    TAG_Double,
                    TAG_Byte_Array,
                    TAG_String,
                    TAG_List,
                    TAG_Compound,
                    TAG_Int_Array,
                    TAG_Long_Array,
                ],
            ]
        ]
        """
		new['nbt'] = [
			[
				[
					[path0, type0],
					[path1, type1],
					...
				],
				path_n,
				NBT
			],
			...
		]
		"""
        extra_needed = False  # used to determine if extra data is required (and thus to do block by block)
        cacheable = True  # cacheable until proven otherwise

    nbt = index_nbt(
        nbt_input, nbt_path
    )  # nbt_path should always exist in nbt_input because the calling code should check that

    datatype = mappings["type"]

    if "functions" in mappings:
        # run functions if present
        output_name, output_type, new_data, extra_needed, cacheable = _translate(
            block_input,
            nbt_input,
            mappings["functions"],
            get_block_callback,
            absolute_location,
            relative_location,
            nbt_path,
            (output_name, output_type, new_data, extra_needed, cacheable),
        )

    if isinstance(nbt, datatype_to_nbt(datatype)):
        # datatypes match
        if datatype == "compound":
            for key in nbt.value:
                if key in mappings.get("keys", {}):
                    (
                        output_name,
                        output_type,
                        new_data,
                        extra_needed,
                        cacheable,
                    ) = _convert_walk_input_nbt(
                        block_input,
                        nbt_input,
                        mappings["keys"][key],
                        get_block_callback,
                        absolute_location,
                        relative_location,
                        (
                            nbt_path[0],
                            nbt_path[1],
                            nbt_path[2] + [(key, nbt_to_datatype(nbt.value[key]))],
                        ),
                        (output_name, output_type, new_data, extra_needed, cacheable),
                    )
                elif "nested_default" in mappings:
                    if mappings["nested_default"] == [{"function": "carry_nbt"}]:
                        log.info(
                            f"Unnaccounted data at {(nbt_path[0], nbt_path[1], nbt_path[2] + [(key, nbt_to_datatype(nbt.value[key]))])}"
                        )
                    (
                        output_name,
                        output_type,
                        new_data,
                        extra_needed,
                        cacheable,
                    ) = _translate(
                        block_input,
                        nbt_input,
                        mappings["nested_default"],
                        get_block_callback,
                        absolute_location,
                        relative_location,
                        (
                            nbt_path[0],
                            nbt_path[1],
                            nbt_path[2] + [(key, nbt_to_datatype(nbt.value[key]))],
                        ),
                        (output_name, output_type, new_data, extra_needed, cacheable),
                    )

        elif datatype == "list":
            for index in range(len(nbt)):
                if str(index) in mappings.get("index", {}):
                    (
                        output_name,
                        output_type,
                        new_data,
                        extra_needed,
                        cacheable,
                    ) = _convert_walk_input_nbt(
                        block_input,
                        nbt_input,
                        mappings["index"][str(index)],
                        get_block_callback,
                        absolute_location,
                        relative_location,
                        (
                            nbt_path[0],
                            nbt_path[1],
                            nbt_path[2] + [(index, nbt_to_datatype(nbt.value[index]))],
                        ),
                        (output_name, output_type, new_data, extra_needed, cacheable),
                    )
                elif "nested_default" in mappings:
                    if mappings["nested_default"] == [{"function": "carry_nbt"}]:
                        log.info(
                            f"Unnaccounted data at {(nbt_path[0], nbt_path[1], nbt_path[2] + [(index, nbt_to_datatype(nbt.value[index]))])}"
                        )
                    (
                        output_name,
                        output_type,
                        new_data,
                        extra_needed,
                        cacheable,
                    ) = _translate(
                        block_input,
                        nbt_input,
                        mappings["nested_default"],
                        get_block_callback,
                        absolute_location,
                        relative_location,
                        (
                            nbt_path[0],
                            nbt_path[1],
                            nbt_path[2] + [(index, nbt_to_datatype(nbt.value[index]))],
                        ),
                        (output_name, output_type, new_data, extra_needed, cacheable),
                    )

        # elif datatype in ('byte', 'short', 'int', 'long', 'float', 'double', 'string'):
        # 	pass

        elif datatype in ("byte_array", "int_array", "long_array"):
            nested_datatype = datatype.replace("_array", "")
            for index in range(len(nbt)):
                if str(index) in mappings.get("index", {}):
                    (
                        output_name,
                        output_type,
                        new_data,
                        extra_needed,
                        cacheable,
                    ) = _convert_walk_input_nbt(
                        block_input,
                        nbt_input,
                        mappings["index"][str(index)],
                        get_block_callback,
                        absolute_location,
                        relative_location,
                        (
                            nbt_path[0],
                            nbt_path[1],
                            nbt_path[2] + [(index, nested_datatype)],
                        ),
                        (output_name, output_type, new_data, extra_needed, cacheable),
                    )
                elif "nested_default" in mappings:
                    (
                        output_name,
                        output_type,
                        new_data,
                        extra_needed,
                        cacheable,
                    ) = _translate(
                        block_input,
                        nbt_input,
                        mappings["nested_default"],
                        get_block_callback,
                        absolute_location,
                        relative_location,
                        (
                            nbt_path[0],
                            nbt_path[1],
                            nbt_path[2] + [(index, nested_datatype)],
                        ),
                        (output_name, output_type, new_data, extra_needed, cacheable),
                    )

    elif "self_default" in mappings:
        # datatypes do not match. Run self_default
        output_name, output_type, new_data, extra_needed, cacheable = _translate(
            block_input,
            nbt_input,
            mappings["self_default"],
            get_block_callback,
            absolute_location,
            relative_location,
            nbt_path,
            (output_name, output_type, new_data, extra_needed, cacheable),
        )

    return output_name, output_type, new_data, extra_needed, cacheable

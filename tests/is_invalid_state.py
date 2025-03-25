"""
A function to check if a block is an invalid blocks.
Bedrock has a number of states that are unused.
"""

from typing import Any

from amulet_nbt import StringTag, ByteTag, IntTag
import PyMCTranslate
from PyMCTranslate.py3.api import Block


def is_invalid_state(
    platform_name: str,
    version_number: Any,
    version: PyMCTranslate.Version,
    input_blockstate: Block,
) -> bool:
    """Skip over invalid states."""
    namespaced_name = input_blockstate.namespaced_name
    if platform_name == "java":
        if version_number <= (1, 12, 2):
            if namespaced_name == "minecraft:tallgrass":
                return (
                    input_blockstate.properties.get("plant_type", StringTag()).py_str
                    == "dead_bush"
                )
            if namespaced_name == "minecraft:piston_head":
                # Numerical does not store sticky state
                return (
                    input_blockstate.properties.get("type", StringTag()).py_str
                    == "sticky"
                )
    elif platform_name == "bedrock":
        if (1, 19, 80) <= version_number and namespaced_name in {
            "minecraft:fence",
            "minecraft:log",
            "minecraft:log2",
        }:
            return True
        elif version_number < (1, 18, 30) and namespaced_name in {
            "minecraft:concrete_powder",
            "minecraft:piston_arm_collision",
            "minecraft:trip_wire",
            "minecraft:invisible_bedrock",
            "minecraft:sea_lantern",
            "minecraft:sticky_piston_arm_collision",
        }:
            return True
        elif (1, 18, 30) <= version_number and namespaced_name in {
            "minecraft:concretePowder",
            "minecraft:pistonArmCollision",
            "minecraft:tripWire",
            "minecraft:invisibleBedrock",
            "minecraft:seaLantern",
            "minecraft:stickyPistonArmCollision",
        }:
            return True
        elif (1, 13, 0) <= version_number:
            # if namespaced_name in {
            #     "minecraft:blue_orchid",
            #
            # }:
            #     # known issues
            #     return True
            if namespaced_name in {
                "minecraft:acacia_pressure_plate",
                "minecraft:birch_pressure_plate",
                "minecraft:dark_oak_pressure_plate",
                "minecraft:jungle_pressure_plate",
                "minecraft:spruce_pressure_plate",
                "minecraft:stone_pressure_plate",
                "minecraft:wooden_pressure_plate",
                "minecraft:bamboo_pressure_plate",
                "minecraft:cherry_pressure_plate",
                "minecraft:crimson_pressure_plate",
                "minecraft:mangrove_pressure_plate",
                "minecraft:pale_oak_pressure_plate",
                "minecraft:polished_blackstone_pressure_plate",
                "minecraft:warped_pressure_plate",
            }:
                return 2 <= input_blockstate.properties["redstone_signal"].py_int
            elif namespaced_name == "minecraft:bamboo_sapling":
                return input_blockstate.properties.get(
                    "sapling_type", StringTag()
                ).py_str in {
                    "spruce",
                    "birch",
                    "jungle",
                    "acacia",
                    "dark_oak",
                }
            elif namespaced_name in {
                "minecraft:bone_block",
                "minecraft:hay_block",
                "minecraft:stripped_crimson_hyphae",
                "minecraft:stripped_crimson_stem",
                "minecraft:stripped_warped_hyphae",
                "minecraft:stripped_warped_stem",
            }:
                return (
                    input_blockstate.properties.get("deprecated", IntTag()).py_int != 0
                )
            elif namespaced_name in {
                "minecraft:brown_mushroom_block",
                "minecraft:red_mushroom_block",
            }:
                state = input_blockstate.properties["huge_mushroom_bits"].py_int
                return 11 <= state <= 13 or (
                    (1, 21, 40) <= version_number and state in (10, 15)
                )
            elif namespaced_name == "minecraft:mushroom_stem":
                return input_blockstate.properties["huge_mushroom_bits"].py_int not in (
                    10,
                    15,
                )
            elif namespaced_name in {
                "minecraft:colored_torch_bp",
                "minecraft:colored_torch_blue",
                "minecraft:colored_torch_purple",
                "minecraft:colored_torch_rg",
                "minecraft:colored_torch_red",
                "minecraft:colored_torch_green",
                "minecraft:torch",
                "minecraft:underwater_torch",
                "minecraft:unlit_redstone_torch",
                "minecraft:redstone_torch",
                "minecraft:soul_torch",
            }:
                return (
                    input_blockstate.properties["torch_facing_direction"].py_str
                    == "unknown"
                )
            elif namespaced_name in {
                "minecraft:coral_fan",
                "minecraft:coral_fan_dead",
                "minecraft:brain_coral_fan",
                "minecraft:dead_brain_coral_fan",
                "minecraft:bubble_coral_fan",
                "minecraft:dead_bubble_coral_fan",
                "minecraft:fire_coral_fan",
                "minecraft:dead_fire_coral_fan",
                "minecraft:horn_coral_fan",
                "minecraft:dead_horn_coral_fan",
                "minecraft:tube_coral_fan",
                "minecraft:dead_tube_coral_fan",
            }:
                return input_blockstate.properties["coral_fan_direction"].py_int == 1
            elif namespaced_name == "minecraft:coral_fan_hang3":
                return input_blockstate.properties["coral_hang_type_bit"].py_int == 1
            elif (
                namespaced_name
                in {
                    "minecraft:stone_slab",
                    "minecraft:double_stone_slab",
                    "minecraft:stone_slab2",
                    "minecraft:double_stone_slab2",
                    "minecraft:stone_slab3",
                    "minecraft:double_stone_slab3",
                    "minecraft:stone_slab4",
                    "minecraft:double_stone_slab4",
                }
                and (1, 19, 0) <= version_number
            ):
                return True
            elif namespaced_name in {
                "minecraft:acacia_double_slab",
                "minecraft:andesite_double_slab",
                "minecraft:bamboo_double_slab",
                "minecraft:bamboo_mosaic_double_slab",
                "minecraft:birch_double_slab",
                "minecraft:blackstone_double_slab",
                "minecraft:brick_double_slab",
                "minecraft:cherry_double_slab",
                "minecraft:cobbled_deepslate_double_slab",
                "minecraft:cobblestone_double_slab",
                "minecraft:crimson_double_slab",
                "minecraft:cut_red_sandstone_double_slab",
                "minecraft:cut_sandstone_double_slab",
                "minecraft:dark_oak_double_slab",
                "minecraft:dark_prismarine_double_slab",
                "minecraft:deepslate_brick_double_slab",
                "minecraft:deepslate_tile_double_slab",
                "minecraft:diorite_double_slab",
                "minecraft:double_cut_copper_slab",
                "minecraft:double_stone_block_slab",
                "minecraft:double_stone_block_slab2",
                "minecraft:double_stone_block_slab3",
                "minecraft:double_stone_block_slab4",
                "minecraft:double_stone_slab",
                "minecraft:double_stone_slab2",
                "minecraft:double_stone_slab3",
                "minecraft:double_stone_slab4",
                "minecraft:double_wooden_slab",
                "minecraft:end_stone_brick_double_slab",
                "minecraft:exposed_double_cut_copper_slab",
                "minecraft:granite_double_slab",
                "minecraft:jungle_double_slab",
                "minecraft:mangrove_double_slab",
                "minecraft:mossy_cobblestone_double_slab",
                "minecraft:mossy_stone_brick_double_slab",
                "minecraft:mud_brick_double_slab",
                "minecraft:nether_brick_double_slab",
                "minecraft:normal_stone_double_slab",
                "minecraft:oak_double_slab",
                "minecraft:oxidized_double_cut_copper_slab",
                "minecraft:pale_oak_double_slab",
                "minecraft:petrified_oak_double_slab",
                "minecraft:polished_andesite_double_slab",
                "minecraft:polished_blackstone_brick_double_slab",
                "minecraft:polished_blackstone_double_slab",
                "minecraft:polished_deepslate_double_slab",
                "minecraft:polished_diorite_double_slab",
                "minecraft:polished_granite_double_slab",
                "minecraft:polished_tuff_double_slab",
                "minecraft:prismarine_brick_double_slab",
                "minecraft:prismarine_double_slab",
                "minecraft:purpur_double_slab",
                "minecraft:quartz_double_slab",
                "minecraft:red_nether_brick_double_slab",
                "minecraft:red_sandstone_double_slab",
                "minecraft:resin_brick_double_slab",
                "minecraft:sandstone_double_slab",
                "minecraft:smooth_quartz_double_slab",
                "minecraft:smooth_red_sandstone_double_slab",
                "minecraft:smooth_sandstone_double_slab",
                "minecraft:smooth_stone_double_slab",
                "minecraft:spruce_double_slab",
                "minecraft:stone_brick_double_slab",
                "minecraft:tuff_brick_double_slab",
                "minecraft:tuff_double_slab",
                "minecraft:warped_double_slab",
                "minecraft:waxed_double_cut_copper_slab",
                "minecraft:waxed_exposed_double_cut_copper_slab",
                "minecraft:waxed_oxidized_double_cut_copper_slab",
                "minecraft:waxed_weathered_double_cut_copper_slab",
                "minecraft:weathered_double_cut_copper_slab",
            }:
                return (
                    input_blockstate.properties.get("top_slot_bit", IntTag()).py_int
                    == 1
                    or input_blockstate.properties.get(
                        "minecraft:vertical_half", StringTag()
                    ).py_str
                    == "top"
                )
            elif namespaced_name == "minecraft:ladder":
                return 0 <= input_blockstate.properties["facing_direction"].py_int <= 1
            elif namespaced_name == "minecraft:portal":
                return input_blockstate.properties["portal_axis"].py_str == "unknown"
            elif namespaced_name == "minecraft:tallgrass":
                return input_blockstate.properties["tall_grass_type"].py_str in {
                    "default",
                    "snow",
                }
            elif namespaced_name == "minecraft:stonecutter_block":
                return (
                    input_blockstate.properties.get(
                        "facing_direction", IntTag(2)
                    ).py_int
                    <= 1
                )
            elif namespaced_name in {
                "minecraft:melon_stem",
                "minecraft:pumpkin_stem",
            }:
                return (
                    input_blockstate.properties.get("facing_direction", IntTag()).py_int
                    == 1
                )
            elif namespaced_name == "minecraft:torchflower_crop":
                return 2 <= input_blockstate.properties.get("growth", IntTag()).py_int
            elif namespaced_name == "minecraft:pitcher_crop":
                return 5 <= input_blockstate.properties["growth"].py_int
            elif namespaced_name in {
                "minecraft:activator_rail",
                "minecraft:detector_rail",
                "minecraft:golden_rail",
            }:
                return 6 <= input_blockstate.properties["rail_direction"].py_int
            elif namespaced_name == "minecraft:chorus_flower":
                return 6 <= input_blockstate.properties["age"].py_int
            elif namespaced_name == "minecraft:cocoa":
                return 3 <= input_blockstate.properties["age"].py_int
            elif namespaced_name == "minecraft:frosted_ice":
                return 4 <= input_blockstate.properties["age"].py_int
            elif namespaced_name == "minecraft:nether_wart":
                return 4 <= input_blockstate.properties["age"].py_int
            elif namespaced_name in {
                "minecraft:deprecated_purpur_block_1",
                "minecraft:deprecated_purpur_block_2",
            }:
                return True
            elif namespaced_name == "minecraft:stonebrick":
                return (
                    input_blockstate.properties["stone_brick_type"].py_str == "smooth"
                )
            elif namespaced_name in {
                "minecraft:mangrove_wood",
                "minecraft:cherry_wood",
            }:
                return (
                    input_blockstate.properties.get("stripped_bit", ByteTag()).py_int
                    == 1
                )
            elif namespaced_name == "minecraft:pink_petals":
                return 4 <= input_blockstate.properties["growth"].py_int
            elif namespaced_name == "minecraft:grindstone":
                return input_blockstate.properties["attachment"].py_str == "multiple"
    return False

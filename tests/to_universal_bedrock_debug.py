from reader.data_version_handler import VersionContainer, Block

block_names = [
    "air",
    "stone",
    "grass",
    "dirt",
    "cobblestone",
    "planks",
    "sapling",
    "bedrock",
    "flowing_water",
    "water",
    "flowing_lava",
    "lava",
    "sand",
    "gravel",
    "gold_ore",
    "iron_ore",
    "coal_ore",
    "log",
    "leaves",
    "sponge",
    "glass",
    "lapis_ore",
    "lapis_block",
    "dispenser",
    "sandstone",
    "noteblock",
    "bed",
    "golden_rail",
    "detector_rail",
    "sticky_piston",
    "web",
    "tallgrass",
    "deadbush",
    "piston",
    "pistonarmcollision",
    "wool",
    "yellow_flower",
    "red_flower",
    "brown_mushroom",
    "red_mushroom",
    "gold_block",
    "iron_block",
    "double_stone_slab",
    "stone_slab",
    "brick_block",
    "tnt",
    "bookshelf",
    "mossy_cobblestone",
    "obsidian",
    "torch",
    "fire",
    "mob_spawner",
    "oak_stairs",
    "chest",
    "redstone_wire",
    "diamond_ore",
    "diamond_block",
    "crafting_table",
    "wheat",
    "farmland",
    "furnace",
    "lit_furnace",
    "standing_sign",
    "wooden_door",
    "ladder",
    "rail",
    "stone_stairs",
    "wall_sign",
    "lever",
    "stone_pressure_plate",
    "iron_door",
    "wooden_pressure_plate",
    "redstone_ore",
    "lit_redstone_ore",
    "unlit_redstone_torch",
    "redstone_torch",
    "stone_button",
    "snow_layer",
    "ice",
    "snow",
    "cactus",
    "clay",
    "reeds",
    "jukebox",
    "fence",
    "pumpkin",
    "netherrack",
    "soul_sand",
    "glowstone",
    "portal",
    "lit_pumpkin",
    "cake",
    "unpowered_repeater",
    "powered_repeater",
    "invisiblebedrock",
    "trapdoor",
    "monster_egg",
    "stonebrick",
    "brown_mushroom_block",
    "red_mushroom_block",
    "iron_bars",
    "glass_pane",
    "melon_block",
    "pumpkin_stem",
    "melon_stem",
    "vine",
    "fence_gate",
    "brick_stairs",
    "stone_brick_stairs",
    "mycelium",
    "waterlily",
    "nether_brick",
    "nether_brick_fence",
    "nether_brick_stairs",
    "nether_wart",
    "enchanting_table",
    "brewing_stand",
    "cauldron",
    "end_portal",
    "end_portal_frame",
    "end_stone",
    "dragon_egg",
    "redstone_lamp",
    "lit_redstone_lamp",
    "dropper",
    "activator_rail",
    "cocoa",
    "sandstone_stairs",
    "emerald_ore",
    "ender_chest",
    "tripwire_hook",
    "tripwire",
    "emerald_block",
    "spruce_stairs",
    "birch_stairs",
    "jungle_stairs",
    "command_block",
    "beacon",
    "cobblestone_wall",
    "flower_pot",
    "carrots",
    "potatoes",
    "wooden_button",
    "skull",
    "anvil",
    "trapped_chest",
    "light_weighted_pressure_plate",
    "heavy_weighted_pressure_plate",
    "unpowered_comparator",
    "powered_comparator",
    "daylight_detector",
    "redstone_block",
    "quartz_ore",
    "hopper",
    "quartz_block",
    "quartz_stairs",
    "double_wooden_slab",
    "wooden_slab",
    "stained_hardened_clay",
    "stained_glass_pane",
    "leaves2",
    "log2",
    "acacia_stairs",
    "dark_oak_stairs",
    "slime",
    "iron_trapdoor",
    "prismarine",
    "sealantern",
    "hay_block",
    "carpet",
    "hardened_clay",
    "coal_block",
    "packed_ice",
    "double_plant",
    "standing_banner",
    "wall_banner",
    "daylight_detector_inverted",
    "red_sandstone",
    "red_sandstone_stairs",
    "double_stone_slab2",
    "stone_slab2",
    "spruce_fence_gate",
    "birch_fence_gate",
    "jungle_fence_gate",
    "dark_oak_fence_gate",
    "acacia_fence_gate",
    "repeating_command_block",
    "chain_command_block",
    "spruce_door",
    "birch_door",
    "jungle_door",
    "acacia_door",
    "dark_oak_door",
    "grass_path",
    "frame",
    "chorus_flower",
    "purpur_block",
    "purpur_stairs",
    "undyed_shulker_box",
    "end_bricks",
    "frosted_ice",
    "end_rod",
    "end_gateway",
    "magma",
    "nether_wart_block",
    "red_nether_brick",
    "bone_block",
    "shulker_box",
    "purple_glazed_terracotta",
    "white_glazed_terracotta",
    "orange_glazed_terracotta",
    "magenta_glazed_terracotta",
    "light_blue_glazed_terracotta",
    "yellow_glazed_terracotta",
    "lime_glazed_terracotta",
    "pink_glazed_terracotta",
    "gray_glazed_terracotta",
    "silver_glazed_terracotta",
    "cyan_glazed_terracotta",
    "blue_glazed_terracotta",
    "brown_glazed_terracotta",
    "green_glazed_terracotta",
    "red_glazed_terracotta",
    "black_glazed_terracotta",
    "concrete",
    "concretepowder",
    "chorus_plant",
    "stained_glass",
    "podzol",
    "beetroots",
    "stonecutter",
    "glowingobsidian",
    "netherreactor",
    "info_update",
    "info_update2",
    "movingblock",
    "observer",
    "structure_block",
    "reserved6",
    "prismarine_stairs",
    "dark_prismarine_stairs",
    "prismarine_bricks_stairs",
    "stripped_spruce_log",
    "stripped_birch_log",
    "stripped_jungle_log",
    "stripped_acacia_log",
    "stripped_dark_oak_log",
    "stripped_oak_log",
    "blue_ice",
    "seagrass",
    "coral",
    "coral_block",
    "coral_fan",
    "coral_fan_dead",
    "coral_fan_hang",
    "coral_fan_hang2",
    "coral_fan_hang3",
    "kelp",
    "dried_kelp_block",
    "acacia_button",
    "birch_button",
    "dark_oak_button",
    "jungle_button",
    "spruce_button",
    "acacia_trapdoor",
    "birch_trapdoor",
    "dark_oak_trapdoor",
    "jungle_trapdoor",
    "spruce_trapdoor",
    "acacia_pressure_plate",
    "birch_pressure_plate",
    "dark_oak_pressure_plate",
    "jungle_pressure_plate",
    "spruce_pressure_plate",
    "carved_pumpkin",
    "sea_pickle",
    "conduit",
    "turtle_egg",
    "bubble_column",
    "barrier",
]

if __name__ == "__main__":
    block_mappings = VersionContainer(r"..\mappings")
    for block_name in block_names:
        print(block_name)
        for data in range(16):
            output = block_mappings.to_universal(
                None,
                "bedrock",
                (1, 7, 0),
                Block("minecraft", block_name, {"block_data": str(data)}),
            )
            print(str(output[0]), str(output[1]), output[2])
        print("")

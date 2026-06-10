import pygame
import cv2
import numpy as np
import random
import terrain
import render
import json
import os
import math

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
screen = pygame.display.set_mode((render.WIDTH, render.HEIGHT))
pygame.display.set_caption(render.WINDOW_NAME)
clock = pygame.time.Clock()

current_state = render.STATE_GAME  
WORLD_ROWS = 96
CHUNK_SIZE = 16 
SAVE_FILE = "savegame_infinite.json"
MAX_STACK = 64
DAY_LENGTH_FRAMES = 24000
MAX_MOBS = 10
MAX_ANIMALS = 8
MAX_BIRDS = 8
MAX_PLANES = 3
MAX_SUPPLY_PLANES = 2
MAX_SUPPLY_CRATES = 4
MAX_SUNBIRDS = 4
MAX_NPCS = 8
MAX_PROJECTILES = 40
MAX_STRUCTURES = 8
MAX_DROPPED_ITEMS = 80
MAX_DROP_AGE_FRAMES = 3600
ACTIVE_CHUNK_KEEP_RADIUS = 6
RESOURCE_CLEANUP_INTERVAL = 600
MAX_PERSISTENT_CHESTS = 80
MAX_COVERED_BLOCKS = 2048
MAX_PLANTED_CROPS = 512
VOID_DEATH_MARGIN_BLOCKS = 4
HOSTILE_AGGRO_BLOCKS = 7
SPAWN_PROTECTION_RADIUS = 8
SPAWN_PROTECTION_BLOCKS = {16, 55, 62, 63}
MOB_SPAWN_INTERVAL = 180
ANIMAL_SPAWN_INTERVAL = 360
BIRD_SPAWN_INTERVAL = 210
PLANE_SPAWN_INTERVAL = 900
SUPPLY_PLANE_SPAWN_INTERVAL = 3000
SUNBIRD_SPAWN_INTERVAL = 520
HOUSE_SPAWN_INTERVAL = 3000
WANDER_NPC_SPAWN_INTERVAL = 700
CAVE_MOB_SPAWN_INTERVAL = 240
BOSS_SPAWN_INTERVAL = 3600
HUNGER_DECAY_INTERVAL = 2400
SPRINT_HUNGER_INTERVAL = 420
STARVE_DAMAGE_INTERVAL = 180
HOTBAR_START = 27
HOTBAR_SIZE = 9
CROP_GROW_INTERVAL = 1800
VILLAGE_UPDATE_INTERVAL = 900
DISPLAY_Y_ZERO_BLOCK = WORLD_ROWS // 2

mouse_x, mouse_y = 0, 0     
is_mining, mine_target_abs_x, mine_target_abs_y, mining_progress, mining_required_time = False, -1, -1, 0, 20
particles = []

hp, hunger, selected_slot = 10, 10, HOTBAR_START
player_level, player_xp, money = 1, 0, 0
inventory = [{"id": 0, "count": 0} for _ in range(36)]
inventory[HOTBAR_START] = {"id": 41, "count": 1}
inventory[HOTBAR_START + 1] = {"id": 40, "count": 32}
inventory[HOTBAR_START + 2] = {"id": 1, "count": 64}
crafting_grid = [{"id": 0, "count": 0} for _ in range(4)] 
crafting_table_grid = [{"id": 0, "count": 0} for _ in range(9)]
furnace_slots = [{"id": 0, "count": 0} for _ in range(3)]
open_chest_key = None
open_chest_slots = [{"id": 0, "count": 0} for _ in range(18)]
crafting_output, crafting_table_output = {"id": 0, "count": 0}, {"id": 0, "count": 0}
cursor_item = {"id": 0, "count": 0}
furnace_progress = 0

ITEM_NAMES = {
    1: "Grass", 2: "Dirt", 3: "Stone", 4: "Crafting Table", 5: "Stick",
    6: "Sand", 7: "Water", 8: "Log", 9: "Leaves", 10: "Planks",
    11: "Wooden Pickaxe", 12: "Wooden Shovel", 13: "Wooden Sword", 14: "Wooden Axe",
    15: "Coal", 16: "Torch", 17: "Iron Ore", 18: "Iron Ingot",
    19: "Iron Pickaxe", 20: "Iron Shovel", 21: "Iron Sword", 22: "Iron Axe",
    23: "Diamond Ore", 24: "Diamond",
    25: "Diamond Pickaxe", 26: "Diamond Shovel", 27: "Diamond Sword", 28: "Diamond Axe",
    29: "Cobblestone", 30: "Stone Pickaxe", 31: "Stone Shovel", 32: "Stone Sword", 33: "Stone Axe",
    34: "Gold Ore", 35: "Gold Ingot",
    36: "Golden Pickaxe", 37: "Golden Shovel", 38: "Golden Sword", 39: "Golden Axe",
    40: "Bullet", 41: "Stone Pistol", 42: "Iron Rifle", 43: "Golden Blaster",
    44: "Diamond Cannon", 45: "Chest", 46: "House Kit",
    47: "Chicken", 48: "Porkchop", 49: "Beef", 50: "Mutton", 51: "Venison",
    # Stone utility set requested by the crafting reference.
    52: "Furnace", 53: "Stone Hoe", 54: "Stonecutter", 55: "Lever", 56: "Cobblestone Wall",
    # Diamond and late-game utility set requested by the crafting reference.
    57: "Diamond Block", 58: "Diamond Helmet", 59: "Diamond Chestplate",
    60: "Diamond Leggings", 61: "Diamond Boots", 62: "Enchanting Table",
    63: "Jukebox", 64: "Smooth Stone", 65: "Book", 66: "Obsidian",
    # Monster drops, deeper underground blocks, and farming.
    67: "Rotten Flesh", 68: "Bone", 69: "String", 70: "Slimeball", 71: "Boss Core",
    72: "Deepslate", 73: "Cave Crystal", 74: "Packed Stone",
    75: "Seeds", 76: "Wheat", 77: "Farmland", 78: "Wheat Crop", 79: "Bread",
    80: "Cooked Chicken", 81: "Cooked Porkchop", 82: "Steak",
    83: "Cooked Mutton", 84: "Cooked Venison",
}
PLACEABLE_BLOCKS = {1, 2, 3, 4, 6, 8, 9, 10, 16, 17, 23, 29, 34, 45, 52, 54, 55, 56, 57, 62, 63, 64, 66, 72, 73, 74, 77}
BLOCK_DROPS = {3: 29, 17: 18, 23: 24, 34: 35, 52: 52, 54: 54, 55: 55, 56: 56, 57: 57, 62: 62, 63: 63, 64: 64, 66: 66, 72: 72, 73: 73, 74: 74, 77: 2, 78: 76}
TOOL_SPEEDS = {
    11: {"stone": 2.0, "dirt": 1.0, "wood": 1.0},
    12: {"stone": 1.0, "dirt": 3.0, "wood": 1.0},
    14: {"stone": 1.0, "dirt": 1.0, "wood": 3.0},
    19: {"stone": 4.0, "dirt": 1.0, "wood": 1.0},
    20: {"stone": 1.0, "dirt": 5.0, "wood": 1.0},
    22: {"stone": 1.0, "dirt": 1.0, "wood": 5.0},
    25: {"stone": 6.0, "dirt": 1.0, "wood": 1.0},
    26: {"stone": 1.0, "dirt": 7.0, "wood": 1.0},
    28: {"stone": 1.0, "dirt": 1.0, "wood": 7.0},
    30: {"stone": 3.0, "dirt": 1.0, "wood": 1.0},
    31: {"stone": 1.0, "dirt": 4.0, "wood": 1.0},
    33: {"stone": 1.0, "dirt": 1.0, "wood": 4.0},
    53: {"stone": 1.0, "dirt": 2.5, "wood": 1.0},
    36: {"stone": 7.0, "dirt": 1.0, "wood": 1.0},
    37: {"stone": 1.0, "dirt": 8.0, "wood": 1.0},
    39: {"stone": 1.0, "dirt": 1.0, "wood": 8.0},
}
WEAPON_DAMAGE = {13: 4, 21: 6, 27: 8, 32: 5, 38: 4, 41: 5, 42: 7, 43: 6, 44: 10, 14: 3, 22: 5, 28: 7, 33: 4, 39: 3, 53: 2}
GUN_STATS = {
    41: {"damage": 5, "speed": 11.0, "cost": 1},
    42: {"damage": 7, "speed": 14.0, "cost": 1},
    43: {"damage": 6, "speed": 18.0, "cost": 1},
    44: {"damage": 10, "speed": 12.0, "cost": 2},
}
ANIMAL_MAX_HP = {"chicken": 4, "pig": 8, "sheep": 8, "cow": 10, "deer": 12}
FOOD_VALUES = {
    47: {"hp": 1, "hunger": 2},
    48: {"hp": 2, "hunger": 3},
    49: {"hp": 2, "hunger": 4},
    50: {"hp": 2, "hunger": 3},
    51: {"hp": 3, "hunger": 4},
    67: {"hp": 0, "hunger": 1},
    79: {"hp": 2, "hunger": 5},
    80: {"hp": 2, "hunger": 4},
    81: {"hp": 3, "hunger": 5},
    82: {"hp": 3, "hunger": 6},
    83: {"hp": 3, "hunger": 5},
    84: {"hp": 4, "hunger": 6},
}
ITEM_MAX_DURABILITY = {
    **{item_id: 60 for item_id in (11, 12, 13, 14)},
    **{item_id: 132 for item_id in (30, 31, 32, 33, 53)},
    **{item_id: 250 for item_id in (19, 20, 21, 22)},
    **{item_id: 40 for item_id in (36, 37, 38, 39)},
    **{item_id: 1561 for item_id in (25, 26, 27, 28)},
    41: 180, 42: 320, 43: 160, 44: 520,
}
MOB_REWARDS = {
    "zombie": {"xp": 4, "money": 3},
    "skeleton": {"xp": 5, "money": 4},
    "slime": {"xp": 4, "money": 2},
    "green_jet": {"xp": 7, "money": 6},
    "cave_zombie": {"xp": 6, "money": 5},
    "cave_spider": {"xp": 7, "money": 5},
    "crystal_wisp": {"xp": 9, "money": 8},
    "ancient_boss": {"xp": 80, "money": 120},
}
TRADER_UNLOCK_LEVEL = 5
BOSS_UNLOCK_LEVEL = 20
PRE_BOSS_XP_REQUIREMENTS = [
    5, 7, 10, 14, 19,
    25, 32, 40, 49, 59,
    70, 82, 95, 109, 124,
    140, 157, 175, 194,
]
TRADER_TRADES = [
    {"name": "Iron Sword", "result": {"id": 21, "count": 1}, "money": 18, "xp": 0, "ores": {}, "desc": "Reliable melee weapon"},
    {"name": "Iron Pickaxe", "result": {"id": 19, "count": 1}, "money": 16, "xp": 4, "ores": {}, "desc": "Faster stone and ore mining"},
    {"name": "Iron Rifle", "result": {"id": 42, "count": 1}, "money": 34, "xp": 8, "ores": {}, "desc": "Stronger ranged weapon"},
    {"name": "Bullet Bundle", "result": {"id": 40, "count": 32}, "money": 7, "xp": 0, "ores": {15: 2}, "desc": "Ammo for every gun"},
    {"name": "Golden Blaster", "result": {"id": 43, "count": 1}, "money": 15, "xp": 5, "ores": {35: 3}, "desc": "Fast but flashy gun"},
    {"name": "Diamond Pickaxe", "result": {"id": 25, "count": 1}, "money": 20, "xp": 12, "ores": {24: 2}, "desc": "Top tier mining tool"},
    {"name": "Diamond Cannon", "result": {"id": 44, "count": 1}, "money": 50, "xp": 18, "ores": {24: 3, 18: 4}, "desc": "Heavy weapon for hard fights"},
    {"name": "Book", "result": {"id": 65, "count": 1}, "money": 8, "xp": 0, "ores": {}, "desc": "Used for an Enchanting Table"},
    {"name": "Obsidian Pack", "result": {"id": 66, "count": 4}, "money": 18, "xp": 3, "ores": {35: 1}, "desc": "Rare block for enchanting"},
]
BLOCK_CATEGORIES = {
    1: "dirt", 2: "dirt", 3: "stone", 4: "wood", 6: "dirt", 8: "wood",
    9: "leaves", 10: "wood", 16: "wood", 17: "stone", 23: "stone", 29: "stone", 34: "stone", 45: "wood",
    52: "stone", 54: "stone", 55: "stone", 56: "stone", 57: "stone", 62: "stone", 63: "wood", 64: "stone", 66: "stone",
    72: "stone", 73: "stone", 74: "stone", 77: "dirt", 78: "leaves",
}
BLOCK_HARDNESS = {
    72: 1.35,
    74: 1.75,
    66: 2.8,
    73: 1.45,
}

SHAPELESS_RECIPES = {
    (8,): {"id": 10, "count": 4},
    (15, 5): {"id": 16, "count": 4},
    (15, 18): {"id": 40, "count": 8},
    (15, 29): {"id": 40, "count": 4},
    (15, 35): {"id": 40, "count": 12},
    (15, 24): {"id": 40, "count": 16},
    (15, 68): {"id": 40, "count": 6},
    (15, 69): {"id": 40, "count": 6},
    (15, 70): {"id": 40, "count": 10},
    (10, 45): {"id": 46, "count": 1},
    (76, 76, 76): {"id": 79, "count": 1},
}
SHAPED_RECIPES_2 = {
    ((8, 8), (8, 8)): {"id": 4, "count": 1},
    ((10, 10), (10, 10)): {"id": 4, "count": 1},
    ((10,), (10,)): {"id": 5, "count": 4},
}
SHAPED_RECIPES_3 = {
    **SHAPED_RECIPES_2,
    ((10, 10, 10), (0, 5, 0), (0, 5, 0)): {"id": 11, "count": 1},
    ((10,), (5,), (5,)): {"id": 12, "count": 1},
    ((10,), (10,), (5,)): {"id": 13, "count": 1},
    ((10, 10), (10, 5), (0, 5)): {"id": 14, "count": 1},
    ((10, 10), (5, 10), (5, 0)): {"id": 14, "count": 1},
    ((29, 29, 29), (0, 5, 0), (0, 5, 0)): {"id": 30, "count": 1},
    ((29,), (5,), (5,)): {"id": 31, "count": 1},
    ((29,), (29,), (5,)): {"id": 32, "count": 1},
    ((29, 29), (29, 5), (0, 5)): {"id": 33, "count": 1},
    ((29, 29), (5, 29), (5, 0)): {"id": 33, "count": 1},
    ((29, 29, 29), (29, 0, 29), (29, 29, 29)): {"id": 52, "count": 1},
    ((29, 29), (0, 5), (0, 5)): {"id": 53, "count": 1},
    ((29, 29), (5, 0), (5, 0)): {"id": 53, "count": 1},
    ((0, 18, 0), (64, 64, 64)): {"id": 54, "count": 1},
    ((5,), (29,)): {"id": 55, "count": 1},
    ((29, 29, 29), (29, 29, 29)): {"id": 56, "count": 6},
    ((18, 18, 18), (0, 5, 0), (0, 5, 0)): {"id": 19, "count": 1},
    ((18,), (5,), (5,)): {"id": 20, "count": 1},
    ((18,), (18,), (5,)): {"id": 21, "count": 1},
    ((18, 18), (18, 5), (0, 5)): {"id": 22, "count": 1},
    ((18, 18), (5, 18), (5, 0)): {"id": 22, "count": 1},
    ((24, 24, 24), (0, 5, 0), (0, 5, 0)): {"id": 25, "count": 1},
    ((24,), (5,), (5,)): {"id": 26, "count": 1},
    ((24,), (24,), (5,)): {"id": 27, "count": 1},
    ((24, 24), (24, 5), (0, 5)): {"id": 28, "count": 1},
    ((24, 24), (5, 24), (5, 0)): {"id": 28, "count": 1},
    ((24, 24, 24), (24, 24, 24), (24, 24, 24)): {"id": 57, "count": 1},
    ((24, 24, 24), (24, 0, 24)): {"id": 58, "count": 1},
    ((24, 0, 24), (24, 24, 24), (24, 24, 24)): {"id": 59, "count": 1},
    ((24, 24, 24), (24, 0, 24), (24, 0, 24)): {"id": 60, "count": 1},
    ((24, 0, 24), (24, 0, 24)): {"id": 61, "count": 1},
    ((0, 65, 0), (24, 66, 24), (66, 66, 66)): {"id": 62, "count": 1},
    ((10, 10, 10), (10, 24, 10), (10, 10, 10)): {"id": 63, "count": 1},
    ((35, 35, 35), (0, 5, 0), (0, 5, 0)): {"id": 36, "count": 1},
    ((35,), (5,), (5,)): {"id": 37, "count": 1},
    ((35,), (35,), (5,)): {"id": 38, "count": 1},
    ((35, 35), (35, 5), (0, 5)): {"id": 39, "count": 1},
    ((35, 35), (5, 35), (5, 0)): {"id": 39, "count": 1},
    ((29, 29, 29), (0, 18, 5)): {"id": 41, "count": 1},
    ((29, 29, 29), (5, 18, 0)): {"id": 41, "count": 1},
    ((18, 18, 18), (29, 15, 5)): {"id": 42, "count": 1},
    ((18, 18, 18), (5, 15, 29)): {"id": 42, "count": 1},
    ((35, 35, 35), (29, 15, 5)): {"id": 43, "count": 1},
    ((35, 35, 35), (5, 15, 29)): {"id": 43, "count": 1},
    ((24, 24, 24), (18, 15, 5)): {"id": 44, "count": 1},
    ((24, 24, 24), (5, 15, 18)): {"id": 44, "count": 1},
    ((10, 10, 10), (10, 0, 10), (10, 10, 10)): {"id": 45, "count": 1},
    ((10, 10, 10), (10, 45, 10), (10, 10, 10)): {"id": 46, "count": 1},
    ((8, 8, 8), (8, 45, 8), (8, 8, 8)): {"id": 46, "count": 1},
}

# 3x3 crafting reference for the requested stone/diamond utility items.
# Format: output, ingredients, layout, in-game use.
CRAFTING_REFERENCE_3X3 = [
    ("Furnace", "Cobblestone x8", "outer ring filled, center empty", "right click to smelt ore or Cobblestone using Coal"),
    ("Stone Sword", "Cobblestone x2 + Stick x1", "top-middle and center Cobblestone, bottom-middle Stick", "melee weapon"),
    ("Stone Pickaxe", "Cobblestone x3 + Stick x2", "top row Cobblestone, center and bottom-middle Stick", "faster mining for stone/ore"),
    ("Stone Axe", "Cobblestone x3 + Stick x2", "top-left, top-middle, middle-left Cobblestone; center and bottom-middle Stick", "faster chopping"),
    ("Stone Shovel", "Cobblestone x1 + Stick x2", "top-middle Cobblestone, center and bottom-middle Stick", "faster digging"),
    ("Stone Hoe", "Cobblestone x2 + Stick x2", "top-left and top-middle Cobblestone, center and bottom-middle Stick", "light utility tool"),
    ("Stonecutter", "Iron Ingot x1 + Smooth Stone x3", "center Iron Ingot, bottom row Smooth Stone", "right click to cut Cobblestone into walls"),
    ("Lever", "Stick x1 + Cobblestone x1", "center Stick, bottom-middle Cobblestone", "right click to toggle a torch signal above"),
    ("Cobblestone Wall x6", "Cobblestone x6", "middle and bottom rows filled", "placeable defensive wall block"),
    ("Diamond Block", "Diamond x9", "all nine slots filled", "compact storage and shiny building block"),
    ("Diamond Armor", "Diamond 5/8/7/4", "Minecraft armor shapes", "right click armor pieces to equip and reduce damage"),
    ("Diamond Tools", "Diamond x1-3 + Stick", "same tool layouts as stone/iron tools", "late-game mining and combat"),
    ("Enchanting Table", "Book x1 + Diamond x2 + Obsidian x4", "Book top-middle; Diamond/Obsidian/Diamond middle; Obsidian bottom row", "right click to enchant held gear for XP"),
    ("Jukebox", "Planks x8 + Diamond x1", "outer ring Planks, center Diamond", "right click to play music and gain a tiny XP boost"),
    ("Stone Pistol", "Cobblestone x3 + Iron Ingot x1 + Stick x1", "top row Cobblestone; middle has Iron Ingot and Stick on either side", "starter gun that uses Bullets"),
    ("Iron Rifle", "Iron Ingot x3 + Coal x1 + Cobblestone x1 + Stick x1", "top row Iron; middle row Cobblestone/Coal/Stick, mirrored also works", "stronger gun with steady damage"),
    ("Golden Blaster", "Gold Ingot x3 + Coal x1 + Cobblestone x1 + Stick x1", "top row Gold; middle row Cobblestone/Coal/Stick, mirrored also works", "fast gun with high fire speed"),
    ("Diamond Cannon", "Diamond x3 + Coal x1 + Iron Ingot x1 + Stick x1", "top row Diamond; middle row Iron/Coal/Stick, mirrored also works", "heavy late-game gun"),
]

active_chunks = {} 
saved_chunks = {}
dirty_chunks = set()
covered_blocks = {}
WORLD_SEED = random.randint(0, 5000)
sky_color = (120, 180, 255)
world_time = 6000
mobs = []
animals = []
birds = []
planes = []
supply_planes = []
supply_crates = []
sunbirds = []
npcs = []
projectiles = []
structures = []
chests = {}
dropped_items = []
equipped_armor = {"helmet": 0, "chestplate": 0, "leggings": 0, "boots": 0}
enchanted_item_ids = []
planted_crops = {}
village_stats = {"houses": 0, "supplies": 0, "reputation": 0}
last_mob_spawn_frame = 0
last_cave_mob_spawn_frame = 0
last_animal_spawn_frame = 0
last_bird_spawn_frame = 0
last_plane_spawn_frame = 0
last_supply_plane_spawn_frame = 0
last_sunbird_spawn_frame = 0
last_house_spawn_frame = 0
last_wander_npc_spawn_frame = 0
last_boss_spawn_frame = 0
last_player_damage_frame = 0
last_resource_cleanup_frame = 0
trader_message = ""

DIAMOND_ARMOR_SLOTS = {58: "helmet", 59: "chestplate", 60: "leggings", 61: "boots"}
DIAMOND_ARMOR_DEFENSE = {58: 1, 59: 3, 60: 2, 61: 1}
ENCHANTABLE_ITEMS = set(TOOL_SPEEDS.keys()) | set(WEAPON_DAMAGE.keys()) | set(GUN_STATS.keys())
FURNACE_RECIPES = {
    17: {"result": 18, "name": "Iron Ingot"},
    34: {"result": 35, "name": "Gold Ingot"},
    23: {"result": 24, "name": "Diamond"},
    29: {"result": 64, "name": "Smooth Stone"},
    47: {"result": 80, "name": "Cooked Chicken"},
    48: {"result": 81, "name": "Cooked Porkchop"},
    49: {"result": 82, "name": "Steak"},
    50: {"result": 83, "name": "Cooked Mutton"},
    51: {"result": 84, "name": "Cooked Venison"},
}

player_abs_px = 0.0  
player_py = 100.0  
vel_x, vel_y = 0.0, 0.0
facing_right, is_grounded = True, False

GRAVITY, JUMP_FORCE = 0.5, -8.0     
WALK_SPEED, SPRINT_SPEED, SNEAK_SPEED = 4.0, 6.0, 1.5      
ACCELERATION, FRICTION, AIR_RESISTANCE = 0.8, 0.80, 0.98  
MINE_MAX_TIME = 20
MINE_REACH_BLOCKS = 3
NON_SOLID_BLOCKS = [0, 7, 9]
last_step_frame = 0
last_swim_frame = 0
last_hunger_decay_frame = 0
last_sprint_hunger_frame = 0
last_starve_damage_frame = 0
last_crop_update_frame = 0
last_village_update_frame = 0

try:
    if not pygame.mixer.get_init():
        pygame.mixer.init()
except pygame.error:
    pass

def make_sound(freq=440, duration=0.08, volume=0.25, noise=0.0, slide=0.0):
    if not pygame.mixer.get_init():
        return None
    sample_rate = pygame.mixer.get_init()[0]
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = np.sin(2 * np.pi * (freq + slide * t) * t)
    if noise:
        tone = tone * (1 - noise) + np.random.uniform(-1, 1, len(t)) * noise
    envelope = np.linspace(1, 0, len(t))
    audio = (tone * envelope * volume * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(audio)

SOUNDS = {
    "click": make_sound(740, 0.035, 0.18),
    "open": make_sound(520, 0.08, 0.18, 0.1, 600),
    "close": make_sound(330, 0.08, 0.18, 0.05, -300),
    "jump": make_sound(460, 0.09, 0.22, 0.05, 500),
    "place": make_sound(160, 0.08, 0.28, 0.55),
    "break": make_sound(95, 0.12, 0.30, 0.75),
    "craft": make_sound(880, 0.12, 0.22, 0.05, 700),
    "step": make_sound(130, 0.045, 0.14, 0.65),
    "swim": make_sound(210, 0.08, 0.16, 0.80),
    "shoot": make_sound(180, 0.07, 0.25, 0.45, -700),
}

def play_sound(name):
    sound = SOUNDS.get(name)
    if sound:
        sound.play()

def get_chunk_and_local(abs_block_x):
    chunk_idx = int(abs_block_x // CHUNK_SIZE)
    local_x = int(abs_block_x % CHUNK_SIZE)
    return chunk_idx, local_x

def generate_chunk_for_index(chunk_idx):
    return terrain.generate_chunk(WORLD_ROWS, CHUNK_SIZE, chunk_idx * CHUNK_SIZE, WORLD_SEED)

def chunk_matches_generated(chunk_idx, chunk):
    return np.array_equal(chunk, generate_chunk_for_index(chunk_idx))

def load_or_generate_chunk(chunk_idx):
    if chunk_idx not in active_chunks:
        if chunk_idx in saved_chunks:
            active_chunks[chunk_idx] = saved_chunks[chunk_idx].copy()
        else:
            active_chunks[chunk_idx] = generate_chunk_for_index(chunk_idx)

def get_block_at(abs_block_x, block_y):
    if block_y < 0 or block_y >= WORLD_ROWS: return 0
    c_idx, lx = get_chunk_and_local(abs_block_x)
    load_or_generate_chunk(c_idx)
    return active_chunks[c_idx][block_y, lx]

def set_block_at(abs_block_x, block_y, block_id):
    if block_y < 0 or block_y >= WORLD_ROWS: return
    c_idx, lx = get_chunk_and_local(abs_block_x)
    load_or_generate_chunk(c_idx)
    if int(active_chunks[c_idx][block_y, lx]) == int(block_id):
        return
    active_chunks[c_idx][block_y, lx] = block_id
    saved_chunks[c_idx] = active_chunks[c_idx].copy()
    dirty_chunks.add(c_idx)

def block_key(abs_block_x, block_y):
    return f"{abs_block_x},{block_y}"

def display_world_y(block_y):
    return DISPLAY_Y_ZERO_BLOCK - int(block_y)

def is_player_in_void():
    return player_py > (WORLD_ROWS + VOID_DEATH_MARGIN_BLOCKS) * render.TILE_SIZE

def parse_block_key(key):
    try:
        x_text, y_text = str(key).split(",", 1)
        return int(x_text), int(y_text)
    except (TypeError, ValueError):
        return None

def block_distance_from_player(abs_block_x, block_y):
    return math.hypot(abs_block_x - player_block_center_x, block_y - int(player_py // render.TILE_SIZE))

def trim_spatial_dict(data, max_items, preserve_key=None):
    if len(data) <= max_items:
        return
    keyed_distances = []
    for key in list(data.keys()):
        if key == preserve_key:
            continue
        pos = parse_block_key(key)
        if not pos:
            keyed_distances.append((float("inf"), key))
            continue
        keyed_distances.append((block_distance_from_player(pos[0], pos[1]), key))
    keyed_distances.sort(reverse=True)
    for _, key in keyed_distances[:max(0, len(data) - max_items)]:
        data.pop(key, None)

def chest_value_is_empty(value):
    slots = value.get("slots", []) if isinstance(value, dict) else value
    return not slots or all(not item or is_empty(item) for item in slots)

def trim_empty_chests(max_items):
    if len(chests) <= max_items:
        return
    removable = []
    for key, value in list(chests.items()):
        if key == open_chest_key or not chest_value_is_empty(value):
            continue
        pos = parse_block_key(key)
        distance = float("inf") if not pos else block_distance_from_player(pos[0], pos[1])
        removable.append((distance, key))
    removable.sort(reverse=True)
    for _, key in removable[:max(0, len(chests) - max_items)]:
        chests.pop(key, None)

def compact_dirty_chunks():
    for chunk_idx in list(dirty_chunks):
        chunk = saved_chunks.get(chunk_idx)
        if chunk is None:
            dirty_chunks.discard(chunk_idx)
        elif chunk_matches_generated(chunk_idx, chunk):
            saved_chunks.pop(chunk_idx, None)
            dirty_chunks.discard(chunk_idx)

def unload_far_chunks_around(center_block_x):
    center_chunk_idx, _ = get_chunk_and_local(center_block_x)
    for chunk_idx in list(active_chunks.keys()):
        if abs(chunk_idx - center_chunk_idx) > ACTIVE_CHUNK_KEEP_RADIUS:
            del active_chunks[chunk_idx]

def unload_far_chunks():
    unload_far_chunks_around(player_block_center_x)

def cleanup_runtime_resources(force=False):
    global last_resource_cleanup_frame
    if not force and frame_count - last_resource_cleanup_frame < RESOURCE_CLEANUP_INTERVAL:
        return
    last_resource_cleanup_frame = frame_count
    unload_far_chunks()
    trim_empty_chests(MAX_PERSISTENT_CHESTS)
    trim_spatial_dict(covered_blocks, MAX_COVERED_BLOCKS)
    trim_spatial_dict(planted_crops, MAX_PLANTED_CROPS)
    del projectiles[MAX_PROJECTILES:]
    del dropped_items[MAX_DROPPED_ITEMS:]

def player_touches_block(abs_block_x, block_y):
    left = int(player_abs_px + 6) // render.TILE_SIZE
    right = int(player_abs_px + render.TILE_SIZE - 6) // render.TILE_SIZE
    top = int(player_py + 2) // render.TILE_SIZE
    bottom = int(player_py + render.TILE_SIZE - 1) // render.TILE_SIZE
    return left - 1 <= abs_block_x <= right + 1 and top - 1 <= block_y <= bottom + 1

def mining_line_blocked(abs_block_x, block_y):
    start_x = player_abs_px + render.TILE_SIZE / 2
    start_y = player_py + render.TILE_SIZE / 2
    end_x = abs_block_x * render.TILE_SIZE + render.TILE_SIZE / 2
    end_y = block_y * render.TILE_SIZE + render.TILE_SIZE / 2
    dx, dy = end_x - start_x, end_y - start_y
    steps = max(1, int(max(abs(dx), abs(dy)) / (render.TILE_SIZE / 8)))

    for i in range(1, steps):
        sample_x = start_x + dx * i / steps
        sample_y = start_y + dy * i / steps
        sample_block_x = int(sample_x // render.TILE_SIZE)
        sample_block_y = int(sample_y // render.TILE_SIZE)
        if sample_block_x == abs_block_x and sample_block_y == block_y:
            continue
        if get_block_at(sample_block_x, sample_block_y) not in NON_SOLID_BLOCKS:
            return True
    return False

def can_mine_block(abs_block_x, block_y):
    block_id = int(get_block_at(abs_block_x, block_y))
    if block_id in (0, 7):
        return False
    if player_touches_block(abs_block_x, block_y):
        return True

    player_center_x = player_abs_px + render.TILE_SIZE / 2
    player_center_y = player_py + render.TILE_SIZE / 2
    block_center_x = abs_block_x * render.TILE_SIZE + render.TILE_SIZE / 2
    block_center_y = block_y * render.TILE_SIZE + render.TILE_SIZE / 2
    distance_blocks = math.hypot(block_center_x - player_center_x, block_center_y - player_center_y) / render.TILE_SIZE
    if distance_blocks > MINE_REACH_BLOCKS:
        return False
    return not mining_line_blocked(abs_block_x, block_y)

def get_break_replacement_block(abs_block_x, block_y):
    key = block_key(abs_block_x, block_y)
    covered_block = covered_blocks.pop(key, None)
    if covered_block is not None:
        return int(covered_block)

    for nx, ny in ((abs_block_x, block_y - 1), (abs_block_x - 1, block_y), (abs_block_x + 1, block_y)):
        if int(get_block_at(nx, ny)) == 7:
            return 7
    return 0

def get_selected_item_id():
    item = inventory[selected_slot]
    return item["id"] if item["count"] > 0 else 0

def get_block_category(block_id):
    return BLOCK_CATEGORIES.get(int(block_id), "stone")

def get_current_mine_time(block_id):
    category = get_block_category(block_id)
    selected_id = get_selected_item_id()
    speed = TOOL_SPEEDS.get(selected_id, {}).get(category, 1.0)
    if selected_id in enchanted_item_ids:
        speed *= 1.35
    if category == "leaves":
        speed = max(speed, 2.5)
    hardness = BLOCK_HARDNESS.get(int(block_id), 1.0)
    return max(5, int(MINE_MAX_TIME * hardness / speed))

def get_attack_damage():
    selected_id = get_selected_item_id()
    damage = WEAPON_DAMAGE.get(selected_id, 1)
    return damage + (2 if selected_id in enchanted_item_ids else 0)

def is_night():
    t = world_time % DAY_LENGTH_FRAMES
    return 13000 <= t <= 23000

def get_sky_color_for_time():
    t = world_time % DAY_LENGTH_FRAMES
    if t < 10000:
        return (120, 180, 255)
    if t < 13000:
        k = (t - 10000) / 3000
        return (int(120 * (1-k) + 40 * k), int(180 * (1-k) + 70 * k), int(255 * (1-k) + 130 * k))
    if t < 23000:
        return (22, 28, 55)
    k = (t - 23000) / 1000
    return (int(22 * (1-k) + 120 * k), int(28 * (1-k) + 180 * k), int(55 * (1-k) + 255 * k))

def simple_noise_1d(x, seed):
    n = int(x) + seed * 57
    n = (n << 13) ^ n
    return 1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0

def smooth_interpolate(a, b, x):
    f = (1 - math.cos(x * math.pi)) * 0.5
    return a * (1 - f) + b * f

def terrain_noise_1d(x, seed):
    integer_x = math.floor(x)
    fractional_x = x - integer_x
    return smooth_interpolate(simple_noise_1d(integer_x, seed), simple_noise_1d(integer_x + 1, seed), fractional_x)

def get_biome_at(abs_block_x):
    temperature = terrain_noise_1d((abs_block_x + WORLD_SEED * 200) * 0.015, WORLD_SEED + 1)
    if temperature < -0.2:
        return "ocean"
    if temperature < 0.1:
        return "desert"
    if temperature > 0.4:
        return "jungle"
    return "plains"

def find_spawn_y(abs_block_x):
    for y in range(WORLD_ROWS - 2):
        if get_block_at(abs_block_x, y) in NON_SOLID_BLOCKS and get_block_at(abs_block_x, y + 1) not in NON_SOLID_BLOCKS:
            return y * render.TILE_SIZE
    return None

def find_safe_player_spawn():
    offsets = [0]
    for radius in range(1, 260):
        offsets.extend((radius, -radius))

    for abs_block_x in offsets:
        biome = get_biome_at(abs_block_x)
        if biome not in ("jungle", "desert"):
            continue
        expected_ground = 6 if biome == "desert" else 1
        for y in range(1, WORLD_ROWS - 1):
            feet_block = int(get_block_at(abs_block_x, y))
            head_block = int(get_block_at(abs_block_x, y - 1))
            ground_block = int(get_block_at(abs_block_x, y + 1))
            if ground_block != expected_ground:
                continue
            if feet_block != 0 or head_block == 7:
                continue
            if any(int(get_block_at(abs_block_x + nx, y)) == 7 for nx in (-1, 0, 1)):
                continue
            unload_far_chunks_around(abs_block_x)
            return abs_block_x * render.TILE_SIZE, y * render.TILE_SIZE

    for abs_block_x in offsets:
        for y in range(1, WORLD_ROWS - 1):
            if int(get_block_at(abs_block_x, y)) == 0 and int(get_block_at(abs_block_x, y + 1)) in (1, 6):
                unload_far_chunks_around(abs_block_x)
                return abs_block_x * render.TILE_SIZE, y * render.TILE_SIZE
    unload_far_chunks_around(0)
    return 0.0, 100.0

def spawn_blood_particles(x, y, source_x=None, source_y=None):
    away_x = 0.0 if source_x is None else x - source_x
    away_y = -1.0 if source_y is None else y - source_y
    length = max(1.0, math.hypot(away_x, away_y))
    for _ in range(18):
        speed = random.uniform(1.2, 4.2)
        vx = away_x / length * speed + random.uniform(-1.6, 1.6)
        vy = away_y / length * speed + random.uniform(-3.2, -0.3)
        particles.append([
            x + random.uniform(-8, 8),
            y + random.uniform(-4, 8),
            vx,
            vy,
            random.randint(18, 34),
            (15, 15, random.randint(150, 235)),
            random.randint(3, 6),
        ])
    if len(particles) > 180:
        del particles[:len(particles) - 180]

def update_particles():
    for p in particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[3] += GRAVITY * 0.28
        p[4] -= 1
        if p[4] <= 0:
            particles.remove(p)

def damage_player(amount, source_x=None, source_y=None):
    global hp
    if source_x is not None or source_y is not None:
        armor_points = sum(DIAMOND_ARMOR_DEFENSE.get(item_id, 0) for item_id in equipped_armor.values())
        amount = max(0, amount - armor_points // 3)
    old_hp = hp
    hp = max(0, hp - max(0, amount))
    if hp < old_hp:
        spawn_blood_particles(player_abs_px + render.TILE_SIZE / 2, player_py + render.TILE_SIZE / 2, source_x, source_y)

def update_hunger(is_sprinting_now):
    global hunger, last_hunger_decay_frame, last_sprint_hunger_frame, last_starve_damage_frame
    if hunger > 0 and frame_count - last_hunger_decay_frame >= HUNGER_DECAY_INTERVAL:
        hunger = max(0, hunger - 1)
        last_hunger_decay_frame = frame_count
    if hunger > 0 and is_sprinting_now and frame_count - last_sprint_hunger_frame >= SPRINT_HUNGER_INTERVAL:
        hunger = max(0, hunger - 1)
        last_sprint_hunger_frame = frame_count
    if hunger <= 0 and frame_count - last_starve_damage_frame >= STARVE_DAMAGE_INTERVAL:
        damage_player(1)
        last_starve_damage_frame = frame_count

def drop_item_stack(item, x, y):
    if is_empty(item):
        return
    if len(dropped_items) >= MAX_DROPPED_ITEMS:
        dropped_items.pop(0)
    drop = {
        "id": int(item["id"]),
        "count": int(item["count"]),
        "x": float(x),
        "y": float(y),
        "vx": random.uniform(-2.6, 2.6),
        "vy": random.uniform(-6.0, -2.0),
        "age": 0,
    }
    if "durability" in item:
        drop["durability"] = int(item["durability"])
    dropped_items.append(drop)

def drop_selected_item():
    item = inventory[selected_slot]
    if is_empty(item):
        return False
    drop = {"id": item["id"], "count": 1}
    if "durability" in item:
        drop["durability"] = item["durability"]
    direction = 1 if facing_right else -1
    drop_x = player_abs_px + render.TILE_SIZE / 2 + direction * 12
    drop_y = player_py + render.TILE_SIZE / 2
    drop_item_stack(drop, drop_x, drop_y)
    dropped_items[-1]["vx"] = direction * 3.2
    item["count"] -= 1
    normalize_item(item)
    play_sound("click")
    return True

def count_item(item_id):
    return sum(slot["count"] for slot in inventory if slot["id"] == item_id)

def consume_item(item_id, amount=1):
    if count_item(item_id) < amount:
        return False
    remaining = amount
    for slot in inventory:
        if slot["id"] == item_id and slot["count"] > 0:
            take = min(slot["count"], remaining)
            slot["count"] -= take
            remaining -= take
            normalize_item(slot)
            if remaining <= 0:
                return True
    return False

def fire_gun(target_world_x, target_world_y):
    gun_id = get_selected_item_id()
    stats = GUN_STATS.get(gun_id)
    if not stats or len(projectiles) >= MAX_PROJECTILES:
        return False
    if count_item(40) < stats["cost"]:
        return False
    consume_item(40, stats["cost"])
    start_x = player_abs_px + render.TILE_SIZE / 2
    start_y = player_py + render.TILE_SIZE / 2
    dx, dy = target_world_x - start_x, target_world_y - start_y
    length = max(1.0, math.hypot(dx, dy))
    projectiles.append({
        "x": start_x,
        "y": start_y,
        "vx": dx / length * stats["speed"],
        "vy": dy / length * stats["speed"],
        "damage": stats["damage"] + (2 if gun_id in enchanted_item_ids else 0),
        "life": 90,
        "kind": gun_id,
    })
    damage_selected_item(1)
    play_sound("shoot")
    return True

def eat_selected_food():
    global hp, hunger
    item = inventory[selected_slot]
    food = FOOD_VALUES.get(item["id"])
    if not food or item["count"] <= 0:
        return False
    if hp >= 10 and hunger >= 10:
        return False
    hp = min(10, hp + food["hp"])
    hunger = min(10, hunger + food["hunger"])
    item["count"] -= 1
    normalize_item(item)
    play_sound("craft")
    return True

def equip_selected_armor():
    global trader_message
    item = inventory[selected_slot]
    slot_name = DIAMOND_ARMOR_SLOTS.get(item["id"])
    if not slot_name or item["count"] <= 0:
        return False
    old_item_id = equipped_armor.get(slot_name, 0)
    equipped_armor[slot_name] = item["id"]
    item["count"] -= 1
    normalize_item(item)
    if old_item_id:
        add_to_inventory({"id": old_item_id, "count": 1})
    trader_message = f"Equipped {ITEM_NAMES.get(equipped_armor[slot_name], 'Armor')}."
    play_sound("craft")
    return True

def use_furnace_block():
    global trader_message
    if count_item(15) <= 0:
        trader_message = "Furnace needs Coal."
        play_sound("click")
        return False
    for source_id, recipe in FURNACE_RECIPES.items():
        if count_item(source_id) > 0 and inventory_has_room({"id": recipe["result"], "count": 1}):
            consume_item(15, 1)
            consume_item(source_id, 1)
            add_to_inventory({"id": recipe["result"], "count": 1})
            trader_message = f"Furnace smelted {recipe['name']}."
            play_sound("craft")
            return True
    trader_message = "Furnace can smelt ore, Cobblestone, or raw food."
    play_sound("click")
    return False

def use_stonecutter_block():
    global trader_message
    if count_item(29) >= 6 and inventory_has_room({"id": 56, "count": 6}):
        consume_item(29, 6)
        add_to_inventory({"id": 56, "count": 6})
        trader_message = "Stonecutter made Cobblestone Wall x6."
        play_sound("craft")
        return True
    if count_item(3) >= 3 and inventory_has_room({"id": 64, "count": 3}):
        consume_item(3, 3)
        add_to_inventory({"id": 64, "count": 3})
        trader_message = "Stonecutter polished Stone into Smooth Stone."
        play_sound("craft")
        return True
    trader_message = "Stonecutter needs Cobblestone x6 or Stone x3."
    play_sound("click")
    return False

def use_lever_block(abs_block_x, block_y):
    global trader_message
    torch_y = block_y - 1
    if int(get_block_at(abs_block_x, torch_y)) == 16:
        set_block_at(abs_block_x, torch_y, 0)
        trader_message = "Lever turned the signal off."
    elif int(get_block_at(abs_block_x, torch_y)) in NON_SOLID_BLOCKS:
        set_block_at(abs_block_x, torch_y, 16)
        trader_message = "Lever turned the signal on."
    else:
        trader_message = "Lever needs empty space above."
    play_sound("place")
    return True

def use_enchanting_table():
    global player_xp, trader_message
    selected_id = get_selected_item_id()
    if selected_id not in ENCHANTABLE_ITEMS:
        trader_message = "Enchanting Table needs a tool or weapon in hand."
        play_sound("click")
        return False
    if selected_id in enchanted_item_ids:
        trader_message = f"{ITEM_NAMES.get(selected_id, 'Item')} is already enchanted."
        play_sound("click")
        return False
    if player_xp < 5:
        trader_message = "Enchanting needs current XP 5."
        play_sound("click")
        return False
    player_xp -= 5
    enchanted_item_ids.append(selected_id)
    trader_message = f"Enchanted {ITEM_NAMES.get(selected_id, 'Item')}."
    play_sound("craft")
    return True

def use_jukebox_block():
    global trader_message
    play_sound("open")
    add_player_xp(1)
    trader_message = "Jukebox played a song. +1 XP."
    return True

def use_hoe_on_block(abs_block_x, block_y):
    global trader_message
    if get_selected_item_id() != 53:
        return False
    if int(get_block_at(abs_block_x, block_y)) in (1, 2):
        set_block_at(abs_block_x, block_y, 77)
        damage_selected_item(1)
        trader_message = "Tilled soil into Farmland."
        play_sound("place")
        return True
    return False

def plant_seed(abs_block_x, block_y):
    global trader_message
    item = inventory[selected_slot]
    if item["id"] != 75 or item["count"] <= 0:
        return False
    if int(get_block_at(abs_block_x, block_y)) == 77 and int(get_block_at(abs_block_x, block_y - 1)) in NON_SOLID_BLOCKS:
        crop_x, crop_y = abs_block_x, block_y - 1
        set_block_at(crop_x, crop_y, 78)
        planted_crops[block_key(crop_x, crop_y)] = {"stage": 0, "last": frame_count}
        item["count"] -= 1
        normalize_item(item)
        trader_message = "Seeds planted."
        play_sound("place")
        return True
    return False

def harvest_crop(abs_block_x, block_y):
    global trader_message
    if int(get_block_at(abs_block_x, block_y)) != 78:
        return False
    crop = planted_crops.get(block_key(abs_block_x, block_y), {"stage": 3})
    if crop.get("stage", 0) < 3:
        trader_message = "Wheat is still growing."
        play_sound("click")
        return True
    set_block_at(abs_block_x, block_y, 0)
    planted_crops.pop(block_key(abs_block_x, block_y), None)
    add_to_inventory({"id": 76, "count": random.randint(1, 2)})
    add_to_inventory({"id": 75, "count": random.randint(0, 2)})
    trader_message = "Harvested Wheat."
    play_sound("craft")
    return True

def update_crops():
    global last_crop_update_frame
    if frame_count - last_crop_update_frame < 120:
        return
    last_crop_update_frame = frame_count
    for key, crop in list(planted_crops.items()):
        x_str, y_str = key.split(",")
        crop_x, crop_y = int(x_str), int(y_str)
        if int(get_block_at(crop_x, crop_y)) != 78:
            planted_crops.pop(key, None)
            continue
        if frame_count - crop.get("last", 0) >= CROP_GROW_INTERVAL and crop.get("stage", 0) < 3:
            crop["stage"] = crop.get("stage", 0) + 1
            crop["last"] = frame_count

def update_village():
    global last_village_update_frame
    if frame_count - last_village_update_frame < VILLAGE_UPDATE_INTERVAL:
        return
    last_village_update_frame = frame_count
    built_houses = sum(1 for structure in structures if not structure.get("queue"))
    village_stats["houses"] = built_houses
    if built_houses:
        village_stats["supplies"] = village_stats.get("supplies", 0) + built_houses
        if village_stats["supplies"] >= 8:
            village_stats["supplies"] -= 8
            add_to_inventory({"id": random.choice([75, 76, 79, 15]), "count": 1})
    for npc in npcs:
        if npc.get("job") == "guard":
            for mob in mobs:
                if math.hypot(mob["x"] - npc["x"], mob["y"] - npc["y"]) < render.TILE_SIZE * 3:
                    mob["hp"] -= 1
                    mob["aggro"] = True
                    break

def xp_to_next_level(level):
    level = max(1, int(level))
    if level <= len(PRE_BOSS_XP_REQUIREMENTS):
        return PRE_BOSS_XP_REQUIREMENTS[level - 1]
    post_boss_level = level - BOSS_UNLOCK_LEVEL
    return 255 + post_boss_level * 42 + post_boss_level * post_boss_level * 4

def add_player_xp(amount):
    global player_xp, player_level
    player_xp += max(0, amount)
    while player_xp >= xp_to_next_level(player_level):
        player_xp -= xp_to_next_level(player_level)
        player_level += 1
        play_sound("craft")

def add_kill_rewards(mob_type):
    global money
    reward = MOB_REWARDS.get(mob_type, {"xp": 3, "money": 2})
    add_player_xp(reward["xp"])
    money += reward["money"]
    return reward

def ore_cost_text(ores):
    parts = []
    for item_id, amount in ores.items():
        parts.append(f"{ITEM_NAMES.get(item_id, item_id)} x{amount}")
    return ", ".join(parts)

def trade_cost_text(trade):
    parts = []
    if trade.get("money", 0):
        parts.append(f"${trade['money']}")
    if trade.get("xp", 0):
        parts.append(f"XP {trade['xp']}")
    if trade.get("ores"):
        parts.append(ore_cost_text(trade["ores"]))
    return " + ".join(parts) if parts else "Free"

def get_trade_view():
    trades = []
    for trade in TRADER_TRADES:
        shown = trade.copy()
        shown["cost_text"] = trade_cost_text(trade)
        trades.append(shown)
    return trades

def can_afford_trade(trade):
    if money < trade.get("money", 0):
        return False, "Need more money."
    if player_xp < trade.get("xp", 0):
        return False, "Need more current XP."
    if not inventory_has_room(trade["result"]):
        return False, "Inventory is full."
    for item_id, amount in trade.get("ores", {}).items():
        if count_item(item_id) < amount:
            return False, f"Need {ITEM_NAMES.get(item_id, item_id)} x{amount}."
    return True, ""

def buy_trade(index):
    global money, player_xp, trader_message
    if index is None or index < 0 or index >= len(TRADER_TRADES):
        return False
    trade = TRADER_TRADES[index]
    ok, reason = can_afford_trade(trade)
    if not ok:
        trader_message = reason
        play_sound("click")
        return False
    money -= trade.get("money", 0)
    player_xp -= trade.get("xp", 0)
    for item_id, amount in trade.get("ores", {}).items():
        consume_item(item_id, amount)
    add_to_inventory(trade["result"])
    trader_message = f"Bought {trade['name']}."
    play_sound("craft")
    return True

def drop_mob_loot(mob):
    if mob.get("type") == "ancient_boss":
        drop_item_stack({"id": 40, "count": random.randint(32, 56)}, mob["x"], mob["y"])
        drop_item_stack({"id": 24, "count": random.randint(2, 4)}, mob["x"], mob["y"])
        drop_item_stack({"id": 35, "count": random.randint(5, 9)}, mob["x"], mob["y"])
        drop_item_stack({"id": 71, "count": 1}, mob["x"], mob["y"])
        if random.random() < 0.55:
            drop_item_stack({"id": 44, "count": 1}, mob["x"], mob["y"])
        return
    bullet_count = random.randint(2, 5)
    if mob.get("type") in ("green_jet", "crystal_wisp"):
        bullet_count += random.randint(1, 3)
    drop_item_stack({"id": 40, "count": bullet_count}, mob["x"], mob["y"])
    mob_type = mob.get("type")
    if mob_type in ("zombie", "cave_zombie"):
        drop_item_stack({"id": 67, "count": random.randint(1, 3)}, mob["x"], mob["y"])
    elif mob_type == "skeleton":
        drop_item_stack({"id": 68, "count": random.randint(1, 3)}, mob["x"], mob["y"])
    elif mob_type == "cave_spider":
        drop_item_stack({"id": 69, "count": random.randint(1, 3)}, mob["x"], mob["y"])
    elif mob_type == "slime":
        drop_item_stack({"id": 70, "count": random.randint(1, 2)}, mob["x"], mob["y"])
    elif mob_type == "crystal_wisp":
        drop_item_stack({"id": 73, "count": 1}, mob["x"], mob["y"])
    if random.random() < 0.25:
        drop_item_stack({"id": 15, "count": 1}, mob["x"], mob["y"])

def damage_mob(index, damage, source_x, source_y, knockback=3.0):
    if index is None or index < 0 or index >= len(mobs):
        return False
    mob = mobs[index]
    mob["hp"] -= damage
    mob["aggro"] = True
    dx = (mob["x"] + render.TILE_SIZE / 2) - source_x
    dy = (mob["y"] + render.TILE_SIZE / 2) - source_y
    length = max(1.0, math.hypot(dx, dy))
    mob["vx"] = mob.get("vx", 0.0) + dx / length * knockback
    mob["vy"] = min(mob.get("vy", 0.0), -2.4) + dy / length * 1.4
    if mob["hp"] <= 0:
        reward = add_kill_rewards(mob.get("type", "zombie"))
        spawn_blood_particles(mob["x"] + render.TILE_SIZE / 2, mob["y"] + render.TILE_SIZE / 2, source_x, source_y)
        drop_mob_loot(mob)
        mobs.pop(index)
        global trader_message
        trader_message = f"+{reward['xp']} XP  +${reward['money']}"
    play_sound("break")
    return True

def get_animal_food_drop(animal_type):
    return {
        "chicken": {"id": 47, "count": random.randint(1, 2)},
        "pig": {"id": 48, "count": random.randint(1, 3)},
        "cow": {"id": 49, "count": random.randint(1, 3)},
        "sheep": {"id": 50, "count": random.randint(1, 2)},
        "deer": {"id": 51, "count": random.randint(2, 3)},
    }.get(animal_type, {"id": 49, "count": 1})

def damage_animal(index, damage, source_x, source_y):
    if index is None or index < 0 or index >= len(animals):
        return False
    animal = animals[index]
    animal_type = animal.get("type", "cow")
    animal["max_hp"] = animal.get("max_hp", ANIMAL_MAX_HP.get(animal_type, 8))
    animal["hp"] = animal.get("hp", animal["max_hp"]) - damage
    dx = (animal["x"] + render.TILE_SIZE / 2) - source_x
    dy = (animal["y"] + render.TILE_SIZE / 2) - source_y
    length = max(1.0, math.hypot(dx, dy))
    animal["vx"] = animal.get("vx", 0.0) + dx / length * 2.0
    animal["vy"] = min(animal.get("vy", 0.0), -2.2) + dy / length * 0.8
    spawn_blood_particles(animal["x"] + render.TILE_SIZE / 2, animal["y"] + render.TILE_SIZE / 2, source_x, source_y)
    if animal["hp"] <= 0:
        drop_item_stack(get_animal_food_drop(animal_type), animal["x"], animal["y"])
        animals.pop(index)
    play_sound("break")
    return True

def clear_item(item):
    item["id"], item["count"] = 0, 0
    item.pop("durability", None)

def drop_all_player_items():
    death_x = player_abs_px + render.TILE_SIZE / 2
    death_y = player_py + render.TILE_SIZE / 2
    for slot in inventory:
        drop_item_stack(slot, death_x, death_y)
        clear_item(slot)
    for slot in crafting_grid:
        drop_item_stack(slot, death_x, death_y)
        clear_item(slot)
    for slot in crafting_table_grid:
        drop_item_stack(slot, death_x, death_y)
        clear_item(slot)
    drop_item_stack(cursor_item, death_x, death_y)
    clear_item(cursor_item)
    for slot_name, item_id in list(equipped_armor.items()):
        if item_id:
            drop_item_stack({"id": item_id, "count": 1}, death_x, death_y)
            equipped_armor[slot_name] = 0
    check_crafting_recipes()

def respawn_player():
    global player_abs_px, player_py, vel_x, vel_y, hp, hunger, current_state, is_mining
    player_abs_px, player_py = find_safe_player_spawn()
    vel_x, vel_y = 0.0, 0.0
    hp, hunger = 10, 10
    ensure_starter_kit()
    current_state = render.STATE_GAME
    is_mining = False

def handle_player_death():
    global hp, trader_message
    if is_player_in_void():
        hp = 0
        trader_message = "You fell into the void."
    if hp > 0:
        return
    drop_all_player_items()
    play_sound("break")
    respawn_player()

def update_dropped_items():
    for drop in dropped_items[:]:
        drop["age"] = drop.get("age", 0) + 1
        if drop["age"] > MAX_DROP_AGE_FRAMES:
            dropped_items.remove(drop)
            continue
        drop["vy"] = min(8.0, drop.get("vy", 0.0) + GRAVITY * 0.45)

        new_x = drop["x"] + drop.get("vx", 0.0)
        if get_block_at(int(new_x // render.TILE_SIZE), int(drop["y"] // render.TILE_SIZE)) in NON_SOLID_BLOCKS:
            drop["x"] = new_x
        else:
            drop["vx"] = -drop.get("vx", 0.0) * 0.25

        new_y = drop["y"] + drop.get("vy", 0.0)
        if get_block_at(int(drop["x"] // render.TILE_SIZE), int(new_y // render.TILE_SIZE)) in NON_SOLID_BLOCKS:
            drop["y"] = new_y
        else:
            drop["vy"] = -abs(drop.get("vy", 0.0)) * 0.25
            drop["vx"] *= 0.85

        if drop["age"] > 45:
            close_enough = abs(drop["x"] - (player_abs_px + 20)) < 32 and abs(drop["y"] - (player_py + 20)) < 32
            if close_enough:
                pickup = {"id": drop["id"], "count": drop["count"]}
                if "durability" in drop:
                    pickup["durability"] = drop["durability"]
                remaining = add_to_inventory(pickup)
                if is_empty(remaining):
                    dropped_items.remove(drop)
                    play_sound("click")
                else:
                    drop["count"] = remaining["count"]

def update_projectiles():
    for shot in projectiles[:]:
        shot["life"] -= 1
        shot["x"] += shot["vx"]
        shot["y"] += shot["vy"]
        block_x = int(shot["x"] // render.TILE_SIZE)
        block_y = int(shot["y"] // render.TILE_SIZE)
        if shot["life"] <= 0 or get_block_at(block_x, block_y) not in NON_SOLID_BLOCKS:
            projectiles.remove(shot)
            continue

        hit_idx = find_mob_at_world(shot["x"], shot["y"])
        if hit_idx is not None:
            damage_mob(hit_idx, shot["damage"], shot["x"] - shot.get("vx", 0.0) * 2, shot["y"] - shot.get("vy", 0.0) * 2, 4.5)
            projectiles.remove(shot)

def is_spawn_protected(abs_block_x, block_y, radius=SPAWN_PROTECTION_RADIUS):
    for y in range(max(0, block_y - radius), min(WORLD_ROWS, block_y + radius + 1)):
        for x in range(abs_block_x - radius, abs_block_x + radius + 1):
            if int(get_block_at(x, y)) in SPAWN_PROTECTION_BLOCKS:
                return True
    return False

def reposition_trade_npc_near_player(npc):
    for _ in range(14):
        spawn_block_x = player_block_center_x + random.choice([-1, 1]) * random.randint(5, 10)
        spawn_y = find_spawn_y(spawn_block_x)
        if spawn_y is None:
            continue
        npc["x"] = float(spawn_block_x * render.TILE_SIZE)
        npc["y"] = float(spawn_y)
        npc["vx"] = 0.0
        npc["vy"] = 0.0
        npc["wander_cd"] = random.randint(60, 160)
        return True
    return False

def spawn_monster():
    if len(mobs) >= MAX_MOBS:
        return
    for _ in range(12):
        offset = random.choice([-1, 1]) * random.randint(8, 16)
        spawn_block_x = player_block_center_x + offset
        spawn_y = find_spawn_y(spawn_block_x)
        if spawn_y is None or is_spawn_protected(spawn_block_x, spawn_y):
            continue
        mob_type = random.choice(["zombie", "skeleton", "slime", "green_jet"])
        base_hp = {"zombie": 12, "skeleton": 10, "slime": 9, "green_jet": 8}[mob_type]
        mobs.append({
            "type": mob_type,
            "x": float(spawn_block_x * render.TILE_SIZE),
            "y": float(spawn_y - (render.TILE_SIZE if mob_type == "green_jet" else 0)),
            "vx": 0.0,
            "vy": 0.0,
            "hp": base_hp,
            "phase": random.random() * math.pi * 2,
        })
        break

def find_cave_spawn():
    for _ in range(24):
        spawn_block_x = player_block_center_x + random.choice([-1, 1]) * random.randint(5, 14)
        y = random.randint(WORLD_ROWS // 2 + 5, WORLD_ROWS - 3)
        if is_spawn_protected(spawn_block_x, y):
            continue
        if get_block_at(spawn_block_x, y) in NON_SOLID_BLOCKS and get_block_at(spawn_block_x, y + 1) not in NON_SOLID_BLOCKS:
            return spawn_block_x * render.TILE_SIZE, y * render.TILE_SIZE
    return None

def spawn_cave_monster():
    if len(mobs) >= MAX_MOBS:
        return
    pos = find_cave_spawn()
    if not pos:
        return
    x, y = pos
    mob_type = random.choice(["cave_zombie", "cave_spider", "crystal_wisp"])
    mobs.append({
        "type": mob_type,
        "x": float(x),
        "y": float(y),
        "vx": 0.0,
        "vy": 0.0,
        "hp": 14 if mob_type != "crystal_wisp" else 9,
        "phase": random.random() * math.pi * 2,
    })

def spawn_boss():
    global trader_message
    if player_level < BOSS_UNLOCK_LEVEL or any(mob.get("type") == "ancient_boss" for mob in mobs):
        return False
    if len(mobs) >= MAX_MOBS:
        for mob in mobs[:]:
            if not mob.get("aggro") and mob.get("type") != "ancient_boss":
                mobs.remove(mob)
                break
    for _ in range(18):
        offset = random.choice([-1, 1]) * random.randint(13, 22)
        spawn_block_x = player_block_center_x + offset
        spawn_y = find_spawn_y(spawn_block_x)
        if spawn_y is None:
            continue
        mobs.append({
            "type": "ancient_boss",
            "x": float(spawn_block_x * render.TILE_SIZE),
            "y": float(spawn_y - render.TILE_SIZE),
            "vx": 0.0,
            "vy": 0.0,
            "hp": 120,
            "max_hp": 120,
            "phase": random.random() * math.pi * 2,
            "aggro": True,
        })
        trader_message = "A Level 20 boss has appeared nearby."
        play_sound("break")
        return True
    return False

def spawn_animal():
    if len(animals) >= MAX_ANIMALS:
        return
    for _ in range(16):
        offset = random.choice([-1, 1]) * random.randint(5, 18)
        spawn_block_x = player_block_center_x + offset
        spawn_y = find_spawn_y(spawn_block_x)
        if spawn_y is None:
            continue
        animal_type = random.choice(["cow", "pig", "sheep", "chicken", "deer"])
        max_hp = ANIMAL_MAX_HP.get(animal_type, 8)
        animals.append({
            "type": animal_type,
            "x": float(spawn_block_x * render.TILE_SIZE),
            "y": float(spawn_y),
            "vx": random.choice([-0.5, 0.5]),
            "vy": 0.0,
            "hp": max_hp,
            "max_hp": max_hp,
            "wander": random.randint(30, 140),
        })
        break

def spawn_bird():
    if len(birds) >= MAX_BIRDS:
        return
    direction = random.choice([-1, 1])
    birds.append({
        "type": random.choice(["sparrow", "hawk", "crow"]),
        "x": float(player_abs_px + direction * random.randint(12, 22) * render.TILE_SIZE),
        "y": float(random.randint(2, 7) * render.TILE_SIZE),
        "vx": float(-direction * random.uniform(1.0, 2.4)),
        "phase": random.uniform(0, math.pi * 2),
    })

def spawn_plane():
    if len(planes) >= MAX_PLANES:
        return
    direction = random.choice([-1, 1])
    planes.append({
        "x": float(player_abs_px + direction * random.randint(22, 34) * render.TILE_SIZE),
        "y": float(random.randint(1, 4) * render.TILE_SIZE),
        "vx": float(-direction * random.uniform(2.4, 3.8)),
        "banner": random.choice(["SKY", "MINE", "AIR"]),
    })

def spawn_supply_plane():
    if len(supply_planes) >= MAX_SUPPLY_PLANES or random.random() > 0.45:
        return
    direction = random.choice([-1, 1])
    supply_planes.append({
        "type": random.choice(["cargo_plane", "blimp", "drone"]),
        "x": float(player_abs_px + direction * random.randint(26, 38) * render.TILE_SIZE),
        "y": float(random.randint(2, 5) * render.TILE_SIZE),
        "vx": float(-direction * random.uniform(1.8, 2.8)),
        "dropped": False,
        "phase": random.uniform(0, math.pi * 2),
    })

def spawn_sunbird():
    if len(sunbirds) >= MAX_SUNBIRDS:
        return
    direction = random.choice([-1, 1])
    sunbirds.append({
        "x": float(player_abs_px + direction * random.randint(14, 24) * render.TILE_SIZE),
        "y": float(random.randint(3, 8) * render.TILE_SIZE),
        "vx": float(-direction * random.uniform(1.4, 2.2)),
        "phase": random.uniform(0, math.pi * 2),
    })

def make_house_blueprint(base_x, ground_y, style=None):
    style = style or random.choice(["cabin", "tower", "hut", "workshop"])
    blocks = []
    if style == "tower":
        width, height = 5, 7
        for x in range(base_x, base_x + width):
            blocks.append((x, ground_y, 29))
        for y in range(ground_y - height, ground_y):
            blocks.append((base_x, y, 3))
            blocks.append((base_x + width - 1, y, 3))
        for x in range(base_x + 1, base_x + width - 1):
            blocks.append((x, ground_y - height, 29))
            blocks.append((x, ground_y - height - 1, 34 if x == base_x + 2 else 29))
        for y in (ground_y - 5, ground_y - 3):
            blocks.append((base_x + 2, y, 0))
        blocks.append((base_x + 2, ground_y - 1, 0))
        blocks.append((base_x + 2, ground_y - 2, 0))
        chest_x, chest_y = base_x + 3, ground_y - 1
    elif style == "hut":
        width, height = 6, 3
        for x in range(base_x, base_x + width):
            blocks.append((x, ground_y, 2))
        for y in range(ground_y - height, ground_y):
            blocks.append((base_x, y, 8))
            blocks.append((base_x + width - 1, y, 8))
        for x in range(base_x + 1, base_x + width - 1):
            blocks.append((x, ground_y - height, 9))
        blocks.append((base_x + 2, ground_y - height - 1, 9))
        blocks.append((base_x + 3, ground_y - height - 1, 9))
        blocks.append((base_x + 2, ground_y - 1, 0))
        blocks.append((base_x + 2, ground_y - 2, 0))
        chest_x, chest_y = base_x + 4, ground_y - 1
    elif style == "workshop":
        width, height = 8, 4
        for x in range(base_x, base_x + width):
            blocks.append((x, ground_y, 29))
        for y in range(ground_y - height, ground_y):
            blocks.append((base_x, y, 10))
            blocks.append((base_x + width - 1, y, 10))
        for x in range(base_x + 1, base_x + width - 1):
            blocks.append((x, ground_y - height, 8 if x % 2 else 10))
            blocks.append((x, ground_y - height - 1, 3))
        blocks.append((base_x + 2, ground_y - 1, 4))
        blocks.append((base_x + 3, ground_y - 1, 0))
        blocks.append((base_x + 3, ground_y - 2, 0))
        chest_x, chest_y = base_x + 6, ground_y - 1
    else:
        for x in range(base_x, base_x + 7):
            blocks.append((x, ground_y, 29))
        for y in range(ground_y - 4, ground_y):
            blocks.append((base_x, y, 10))
            blocks.append((base_x + 6, y, 10))
        for x in range(base_x + 1, base_x + 6):
            blocks.append((x, ground_y - 4, 8))
            blocks.append((x, ground_y - 5, 8 if x in (base_x + 2, base_x + 4) else 10))
        for x in range(base_x + 2, base_x + 5):
            blocks.append((x, ground_y - 1, 0))
            blocks.append((x, ground_y - 2, 0))
        chest_x, chest_y = base_x + 5, ground_y - 1
    blocks.append((chest_x, chest_y, 45))
    return blocks, chest_x, chest_y, style

def create_chest_loot():
    possible = [
        {"id": 10, "count": random.randint(8, 18)},
        {"id": 15, "count": random.randint(2, 6)},
        {"id": 40, "count": random.randint(6, 16)},
        {"id": 18, "count": random.randint(1, 3)},
        {"id": 35, "count": random.randint(1, 2)},
        {"id": 41, "count": 1},
        {"id": 65, "count": 1},
        {"id": 66, "count": random.randint(1, 2)},
        {"id": 75, "count": random.randint(2, 5)},
    ]
    random.shuffle(possible)
    return possible[:random.randint(2, 4)]

def create_airdrop_loot():
    possible = [
        {"id": 40, "count": random.randint(18, 36)},
        {"id": 47, "count": random.randint(2, 4)},
        {"id": 49, "count": random.randint(2, 4)},
        {"id": 15, "count": random.randint(4, 9)},
        {"id": 18, "count": random.randint(2, 5)},
        {"id": 35, "count": random.randint(1, 4)},
        {"id": 24, "count": 1},
        {"id": 65, "count": 1},
        {"id": 66, "count": random.randint(1, 3)},
        {"id": 75, "count": random.randint(3, 8)},
        {"id": 79, "count": random.randint(1, 3)},
        {"id": random.choice([19, 21, 30, 32, 41, 42]), "count": 1},
    ]
    random.shuffle(possible)
    return possible[:random.randint(3, 5)]

def spawn_house_with_npc():
    if len(structures) >= MAX_STRUCTURES or len(npcs) >= MAX_NPCS:
        return
    for _ in range(18):
        base_x = player_block_center_x + random.choice([-1, 1]) * random.randint(12, 24)
        ground_y_px = find_spawn_y(base_x)
        if ground_y_px is None:
            continue
        ground_y = int(ground_y_px // render.TILE_SIZE) + 1
        if ground_y < 8 or ground_y >= WORLD_ROWS - 2:
            continue
        blocks, chest_x, chest_y, style = make_house_blueprint(base_x, ground_y)
        house_id = f"house:{base_x}:{ground_y}"
        if any(s.get("id") == house_id for s in structures):
            continue
        structures.append({"id": house_id, "queue": blocks, "built": 0, "chest": [chest_x, chest_y], "style": style})
        npcs.append({
            "type": "villager",
            "x": float((base_x + 3) * render.TILE_SIZE),
            "y": float((ground_y - 1) * render.TILE_SIZE),
            "vx": 0.0,
            "vy": 0.0,
            "job": "builder",
            "house": house_id,
            "build_cd": 20,
            "wave": random.random() * math.pi,
        })
        chests[block_key(chest_x, chest_y)] = create_chest_loot()
        break

def start_house_at(base_x, ground_y):
    if len(structures) >= MAX_STRUCTURES:
        return False
    blocks, chest_x, chest_y, style = make_house_blueprint(base_x, ground_y)
    house_id = f"player_house:{base_x}:{ground_y}:{frame_count}"
    structures.append({"id": house_id, "queue": blocks, "built": 0, "chest": [chest_x, chest_y], "style": style})
    npcs.append({
        "type": "villager",
        "x": float((base_x + 3) * render.TILE_SIZE),
        "y": float((ground_y - 1) * render.TILE_SIZE),
        "vx": 0.0,
        "vy": 0.0,
        "job": "builder",
        "house": house_id,
        "build_cd": 8,
        "wave": random.random() * math.pi,
    })
    chests[block_key(chest_x, chest_y)] = create_chest_loot()
    return True

def spawn_wandering_npc():
    needs_trader = player_level >= TRADER_UNLOCK_LEVEL and not any(npc.get("job") in ("trader", "merchant") for npc in npcs)
    if needs_trader and len(npcs) >= MAX_NPCS:
        for npc in npcs[:]:
            if not npc.get("house") and npc.get("job") not in ("trader", "merchant"):
                npcs.remove(npc)
                break
    if len(npcs) >= MAX_NPCS:
        return
    for _ in range(12):
        offset = random.choice([-1, 1]) * random.randint(8, 22)
        spawn_block_x = player_block_center_x + offset
        spawn_y = find_spawn_y(spawn_block_x)
        if spawn_y is None:
            continue
        if needs_trader:
            jobs = ["trader"]
        else:
            jobs = ["wanderer", "miner", "guard"]
        if player_level >= TRADER_UNLOCK_LEVEL and not needs_trader:
            jobs.extend(["trader", "trader", "merchant"])
        job = random.choice(jobs)
        npcs.append({
            "type": "villager",
            "x": float(spawn_block_x * render.TILE_SIZE),
            "y": float(spawn_y),
            "vx": random.choice([-0.4, 0.4]),
            "vy": 0.0,
            "job": job,
            "build_cd": 0,
            "wave": random.random() * math.pi,
            "wander_cd": random.randint(45, 160),
        })
        break

def normalize_chest_slots(abs_block_x, block_y):
    key = block_key(abs_block_x, block_y)
    slots = chests.get(key)
    if slots is None:
        slots = []
    normalized = []
    for item in slots[:18]:
        if not item or is_empty(item):
            normalized.append(empty_item())
        else:
            normalized.append(copy_item(item))
    while len(normalized) < 18:
        normalized.append(empty_item())
    chests[key] = normalized
    return key, normalized

def open_chest_storage(abs_block_x, block_y):
    global current_state, open_chest_key, open_chest_slots
    open_chest_key, open_chest_slots = normalize_chest_slots(abs_block_x, block_y)
    current_state = render.STATE_CHEST
    play_sound("open")
    return True

def drop_chest_contents(abs_block_x, block_y):
    key = block_key(abs_block_x, block_y)
    slots = chests.pop(key, [])
    drop_x = abs_block_x * render.TILE_SIZE + render.TILE_SIZE / 2
    drop_y = block_y * render.TILE_SIZE + render.TILE_SIZE / 2
    for item in slots:
        drop_item_stack(item, drop_x, drop_y)

def find_mob_at_world(world_px, world_py):
    for idx, mob in enumerate(mobs):
        pad = 28 if mob.get("type") == "ancient_boss" else 4
        width = render.TILE_SIZE * (2 if mob.get("type") == "ancient_boss" else 1)
        height = render.TILE_SIZE * (2 if mob.get("type") == "ancient_boss" else 1)
        if mob["x"] - pad <= world_px <= mob["x"] + width + pad and mob["y"] - pad <= world_py <= mob["y"] + height + pad:
            return idx
    return None

def find_animal_at_world(world_px, world_py):
    for idx, animal in enumerate(animals):
        if animal["x"] - 4 <= world_px <= animal["x"] + render.TILE_SIZE + 4 and animal["y"] - 4 <= world_py <= animal["y"] + render.TILE_SIZE + 4:
            return idx
    return None

def find_npc_at_world(world_px, world_py):
    for idx, npc in enumerate(npcs):
        if npc["x"] - 8 <= world_px <= npc["x"] + render.TILE_SIZE + 8 and npc["y"] - 8 <= world_py <= npc["y"] + render.TILE_SIZE + 8:
            return idx
    return None

def can_trade_with_npc(npc):
    if player_level < TRADER_UNLOCK_LEVEL:
        return False
    if npc.get("job") not in ("trader", "merchant"):
        return False
    player_center_x = player_abs_px + render.TILE_SIZE / 2
    player_center_y = player_py + render.TILE_SIZE / 2
    npc_center_x = npc["x"] + render.TILE_SIZE / 2
    npc_center_y = npc["y"] + render.TILE_SIZE / 2
    return math.hypot(npc_center_x - player_center_x, npc_center_y - player_center_y) / render.TILE_SIZE <= 3.0

def can_attack_mob(mob):
    player_center_x = player_abs_px + render.TILE_SIZE / 2
    player_center_y = player_py + render.TILE_SIZE / 2
    mob_center_x = mob["x"] + render.TILE_SIZE / 2
    mob_center_y = mob["y"] + render.TILE_SIZE / 2
    distance_blocks = math.hypot(mob_center_x - player_center_x, mob_center_y - player_center_y) / render.TILE_SIZE
    if distance_blocks > MINE_REACH_BLOCKS:
        return False
    return not mining_line_blocked(int(mob_center_x // render.TILE_SIZE), int(mob_center_y // render.TILE_SIZE))

def can_attack_animal(animal):
    player_center_x = player_abs_px + render.TILE_SIZE / 2
    player_center_y = player_py + render.TILE_SIZE / 2
    animal_center_x = animal["x"] + render.TILE_SIZE / 2
    animal_center_y = animal["y"] + render.TILE_SIZE / 2
    return math.hypot(animal_center_x - player_center_x, animal_center_y - player_center_y) / render.TILE_SIZE <= MINE_REACH_BLOCKS

def update_mobs():
    global hp, last_player_damage_frame
    for mob in mobs[:]:
        kind = mob.get("type", "zombie")
        dx = player_abs_px - mob["x"]
        dy = player_py - mob["y"]
        distance_blocks = math.hypot(dx, dy) / render.TILE_SIZE
        mob["aggro"] = True if kind == "ancient_boss" else distance_blocks <= HOSTILE_AGGRO_BLOCKS
        mob["phase"] = mob.get("phase", 0.0) + 0.08

        if kind == "ancient_boss":
            if mob["aggro"]:
                mob["vx"] = max(-0.9, min(0.9, mob["vx"] + (0.065 if dx > 0 else -0.065)))
                if abs(dx) < render.TILE_SIZE * 4 and random.random() < 0.018:
                    mob["vy"] = min(mob.get("vy", 0.0), -7.2)

            new_x = mob["x"] + mob["vx"]
            if not check_collision(new_x, mob["y"]):
                mob["x"] = new_x
            else:
                mob["vx"] *= -0.35
                if random.random() < 0.10:
                    mob["vy"] = -6.0

            mob["vy"] += GRAVITY
            new_y = mob["y"] + mob["vy"]
            if not check_collision(mob["x"], new_y):
                mob["y"] = new_y
            else:
                mob["vy"] = 0
        elif kind in ("green_jet", "crystal_wisp"):
            max_speed = 1.75 if kind == "green_jet" else 1.35
            if mob["aggro"]:
                mob["vx"] = max(-max_speed, min(max_speed, mob["vx"] + (0.10 if dx > 0 else -0.10)))
                mob["vy"] = max(-max_speed, min(max_speed, mob["vy"] + (0.07 if dy > 0 else -0.07)))
            else:
                mob["vx"] = mob.get("vx", 0.0) * 0.94 + math.sin(mob["phase"]) * 0.08
                mob["vy"] = math.sin(mob["phase"] * 1.4) * 0.9

            new_x = mob["x"] + mob["vx"]
            if get_block_at(int((new_x + render.TILE_SIZE / 2) // render.TILE_SIZE), int((mob["y"] + render.TILE_SIZE / 2) // render.TILE_SIZE)) in NON_SOLID_BLOCKS:
                mob["x"] = new_x
            else:
                mob["vx"] *= -0.5

            new_y = mob["y"] + mob["vy"]
            if get_block_at(int((mob["x"] + render.TILE_SIZE / 2) // render.TILE_SIZE), int((new_y + render.TILE_SIZE / 2) // render.TILE_SIZE)) in NON_SOLID_BLOCKS:
                mob["y"] = new_y
            else:
                mob["vy"] *= -0.5
        else:
            if mob["aggro"]:
                mob["vx"] = max(-1.25, min(1.25, mob["vx"] + (0.11 if dx > 0 else -0.11)))
            elif random.random() < 0.018:
                mob["vx"] = random.choice([-0.45, 0.45])
            elif not mob["aggro"]:
                mob["vx"] *= 0.92

            if kind == "slime" and random.random() < (0.05 if mob["aggro"] else 0.018):
                mob["vy"] = min(mob.get("vy", 0.0), -6.8)

            new_x = mob["x"] + mob["vx"]
            if not check_collision(new_x, mob["y"]):
                mob["x"] = new_x
            else:
                mob["vx"] = 0
                if random.random() < 0.08:
                    mob["vy"] = -6.0

            mob["vy"] += GRAVITY
            new_y = mob["y"] + mob["vy"]
            if not check_collision(mob["x"], new_y):
                mob["y"] = new_y
            else:
                mob["vy"] = 0

        contact_x = 58 if kind == "ancient_boss" else 32
        contact_y = 70 if kind == "ancient_boss" else 36
        if abs((mob["x"] + 20) - (player_abs_px + 20)) < contact_x and abs((mob["y"] + 20) - (player_py + 20)) < contact_y:
            if frame_count - last_player_damage_frame > 45:
                damage = {"zombie": 2, "cave_zombie": 2, "cave_spider": 2, "green_jet": 2, "crystal_wisp": 2, "slime": 1, "skeleton": 1, "ancient_boss": 4}.get(kind, 1)
                damage_player(damage, mob["x"] + render.TILE_SIZE / 2, mob["y"] + render.TILE_SIZE / 2)
                last_player_damage_frame = frame_count
                play_sound("break")

        if mob["hp"] <= 0 or mob["y"] > WORLD_ROWS * render.TILE_SIZE or abs(mob["x"] - player_abs_px) > render.TILE_SIZE * 36:
            mobs.remove(mob)

def update_animals():
    for animal in animals[:]:
        animal_type = animal.get("type", "cow")
        animal["max_hp"] = animal.get("max_hp", ANIMAL_MAX_HP.get(animal_type, 8))
        animal["hp"] = animal.get("hp", animal["max_hp"])
        animal["wander"] = animal.get("wander", 0) - 1
        if animal["wander"] <= 0:
            speed_choices = {
                "chicken": [-1.0, -0.55, 0.0, 0.55, 1.0],
                "deer": [-1.4, -0.8, 0.0, 0.8, 1.4],
            }.get(animal_type, [-0.8, -0.45, 0.0, 0.45, 0.8])
            animal["vx"] = random.choice(speed_choices)
            animal["wander"] = random.randint(45, 180)
            if animal_type in ("chicken", "deer") and random.random() < 0.35:
                animal["vy"] = min(animal.get("vy", 0.0), -4.0)

        new_x = animal["x"] + animal.get("vx", 0.0)
        if not check_collision(new_x, animal["y"]):
            animal["x"] = new_x
        else:
            animal["vx"] = -animal.get("vx", 0.0) * 0.6

        animal["vy"] = animal.get("vy", 0.0) + GRAVITY
        new_y = animal["y"] + animal["vy"]
        if not check_collision(animal["x"], new_y):
            animal["y"] = new_y
        else:
            animal["vy"] = 0

        if abs(animal["x"] - player_abs_px) > render.TILE_SIZE * 28:
            animals.remove(animal)

def update_birds():
    for bird in birds[:]:
        bird["phase"] = bird.get("phase", 0.0) + 0.12
        bird["x"] += bird.get("vx", 0.0)
        bird["y"] += math.sin(bird["phase"]) * 0.45
        if abs(bird["x"] - player_abs_px) > render.TILE_SIZE * 30:
            birds.remove(bird)

def update_planes():
    for plane in planes[:]:
        plane["x"] += plane.get("vx", 0.0)
        if abs(plane["x"] - player_abs_px) > render.TILE_SIZE * 40:
            planes.remove(plane)

def update_supply_planes():
    for plane in supply_planes[:]:
        plane["phase"] = plane.get("phase", 0.0) + 0.06
        plane["x"] += plane.get("vx", 0.0)
        should_drop = not plane.get("dropped") and abs(plane["x"] - (player_abs_px + render.TILE_SIZE / 2)) < render.TILE_SIZE * 2.5
        if should_drop and len(supply_crates) < MAX_SUPPLY_CRATES:
            plane["dropped"] = True
            supply_crates.append({
                "x": plane["x"] + 18,
                "y": plane["y"] + 22,
                "vx": plane.get("vx", 0.0) * 0.18,
                "vy": 0.4,
                "phase": random.random() * math.pi * 2,
                "loot": create_airdrop_loot(),
            })
            play_sound("place")
        if abs(plane["x"] - player_abs_px) > render.TILE_SIZE * 44:
            supply_planes.remove(plane)

def update_supply_crates():
    for crate in supply_crates[:]:
        crate["phase"] = crate.get("phase", 0.0) + 0.10
        crate["vy"] = min(3.4, crate.get("vy", 0.0) + GRAVITY * 0.08)
        crate["x"] += crate.get("vx", 0.0)
        crate["y"] += crate["vy"]
        block_x = int((crate["x"] + render.TILE_SIZE / 2) // render.TILE_SIZE)
        block_y = int((crate["y"] + render.TILE_SIZE) // render.TILE_SIZE)
        if block_y >= WORLD_ROWS - 1 or int(get_block_at(block_x, block_y)) not in NON_SOLID_BLOCKS:
            chest_y = max(0, min(WORLD_ROWS - 1, block_y - 1))
            if int(get_block_at(block_x, chest_y)) in NON_SOLID_BLOCKS and len(chests) < MAX_PERSISTENT_CHESTS:
                set_block_at(block_x, chest_y, 45)
                chests[block_key(block_x, chest_y)] = crate.get("loot", create_airdrop_loot())
                play_sound("craft")
            else:
                for item in crate.get("loot", []):
                    drop_item_stack(item, crate["x"], crate["y"])
            supply_crates.remove(crate)

def update_sunbirds():
    for sunbird in sunbirds[:]:
        sunbird["phase"] = sunbird.get("phase", 0.0) + 0.18
        sunbird["x"] += sunbird.get("vx", 0.0)
        sunbird["y"] += math.sin(sunbird["phase"]) * 0.75
        if abs(sunbird["x"] - player_abs_px) > render.TILE_SIZE * 32:
            sunbirds.remove(sunbird)

def update_npcs():
    house_by_id = {s["id"]: s for s in structures}
    for npc in npcs[:]:
        npc["wave"] = npc.get("wave", 0.0) + 0.08
        structure = house_by_id.get(npc.get("house"))
        if structure and structure.get("queue"):
            npc["build_cd"] = npc.get("build_cd", 20) - 1
            if npc["build_cd"] <= 0:
                bx, by, bid = structure["queue"].pop(0)
                set_block_at(bx, by, bid)
                structure["built"] = structure.get("built", 0) + 1
                npc["x"] = bx * render.TILE_SIZE
                npc["y"] = (by - 1) * render.TILE_SIZE
                npc["build_cd"] = 12
                play_sound("place")
        else:
            npc["wander_cd"] = npc.get("wander_cd", 90) - 1
            if npc["wander_cd"] <= 0:
                base_speed = 0.55 if npc.get("job") in ("guard", "miner") else 0.4
                npc["vx"] = random.choice([-base_speed, -base_speed * 0.5, 0, base_speed * 0.5, base_speed])
                npc["wander_cd"] = random.randint(50, 180)
            elif npc.get("job") in ("merchant", "trader"):
                npc["vx"] = math.sin(npc["wave"] * 0.7) * 0.22
            elif npc.get("job") == "wanderer":
                npc["vx"] = npc.get("vx", 0.0) * 0.98 + math.sin(npc["wave"]) * 0.025
            else:
                npc["vx"] = npc.get("vx", 0.0) * 0.95
            new_x = npc["x"] + npc["vx"]
            if not check_collision(new_x, npc["y"]):
                npc["x"] = new_x
            else:
                npc["vx"] = -npc.get("vx", 0.0) * 0.5
            npc["vy"] = npc.get("vy", 0.0) + GRAVITY
            new_y = npc["y"] + npc["vy"]
            if not check_collision(npc["x"], new_y):
                npc["y"] = new_y
            else:
                npc["vy"] = 0
        if abs(npc["x"] - player_abs_px) > render.TILE_SIZE * 42 and not npc.get("house"):
            if npc.get("job") in ("merchant", "trader"):
                reposition_trade_npc_near_player(npc)
            else:
                npcs.remove(npc)

def check_collision(abs_px, py):
    left = int(abs_px + 6) // render.TILE_SIZE
    right = int(abs_px + render.TILE_SIZE - 6) // render.TILE_SIZE
    top = int(py + 2) // render.TILE_SIZE
    bottom = int(py + render.TILE_SIZE - 1) // render.TILE_SIZE
    
    for r in range(top, bottom + 1):
        for c in range(left, right + 1):
            if get_block_at(c, r) not in NON_SOLID_BLOCKS: 
                return True
    return False

def check_will_fall(abs_px, py):
    left = int(abs_px + 6) // render.TILE_SIZE
    right = int(abs_px + render.TILE_SIZE - 6) // render.TILE_SIZE
    bottom_next = int(py + render.TILE_SIZE) // render.TILE_SIZE 
    if get_block_at(left, bottom_next) in NON_SOLID_BLOCKS and get_block_at(right, bottom_next) in NON_SOLID_BLOCKS:
        return True
    return False

def save_game():
    cleanup_runtime_resources(force=True)
    compact_dirty_chunks()
    chunks_to_save = {idx: saved_chunks[idx] for idx in dirty_chunks if idx in saved_chunks}
    serializable_chunks = {str(k): v.astype(int).tolist() for k, v in chunks_to_save.items()}
    save_data = {
        "player_abs_px": player_abs_px, "player_py": player_py, "seed": WORLD_SEED,
        "hp": hp, "hunger": hunger, "player_level": player_level,
        "player_xp": player_xp, "money": money, "inventory": inventory,
        "equipped_armor": equipped_armor, "enchanted_item_ids": enchanted_item_ids,
        "crafting_grid": crafting_grid, "crafting_table_grid": crafting_table_grid,
        "furnace_slots": furnace_slots, "furnace_progress": furnace_progress,
        "cursor_item": cursor_item, "covered_blocks": covered_blocks,
        "planted_crops": planted_crops, "village_stats": village_stats,
        "world_time": world_time, "mobs": mobs, "animals": animals,
        "birds": [], "planes": [], "supply_planes": [],
        "supply_crates": [], "sunbirds": [],
        "npcs": npcs, "projectiles": [], "structures": structures,
        "chests": chests, "dropped_items": dropped_items,
        "chunks": serializable_chunks, "dirty_chunks": sorted(dirty_chunks),
        "save_version": 2
    }
    with open(SAVE_FILE, "w") as f: 
        json.dump(save_data, f)
    print("✅ 無限區塊存檔成功！")

def load_game():
    global active_chunks, saved_chunks, dirty_chunks, covered_blocks, player_abs_px, player_py, WORLD_SEED, hp, hunger, player_level, player_xp, money, inventory, equipped_armor, enchanted_item_ids, crafting_grid, crafting_table_grid, furnace_slots, furnace_progress, cursor_item, planted_crops, village_stats, world_time, mobs, animals, birds, planes, supply_planes, supply_crates, sunbirds, npcs, projectiles, structures, chests, dropped_items
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f: 
                save_data = json.load(f)
            player_abs_px, player_py = save_data["player_abs_px"], save_data["player_py"]
            WORLD_SEED = save_data["seed"]
            hp, hunger, inventory = save_data["hp"], save_data["hunger"], save_data["inventory"]
            player_level = save_data.get("player_level", player_level)
            player_xp = save_data.get("player_xp", player_xp)
            money = save_data.get("money", money)
            equipped_armor = save_data.get("equipped_armor", equipped_armor)
            enchanted_item_ids = save_data.get("enchanted_item_ids", enchanted_item_ids)
            crafting_grid = save_data.get("crafting_grid", crafting_grid)
            crafting_table_grid = save_data.get("crafting_table_grid", crafting_table_grid)
            furnace_slots = save_data.get("furnace_slots", furnace_slots)
            furnace_progress = save_data.get("furnace_progress", furnace_progress)
            cursor_item = save_data.get("cursor_item", cursor_item)
            planted_crops = save_data.get("planted_crops", planted_crops)
            village_stats = save_data.get("village_stats", village_stats)
            covered_blocks = save_data.get("covered_blocks", {})
            world_time = save_data.get("world_time", world_time)
            mobs = save_data.get("mobs", [])
            animals = save_data.get("animals", [])
            birds = save_data.get("birds", [])
            planes = save_data.get("planes", [])
            supply_planes = save_data.get("supply_planes", [])
            supply_crates = save_data.get("supply_crates", [])
            sunbirds = save_data.get("sunbirds", [])
            npcs = save_data.get("npcs", [])
            projectiles = save_data.get("projectiles", [])
            structures = save_data.get("structures", [])
            chests = save_data.get("chests", {})
            dropped_items = save_data.get("dropped_items", [])
            saved_chunks = {}
            dirty_chunks = set()
            for key, value in save_data.get("chunks", {}).items():
                chunk_idx = int(key)
                chunk = np.array(value, dtype=np.int8)
                if chunk.shape != (WORLD_ROWS, CHUNK_SIZE):
                    continue
                if chunk_matches_generated(chunk_idx, chunk):
                    continue
                saved_chunks[chunk_idx] = chunk
                dirty_chunks.add(chunk_idx)
            active_chunks = {}
            return True
        except: 
            return False
    return False

def empty_item():
    return {"id": 0, "count": 0}

def copy_item(item):
    copied = {"id": int(item["id"]), "count": int(item["count"])}
    if "durability" in item:
        copied["durability"] = int(item["durability"])
    return copied

def is_empty(item):
    return item["id"] == 0 or item["count"] <= 0

def normalize_item(item):
    if is_empty(item):
        item["id"], item["count"] = 0, 0
        item.pop("durability", None)

def get_max_durability(item_id):
    return ITEM_MAX_DURABILITY.get(int(item_id), 0)

def ensure_item_durability(item):
    max_durability = get_max_durability(item.get("id", 0))
    if max_durability and "durability" not in item:
        item["durability"] = max_durability

def damage_item(item, amount=1):
    ensure_item_durability(item)
    if "durability" not in item:
        return
    item["durability"] -= amount
    if item["durability"] <= 0:
        play_sound("break")
        clear_item(item)

def damage_selected_item(amount=1):
    damage_item(inventory[selected_slot], amount)

def can_stack(a, b):
    return not is_empty(a) and not is_empty(b) and a["id"] == b["id"] and get_max_durability(a["id"]) == 0

def add_to_inventory(item):
    remaining = copy_item(item)
    if is_empty(remaining):
        return empty_item()
    ensure_item_durability(remaining)

    for slot in inventory:
        if can_stack(slot, remaining) and slot["count"] < MAX_STACK:
            moved = min(MAX_STACK - slot["count"], remaining["count"])
            slot["count"] += moved
            remaining["count"] -= moved
            if remaining["count"] <= 0:
                return empty_item()

    for slot in inventory:
        if is_empty(slot):
            moved = min(MAX_STACK, remaining["count"])
            slot["id"], slot["count"] = remaining["id"], moved
            remaining["count"] -= moved
            if remaining["count"] <= 0:
                return empty_item()

    return remaining

def has_starter_gun():
    return any(slot["count"] > 0 and slot["id"] in GUN_STATS for slot in inventory)

def hotbar_indices():
    return range(HOTBAR_START, HOTBAR_START + HOTBAR_SIZE)

def hotbar_has_item(item_id):
    return any(inventory[i]["id"] == item_id and inventory[i]["count"] > 0 for i in hotbar_indices())

def move_item_to_hotbar(item_id, preferred_index):
    if hotbar_has_item(item_id):
        return True
    source_idx = None
    for idx, slot in enumerate(inventory):
        if slot["id"] == item_id and slot["count"] > 0:
            source_idx = idx
            break
    if source_idx is None:
        return False
    target_idx = preferred_index if is_empty(inventory[preferred_index]) else None
    if target_idx is None:
        for idx in hotbar_indices():
            if is_empty(inventory[idx]):
                target_idx = idx
                break
    if target_idx is None:
        return False
    inventory[source_idx], inventory[target_idx] = inventory[target_idx], inventory[source_idx]
    return True

def ensure_starter_kit():
    had_gun = has_starter_gun()
    if not had_gun:
        add_to_inventory({"id": 41, "count": 1})
    if not had_gun and count_item(40) < 24:
        add_to_inventory({"id": 40, "count": 24 - count_item(40)})
    move_item_to_hotbar(41, HOTBAR_START)
    move_item_to_hotbar(40, HOTBAR_START + 1)
    move_item_to_hotbar(1, HOTBAR_START + 2)

def inventory_has_room(item):
    room = 0
    for slot in inventory:
        if is_empty(slot):
            room += MAX_STACK
        elif slot["id"] == item["id"]:
            room += MAX_STACK - slot["count"]
    return room >= item["count"]

def return_item_to_inventory(item):
    remaining = add_to_inventory(item)
    item["id"], item["count"] = remaining["id"], remaining["count"]

def close_inventory():
    for slot in crafting_grid:
        return_item_to_inventory(slot)
    for slot in crafting_table_grid:
        return_item_to_inventory(slot)
    for slot in furnace_slots:
        return_item_to_inventory(slot)
    return_item_to_inventory(cursor_item)
    check_crafting_recipes()

def update_furnace():
    global furnace_progress
    input_slot, fuel_slot, output_slot = furnace_slots
    recipe = FURNACE_RECIPES.get(input_slot["id"])
    can_output = recipe and (is_empty(output_slot) or (output_slot["id"] == recipe["result"] and output_slot["count"] < MAX_STACK))
    if recipe and fuel_slot["id"] == 15 and fuel_slot["count"] > 0 and can_output:
        furnace_progress += 1
        if furnace_progress >= 180:
            input_slot["count"] -= 1
            fuel_slot["count"] -= 1
            normalize_item(input_slot)
            normalize_item(fuel_slot)
            if is_empty(output_slot):
                output_slot["id"], output_slot["count"] = recipe["result"], 1
            else:
                output_slot["count"] += 1
            furnace_progress = 0
            play_sound("craft")
    else:
        furnace_progress = max(0, furnace_progress - 2)

def handle_furnace_output_click(button, shift_pressed):
    output_slot = furnace_slots[2]
    if is_empty(output_slot):
        return
    if shift_pressed:
        return_item_to_inventory(output_slot)
        play_sound("click")
        return
    if button == 1 and (is_empty(cursor_item) or can_stack(cursor_item, output_slot)):
        if is_empty(cursor_item):
            cursor_item["id"], cursor_item["count"] = output_slot["id"], output_slot["count"]
            clear_item(output_slot)
        else:
            moved = min(MAX_STACK - cursor_item["count"], output_slot["count"])
            cursor_item["count"] += moved
            output_slot["count"] -= moved
            normalize_item(output_slot)
        play_sound("click")

def normalize_grid_shape(grid, width):
    height = len(grid) // width
    ids = [[grid[row * width + col]["id"] if grid[row * width + col]["count"] > 0 else 0 for col in range(width)] for row in range(height)]
    used_rows = [i for i, row in enumerate(ids) if any(row)]
    used_cols = [i for i in range(width) if any(ids[row][i] for row in range(height))]
    if not used_rows or not used_cols:
        return ()
    return tuple(tuple(ids[row][col] for col in used_cols) for row in used_rows)

def shapeless_key(grid):
    return tuple(sorted(slot["id"] for slot in grid if not is_empty(slot)))

def match_recipe(grid, width, shaped_recipes):
    shaped = shaped_recipes.get(normalize_grid_shape(grid, width))
    if shaped:
        return shaped
    return SHAPELESS_RECIPES.get(shapeless_key(grid), empty_item())

def check_crafting_recipes():
    result = match_recipe(crafting_grid, 2, SHAPED_RECIPES_2)
    crafting_output["id"], crafting_output["count"] = result["id"], result["count"]
    table_result = match_recipe(crafting_table_grid, 3, SHAPED_RECIPES_3)
    crafting_table_output["id"], crafting_table_output["count"] = table_result["id"], table_result["count"]

def consume_crafting_ingredients(grid):
    for slot in grid:
        if not is_empty(slot):
            slot["count"] -= 1
            normalize_item(slot)
    check_crafting_recipes()

def can_take_crafting_output(output):
    if is_empty(output):
        return False
    return is_empty(cursor_item) or (cursor_item["id"] == output["id"] and cursor_item["count"] + output["count"] <= MAX_STACK)

def handle_crafting_output_click(output, grid, button, shift_pressed):
    if is_empty(output):
        return

    if shift_pressed:
        crafted_any = False
        while not is_empty(output) and inventory_has_room(output):
            add_to_inventory(output)
            consume_crafting_ingredients(grid)
            crafted_any = True
        if crafted_any:
            play_sound("craft")
        return

    if button != 1 or not can_take_crafting_output(output):
        return

    if is_empty(cursor_item):
        cursor_item["id"], cursor_item["count"] = output["id"], output["count"]
        ensure_item_durability(cursor_item)
    else:
        cursor_item["count"] += output["count"]
    consume_crafting_ingredients(grid)
    play_sound("craft")

def handle_slot_click(container, index, button):
    slot = container[index]
    if button == 1:
        if is_empty(cursor_item) and not is_empty(slot):
            cursor_item.clear()
            cursor_item.update(copy_item(slot))
            clear_item(slot)
        elif not is_empty(cursor_item) and is_empty(slot):
            slot.clear()
            slot.update(copy_item(cursor_item))
            clear_item(cursor_item)
        elif can_stack(slot, cursor_item) and slot["count"] < MAX_STACK:
            moved = min(MAX_STACK - slot["count"], cursor_item["count"])
            slot["count"] += moved
            cursor_item["count"] -= moved
            normalize_item(cursor_item)
        elif not is_empty(cursor_item):
            old_slot = copy_item(slot)
            old_cursor = copy_item(cursor_item)
            slot.clear()
            slot.update(old_cursor)
            cursor_item.clear()
            cursor_item.update(old_slot)
    elif button == 3:
        if is_empty(cursor_item) and not is_empty(slot):
            take = (slot["count"] + 1) // 2
            cursor_item.clear()
            cursor_item.update(copy_item(slot))
            cursor_item["count"] = take
            slot["count"] -= take
            normalize_item(slot)
        elif not is_empty(cursor_item) and is_empty(slot):
            slot.clear()
            slot.update(copy_item(cursor_item))
            slot["count"] = 1
            cursor_item["count"] -= 1
            normalize_item(cursor_item)
        elif can_stack(slot, cursor_item) and slot["count"] < MAX_STACK:
            slot["count"] += 1
            cursor_item["count"] -= 1
            normalize_item(cursor_item)
        elif not is_empty(cursor_item):
            old_slot = copy_item(slot)
            old_cursor = copy_item(cursor_item)
            slot.clear()
            slot.update(old_cursor)
            cursor_item.clear()
            cursor_item.update(old_slot)

    check_crafting_recipes()
    if button in (1, 3):
        play_sound("click")

loaded_game = load_game()
if not loaded_game:
    player_abs_px, player_py = find_safe_player_spawn()
ensure_starter_kit()

check_crafting_recipes()

frame_count = 0
running = True

# --- 主迴圈 ---
while running:
    clock.tick(60)
    frame_count += 1
    world_time = (world_time + 1) % DAY_LENGTH_FRAMES
    sky_color = get_sky_color_for_time()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    player_block_center_x = int(player_abs_px + render.TILE_SIZE // 2) // render.TILE_SIZE
    in_water = get_block_at(player_block_center_x, int(player_py + render.TILE_SIZE // 2) // render.TILE_SIZE) == 7
    
    screen_pixel_start_x = int(player_abs_px - render.WIDTH // 2 + render.TILE_SIZE // 2)
    screen_pixel_start_y = int(player_py - render.HEIGHT // 2 + render.TILE_SIZE // 2)
    start_block_x = screen_pixel_start_x // render.TILE_SIZE
    start_block_y = screen_pixel_start_y // render.TILE_SIZE
    subpixel_offset_x = screen_pixel_start_x % render.TILE_SIZE
    subpixel_offset_y = screen_pixel_start_y % render.TILE_SIZE

    visible_world = np.zeros((render.ROWS + 2, render.COLS + 2), dtype=np.int8)
    for y in range(render.ROWS + 2):
        for x in range(render.COLS + 2):
            visible_world[y, x] = get_block_at(start_block_x + x, start_block_y + y)

    target_abs_block_x = start_block_x + (mouse_x + subpixel_offset_x) // render.TILE_SIZE
    target_block_y = start_block_y + (mouse_y + subpixel_offset_y) // render.TILE_SIZE
    target_block = int(get_block_at(target_abs_block_x, target_block_y))
    target_data = [current_state == render.STATE_GAME, target_abs_block_x - start_block_x, target_block_y - start_block_y]

    if current_state == render.STATE_GAME:
        if is_night() and frame_count - last_mob_spawn_frame > MOB_SPAWN_INTERVAL:
            spawn_monster()
            last_mob_spawn_frame = frame_count
        if frame_count - last_cave_mob_spawn_frame > CAVE_MOB_SPAWN_INTERVAL:
            spawn_cave_monster()
            last_cave_mob_spawn_frame = frame_count
        if player_level >= BOSS_UNLOCK_LEVEL and frame_count - last_boss_spawn_frame > BOSS_SPAWN_INTERVAL:
            spawn_boss()
            last_boss_spawn_frame = frame_count
        if not is_night() and frame_count - last_animal_spawn_frame > ANIMAL_SPAWN_INTERVAL:
            spawn_animal()
            last_animal_spawn_frame = frame_count
        if frame_count - last_bird_spawn_frame > BIRD_SPAWN_INTERVAL:
            spawn_bird()
            last_bird_spawn_frame = frame_count
        if frame_count - last_plane_spawn_frame > PLANE_SPAWN_INTERVAL:
            spawn_plane()
            last_plane_spawn_frame = frame_count
        if frame_count - last_supply_plane_spawn_frame > SUPPLY_PLANE_SPAWN_INTERVAL:
            spawn_supply_plane()
            last_supply_plane_spawn_frame = frame_count
        if frame_count - last_sunbird_spawn_frame > SUNBIRD_SPAWN_INTERVAL:
            spawn_sunbird()
            last_sunbird_spawn_frame = frame_count
        if frame_count - last_house_spawn_frame > HOUSE_SPAWN_INTERVAL:
            spawn_house_with_npc()
            last_house_spawn_frame = frame_count
        if frame_count - last_wander_npc_spawn_frame > WANDER_NPC_SPAWN_INTERVAL:
            spawn_wandering_npc()
            last_wander_npc_spawn_frame = frame_count

    is_sneaking = False
    is_sprinting = False
    is_swimming = False

    # 1. 事件攔截
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
        elif event.type == pygame.MOUSEWHEEL and current_state == render.STATE_GAME:
            selected_slot = HOTBAR_START + ((selected_slot - HOTBAR_START - event.y) % HOTBAR_SIZE)
            play_sound("click")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if current_state in (render.STATE_INVENTORY, render.STATE_CRAFTING_TABLE, render.STATE_FURNACE, render.STATE_CHEST):
                    close_inventory()
                    current_state = render.STATE_GAME
                    play_sound("close")
                elif current_state == render.STATE_TRADER:
                    current_state = render.STATE_GAME
                    trader_message = ""
                    play_sound("close")
                else:
                    current_state = render.STATE_MENU if current_state == render.STATE_GAME else render.STATE_GAME
                    play_sound("open" if current_state == render.STATE_MENU else "close")
            elif event.key == pygame.K_e: 
                if current_state == render.STATE_GAME:
                    current_state = render.STATE_INVENTORY
                    play_sound("open")
                elif current_state in (render.STATE_INVENTORY, render.STATE_CRAFTING_TABLE, render.STATE_FURNACE, render.STATE_CHEST):
                    close_inventory()
                    current_state = render.STATE_GAME
                    play_sound("close")
                elif current_state == render.STATE_TRADER:
                    current_state = render.STATE_GAME
                    trader_message = ""
                    play_sound("close")
            elif pygame.K_1 <= event.key <= pygame.K_9: 
                selected_slot = HOTBAR_START + (event.key - pygame.K_1)
            elif event.key == pygame.K_q and current_state == render.STATE_GAME:
                drop_selected_item()
            elif event.key == pygame.K_w:
                if is_grounded: 
                    vel_y = JUMP_FORCE
                    is_grounded = False
                    play_sound("jump")
                elif in_water: 
                    vel_y = JUMP_FORCE * 0.7
                    play_sound("swim")

        elif event.type == pygame.MOUSEBUTTONDOWN and current_state == render.STATE_MENU:
            action = render.get_menu_action(mouse_x, mouse_y)
            if action == "back":
                current_state = render.STATE_GAME
                play_sound("click")
            elif action == "save_quit":
                running = False
                play_sound("click")

        elif event.type == pygame.MOUSEBUTTONDOWN and current_state == render.STATE_INVENTORY:
            shift_pressed = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)
            if render.rect_contains(render.get_crafting_output_rect(), mouse_x, mouse_y):
                handle_crafting_output_click(crafting_output, crafting_grid, event.button, shift_pressed)
            else:
                slot_idx = render.get_inventory_slot_at(mouse_x, mouse_y)
                craft_idx = render.get_crafting_slot_at(mouse_x, mouse_y)
                if slot_idx is not None:
                    handle_slot_click(inventory, slot_idx, event.button)
                elif craft_idx is not None:
                    handle_slot_click(crafting_grid, craft_idx, event.button)

        elif event.type == pygame.MOUSEBUTTONDOWN and current_state == render.STATE_CRAFTING_TABLE:
            shift_pressed = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)
            if render.rect_contains(render.get_table_output_rect(), mouse_x, mouse_y):
                handle_crafting_output_click(crafting_table_output, crafting_table_grid, event.button, shift_pressed)
            else:
                slot_idx = render.get_inventory_slot_at(mouse_x, mouse_y)
                table_idx = render.get_table_slot_at(mouse_x, mouse_y)
                if slot_idx is not None:
                    handle_slot_click(inventory, slot_idx, event.button)
                elif table_idx is not None:
                    handle_slot_click(crafting_table_grid, table_idx, event.button)

        elif event.type == pygame.MOUSEBUTTONDOWN and current_state == render.STATE_FURNACE:
            shift_pressed = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)
            furnace_idx = render.get_furnace_slot_at(mouse_x, mouse_y)
            if furnace_idx == 2:
                handle_furnace_output_click(event.button, shift_pressed)
            elif furnace_idx is not None:
                handle_slot_click(furnace_slots, furnace_idx, event.button)
            else:
                slot_idx = render.get_inventory_slot_at(mouse_x, mouse_y)
                if slot_idx is not None:
                    handle_slot_click(inventory, slot_idx, event.button)

        elif event.type == pygame.MOUSEBUTTONDOWN and current_state == render.STATE_CHEST:
            chest_idx = render.get_chest_slot_at(mouse_x, mouse_y)
            if chest_idx is not None:
                handle_slot_click(open_chest_slots, chest_idx, event.button)
            else:
                slot_idx = render.get_inventory_slot_at(mouse_x, mouse_y)
                if slot_idx is not None:
                    handle_slot_click(inventory, slot_idx, event.button)

        elif event.type == pygame.MOUSEBUTTONDOWN and current_state == render.STATE_TRADER:
            if event.button == 1:
                trade_idx = render.get_trader_trade_at(mouse_x, mouse_y, len(TRADER_TRADES))
                buy_trade(trade_idx)

        elif event.type == pygame.MOUSEBUTTONDOWN and current_state == render.STATE_GAME:
            if event.button == 1:
                handled_attack = False
                if get_selected_item_id() in GUN_STATS:
                    handled_attack = fire_gun(screen_pixel_start_x + mouse_x, screen_pixel_start_y + mouse_y)
                target_mob_idx = find_mob_at_world(screen_pixel_start_x + mouse_x, screen_pixel_start_y + mouse_y)
                if not handled_attack and target_mob_idx is not None and can_attack_mob(mobs[target_mob_idx]):
                    damage_mob(target_mob_idx, get_attack_damage(), player_abs_px + render.TILE_SIZE / 2, player_py + render.TILE_SIZE / 2, 3.0)
                    if get_max_durability(get_selected_item_id()):
                        damage_selected_item(1)
                    handled_attack = True
                else:
                    target_animal_idx = find_animal_at_world(screen_pixel_start_x + mouse_x, screen_pixel_start_y + mouse_y)
                    if target_animal_idx is not None and can_attack_animal(animals[target_animal_idx]):
                        damage_animal(target_animal_idx, get_attack_damage(), player_abs_px + render.TILE_SIZE / 2, player_py + render.TILE_SIZE / 2)
                        if get_max_durability(get_selected_item_id()):
                            damage_selected_item(1)
                        handled_attack = True
                if not handled_attack and can_mine_block(target_abs_block_x, target_block_y):
                    is_mining = True
                    mine_target_abs_x, mine_target_abs_y = target_abs_block_x, target_block_y
                    mining_progress = 0
                    mining_required_time = get_current_mine_time(target_block)
                    play_sound("click")
            elif event.button == 3:
                target_npc_idx = find_npc_at_world(screen_pixel_start_x + mouse_x, screen_pixel_start_y + mouse_y)
                if target_npc_idx is not None and can_trade_with_npc(npcs[target_npc_idx]):
                    current_state = render.STATE_TRADER
                    trader_message = "Spend money, XP, or minerals for gear."
                    play_sound("open")
                    continue
                if target_block == 45 and open_chest_storage(target_abs_block_x, target_block_y):
                    continue
                if target_block == 4:
                    current_state = render.STATE_CRAFTING_TABLE
                    check_crafting_recipes()
                    play_sound("open")
                    continue
                if target_block == 52:
                    current_state = render.STATE_FURNACE
                    play_sound("open")
                    continue
                if target_block == 54:
                    use_stonecutter_block()
                    continue
                if target_block == 55:
                    use_lever_block(target_abs_block_x, target_block_y)
                    continue
                if target_block == 62:
                    use_enchanting_table()
                    continue
                if target_block == 63:
                    use_jukebox_block()
                    continue

                item = inventory[selected_slot]
                if harvest_crop(target_abs_block_x, target_block_y):
                    continue
                if use_hoe_on_block(target_abs_block_x, target_block_y):
                    continue
                if plant_seed(target_abs_block_x, target_block_y):
                    continue
                if eat_selected_food():
                    continue
                if equip_selected_armor():
                    continue
                if item["id"] == 46:
                    ground_y = target_block_y
                    while ground_y < WORLD_ROWS - 1 and get_block_at(target_abs_block_x, ground_y) in NON_SOLID_BLOCKS:
                        ground_y += 1
                    if start_house_at(target_abs_block_x - 3, ground_y):
                        item["count"] -= 1
                        normalize_item(item)
                        play_sound("craft")
                    continue
                if item["id"] in PLACEABLE_BLOCKS and item["count"] > 0 and target_block in NON_SOLID_BLOCKS:
                    key = block_key(target_abs_block_x, target_block_y)
                    previous_covered = covered_blocks.get(key)
                    set_block_at(target_abs_block_x, target_block_y, item["id"])
                    if check_collision(player_abs_px, player_py):
                        set_block_at(target_abs_block_x, target_block_y, target_block)
                        if previous_covered is None:
                            covered_blocks.pop(key, None)
                        else:
                            covered_blocks[key] = previous_covered
                    else:
                        if target_block != 0:
                            covered_blocks[key] = target_block
                        else:
                            covered_blocks.pop(key, None)
                        item["count"] -= 1
                        normalize_item(item)
                        play_sound("place")
                    
        elif event.type == pygame.MOUSEBUTTONUP: 
            is_mining = False

    # 2. 運動與物理
    if current_state == render.STATE_GAME:
        keys = pygame.key.get_pressed()
        is_sneaking = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        is_sprinting = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
        is_swimming = in_water and is_sprinting
        
        current_max_speed = SNEAK_SPEED if is_sneaking else (SPRINT_SPEED if is_sprinting and hunger > 0 else WALK_SPEED)
        if in_water: 
            current_max_speed *= 0.85 if is_swimming else 0.6
        
        # --- 修正後的平滑排版 ---
        if keys[pygame.K_a]: 
            vel_x = max(-current_max_speed, vel_x - ACCELERATION)
            facing_right = False
        elif keys[pygame.K_d]: 
            vel_x = min(current_max_speed, vel_x + ACCELERATION)
            facing_right = True
        else: 
            vel_x = (vel_x * FRICTION if is_grounded else vel_x * AIR_RESISTANCE)
            if abs(vel_x) < 0.1: 
                vel_x = 0

        if in_water and is_swimming:
            if keys[pygame.K_w]:
                vel_y = max(vel_y - 0.35, -3.5)
            if keys[pygame.K_s]:
                vel_y = min(vel_y + 0.25, 3.0)
            
        new_abs_px = player_abs_px + vel_x
        if not check_collision(new_abs_px, player_py):
            if is_grounded and is_sneaking and check_will_fall(new_abs_px, player_py): 
                vel_x = 0
                new_abs_px = player_abs_px
            player_abs_px = new_abs_px
        else: 
            vel_x = 0
            
        vel_y += GRAVITY * 0.12 if is_swimming else (GRAVITY * 0.3 if in_water else GRAVITY)
        new_py = player_py + vel_y
        
        if not check_collision(player_abs_px, new_py): 
            player_py = new_py
            is_grounded = False
        else:
            if vel_y > 0: 
                is_grounded = True
            vel_y = 0

        if is_mining:
            if not can_mine_block(mine_target_abs_x, mine_target_abs_y):
                is_mining = False
                mining_progress = 0
            else:
                mining_progress += 1
            if is_mining and mining_progress >= mining_required_time:
                bid = int(get_block_at(mine_target_abs_x, mine_target_abs_y))
                is_mining = False
                drop_id = BLOCK_DROPS.get(bid, bid)
                if bid not in (0, 7):
                    restore_block = get_break_replacement_block(mine_target_abs_x, mine_target_abs_y)
                    set_block_at(mine_target_abs_x, mine_target_abs_y, restore_block)
                    drop_x = mine_target_abs_x * render.TILE_SIZE + render.TILE_SIZE / 2
                    drop_y = mine_target_abs_y * render.TILE_SIZE + render.TILE_SIZE / 2
                    drop_item_stack({"id": drop_id, "count": 1}, drop_x, drop_y)
                    if bid == 45:
                        drop_chest_contents(mine_target_abs_x, mine_target_abs_y)
                    if bid in (1, 9) and random.random() < 0.35:
                        drop_item_stack({"id": 75, "count": 1}, drop_x, drop_y)
                    if bid == 78:
                        crop_key = block_key(mine_target_abs_x, mine_target_abs_y)
                        crop = planted_crops.pop(crop_key, {"stage": 3})
                        if crop.get("stage", 0) >= 3:
                            drop_item_stack({"id": 75, "count": random.randint(0, 2)}, drop_x, drop_y)
                    if get_max_durability(get_selected_item_id()):
                        damage_selected_item(1)
                    play_sound("break")

        update_hunger(is_sprinting and abs(vel_x) > 1.2)
        update_crops()
        update_village()
        update_mobs()
        update_animals()
        update_birds()
        update_planes()
        update_supply_planes()
        update_supply_crates()
        update_sunbirds()
        update_npcs()
        update_projectiles()
        update_dropped_items()
        update_particles()
        handle_player_death()

        if is_grounded and abs(vel_x) > 0.6 and frame_count - last_step_frame > 18:
            play_sound("step")
            last_step_frame = frame_count
        if is_swimming and (abs(vel_x) > 0.4 or abs(vel_y) > 0.4) and frame_count - last_swim_frame > 20:
            play_sound("swim")
            last_swim_frame = frame_count

        cleanup_runtime_resources()

    # 3. 轉發給 OpenCV 渲染
    p_data = [player_abs_px, player_py, vel_x if current_state == render.STATE_GAME else 0, is_grounded, facing_right, is_swimming]
    m_data = [is_mining, mine_target_abs_x - start_block_x, mine_target_abs_y - start_block_y, mining_progress, mining_required_time]
    
    final_canvas = render.draw_game_scene(sky_color, visible_world, p_data, m_data, particles, frame_count, subpixel_offset_x, subpixel_offset_y, target_data, mobs, animals, birds, dropped_items, planes, sunbirds, npcs, projectiles, supply_planes, supply_crates)
    render.draw_hud(final_canvas, hp, hunger, inventory, selected_slot, player_level, player_xp, xp_to_next_level(player_level), money)
    player_block_y = int(player_py // render.TILE_SIZE)
    render.draw_minimap(final_canvas, visible_world, player_block_center_x, player_block_y, mobs, animals, npcs, village_stats, display_world_y(player_block_y))
    cv2.putText(final_canvas, ("Night" if is_night() else "Day") + f" {world_time // 1000:02d}", (20, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
    held_item = inventory[selected_slot]
    if held_item["id"] != 0:
        held_name = ITEM_NAMES.get(held_item["id"], f"Item {held_item['id']}")
        cv2.putText(final_canvas, held_name, (render.WIDTH // 2 - 95, render.HEIGHT - 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 210), 1)
        if held_item["id"] in GUN_STATS:
            cv2.putText(final_canvas, f"Ammo {count_item(40)}", (render.WIDTH // 2 + 35, render.HEIGHT - 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 240, 255), 1)
    if mobs:
        nearest = min(math.hypot(mob["x"] - player_abs_px, mob["y"] - player_py) for mob in mobs)
        if nearest < render.TILE_SIZE * HOSTILE_AGGRO_BLOCKS:
            cv2.putText(final_canvas, "Danger nearby", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (80, 80, 255), 2)
    
    if is_swimming:
        cv2.putText(final_canvas, "SWIMMING!", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 230, 255), 2)
    elif is_sprinting: 
        cv2.putText(final_canvas, "INFINITE SPRINT!", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2)
    elif is_sneaking: 
        cv2.putText(final_canvas, "INFINITE SNEAK...", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 255), 2)
    
    if current_state == render.STATE_MENU: 
        final_canvas = render.draw_minecraft_menu(final_canvas, mouse_x, mouse_y)
    elif current_state == render.STATE_INVENTORY: 
        final_canvas = render.draw_inventory_screen(final_canvas, inventory, crafting_grid, crafting_output, mouse_x, mouse_y, cursor_item, ITEM_NAMES, TOOL_SPEEDS, WEAPON_DAMAGE, PLACEABLE_BLOCKS)
    elif current_state == render.STATE_CRAFTING_TABLE:
        final_canvas = render.draw_crafting_table_screen(final_canvas, inventory, crafting_table_grid, crafting_table_output, mouse_x, mouse_y, cursor_item, ITEM_NAMES, TOOL_SPEEDS, WEAPON_DAMAGE, PLACEABLE_BLOCKS)
    elif current_state == render.STATE_TRADER:
        final_canvas = render.draw_trader_screen(final_canvas, get_trade_view(), mouse_x, mouse_y, ITEM_NAMES, player_level, player_xp, xp_to_next_level(player_level), money, trader_message)
    elif current_state == render.STATE_FURNACE:
        update_furnace()
        final_canvas = render.draw_furnace_screen(final_canvas, inventory, furnace_slots, furnace_progress, mouse_x, mouse_y, cursor_item, ITEM_NAMES, TOOL_SPEEDS, WEAPON_DAMAGE, PLACEABLE_BLOCKS)
    elif current_state == render.STATE_CHEST:
        final_canvas = render.draw_chest_screen(final_canvas, inventory, open_chest_slots, mouse_x, mouse_y, cursor_item, ITEM_NAMES, TOOL_SPEEDS, WEAPON_DAMAGE, PLACEABLE_BLOCKS)

    # 4. 刷入 Pygame 視窗
    rgb_canvas = cv2.cvtColor(final_canvas, cv2.COLOR_BGR2RGB)
    pygame.surfarray.blit_array(screen, np.transpose(rgb_canvas, (1, 0, 2)))
    pygame.display.flip()

close_inventory()
save_game()
pygame.quit()

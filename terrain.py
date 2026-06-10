# terrain.py
import numpy as np
import ctypes
import os
import platform
import math

system = platform.system()
lib_name = "libterrain.dylib" if system == "Darwin" else "libterrain.dll" if system == "Windows" else "libterrain.so"

try:
    _terrain_engine = ctypes.CDLL(os.path.join(os.path.dirname(__file__), lib_name))
    _terrain_engine.generate_chunk_c.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    _terrain_engine.generate_chunk_c.restype = None
    C_ENGINE_AVAILABLE = True
    print("🚀 成功掛載 C 語言無限區塊創世引擎！")
except Exception as e:
    print(f"⚠️ 無法載入 C 語言引擎: {e}，請確認是否成功編譯庫。")
    C_ENGINE_AVAILABLE = False

def generate_chunk(rows, chunk_cols, offset_x, seed):
    """驅動 C 引擎生成單個指定偏移量的區塊"""
    chunk = np.zeros((rows, chunk_cols), dtype=np.int8)
    if C_ENGINE_AVAILABLE:
        chunk_ptr = chunk.ctypes.data_as(ctypes.c_char_p)
        _terrain_engine.generate_chunk_c(chunk_ptr, rows, chunk_cols, offset_x, seed)
    else:
        generate_python_biome_chunk(chunk, rows, chunk_cols, offset_x, seed)
    add_caves_and_ores(chunk, rows, chunk_cols, offset_x, seed)
    return chunk

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

def octave_noise_1d(x, seed, base_freq, base_amp, octaves):
    value = 0.0
    amp = base_amp
    freq = base_freq
    max_amp = 0.0
    for octave in range(octaves):
        value += terrain_noise_1d(x * freq, seed + octave * 31) * amp
        max_amp += amp
        amp *= 0.5
        freq *= 2.0
    return 0.0 if max_amp == 0 else value / max_amp

def get_column_biome(abs_block_x, seed):
    continental = octave_noise_1d(abs_block_x + seed * 310, seed + 17, 0.0065, 1.0, 3)
    temperature = octave_noise_1d(abs_block_x + seed * 200, seed + 1, 0.010, 1.0, 3)
    moisture = octave_noise_1d(abs_block_x - seed * 150, seed + 29, 0.012, 1.0, 3)
    if continental < -0.42:
        return "deep_ocean"
    if continental < -0.22:
        return "ocean"
    if continental < -0.12:
        return "beach"
    if temperature > 0.05 and moisture < -0.08:
        return "desert"
    if temperature > 0.25 and moisture > 0.12:
        return "jungle"
    if moisture > -0.05:
        return "forest"
    return "plains"

def generate_python_biome_chunk(chunk, rows, chunk_cols, offset_x, seed):
    base_height = rows // 2
    sea_level = base_height + 4
    for local_x in range(chunk_cols):
        absolute_x = offset_x + local_x
        biome = get_column_biome(absolute_x, seed)
        elevation = octave_noise_1d(absolute_x + seed * 100, seed, 0.035, 6.0, 4)
        surface_y = base_height + int(elevation * 9.0)
        top_block, mid_block = 1, 2

        if biome == "deep_ocean":
            surface_y = sea_level + 10 + int(elevation * 3.0)
            top_block, mid_block = 6, 6
        elif biome == "ocean":
            surface_y = sea_level + 4 + int(elevation * 4.0)
            top_block, mid_block = 6, 6
        elif biome == "beach":
            surface_y = sea_level - 1 + int(elevation * 2.0)
            top_block, mid_block = 6, 6
        elif biome == "desert":
            surface_y += 1
            top_block, mid_block = 6, 6
        elif biome == "jungle":
            surface_y -= 2
        elif biome == "forest":
            surface_y -= 1

        surface_y = max(2, min(rows - 8, surface_y))
        chunk[surface_y, local_x] = top_block
        chunk[surface_y + 1:min(surface_y + 4, rows), local_x] = mid_block
        chunk[min(surface_y + 4, rows):rows, local_x] = 3

        if biome in ("deep_ocean", "ocean"):
            for y in range(surface_y - 1, sea_level - 1, -1):
                if y > 0:
                    chunk[y, local_x] = 7

        if biome not in ("deep_ocean", "ocean", "beach", "desert") and chunk[surface_y, local_x] == 1:
            tree_roll = cave_noise(absolute_x, surface_y, seed)
            threshold = 0.72 if biome == "jungle" else (0.82 if biome == "forest" else 0.96)
            if tree_roll > threshold:
                tree_height = 7 + int(cave_noise(absolute_x, 1, seed) > 0.5) * 2 if biome == "jungle" else (5 if biome == "forest" else 4)
                for ty in range(1, tree_height + 1):
                    if surface_y - ty >= 0:
                        chunk[surface_y - ty, local_x] = 8
                leaf_y = surface_y - tree_height
                if leaf_y >= 2:
                    leaf_radius = 3 if biome == "jungle" else 2
                    for ly in range(leaf_y - 2, leaf_y + 2):
                        if ly < 0 or ly >= rows:
                            continue
                        for lx in range(local_x - leaf_radius, local_x + leaf_radius + 1):
                            if 0 <= lx < chunk_cols and chunk[ly, lx] == 0:
                                chunk[ly, lx] = 9

def cave_noise(x, y, seed):
    n = x * 734287 + y * 912271 + seed * 1361
    n = (n ^ (n >> 13)) * 1274126177
    return (n & 0xFFFFFF) / float(0xFFFFFF)

def smooth_cave_value(x, y, seed):
    total = 0.0
    weight = 0.0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            w = 2.0 if dx == 0 and dy == 0 else 1.0
            total += cave_noise((x + dx) // 3, (y + dy) // 3, seed) * w
            weight += w
    return total / weight

def add_caves_and_ores(chunk, rows, chunk_cols, offset_x, seed):
    for local_x in range(chunk_cols):
        absolute_x = offset_x + local_x
        for y in range(rows):
            block = int(chunk[y, local_x])
            if block == 0 or y < rows // 2 + 3:
                continue

            depth_ratio = y / max(1, rows - 1)
            cave_a = smooth_cave_value(absolute_x, y, seed)
            cave_b = smooth_cave_value(absolute_x + seed, y * 2, seed + 99)
            cave_threshold = 0.76 if depth_ratio < 0.76 else 0.80
            pocket_threshold = 0.61 if depth_ratio < 0.82 else 0.66
            if cave_a > cave_threshold and cave_b > pocket_threshold and cave_noise(absolute_x, y, seed + 313) > 0.48:
                chunk[y, local_x] = 0
                continue

            ore_roll = cave_noise(absolute_x, y, seed + 777)
            deep_roll = cave_noise(absolute_x, y, seed + 444)
            if block in (3, 29) and y > rows * 0.86 and deep_roll > 0.58:
                chunk[y, local_x] = 66
                block = 66
            elif block in (3, 29) and y > rows * 0.76 and deep_roll > 0.30:
                chunk[y, local_x] = 74
                block = 74
            elif block == 3 and y > rows * 0.62 and deep_roll > 0.28:
                chunk[y, local_x] = 72
                block = 72
            elif block == 3 and y > rows * 0.54 and deep_roll > 0.84:
                chunk[y, local_x] = 29
                block = 29

            crystal_bonus = 0.003 if depth_ratio > 0.75 else 0.0
            diamond_bonus = 0.004 if depth_ratio > 0.72 else 0.0
            gold_bonus = 0.004 if depth_ratio > 0.62 else 0.0
            iron_bonus = 0.006 if depth_ratio > 0.52 else 0.0
            coal_bonus = 0.010 if depth_ratio > 0.50 else 0.0

            if block in (3, 29, 72, 74, 66) and ore_roll > 0.993 - crystal_bonus:
                chunk[y, local_x] = 73
            elif block in (3, 29, 72, 74, 66) and ore_roll > 0.987 - diamond_bonus:
                chunk[y, local_x] = 23
            elif block in (3, 29, 72, 74, 66) and ore_roll > 0.972 - gold_bonus:
                chunk[y, local_x] = 34
            elif block in (3, 29, 72, 74, 66) and ore_roll > 0.956 - iron_bonus:
                chunk[y, local_x] = 17
            elif block in (3, 29, 72, 74, 66) and ore_roll > 0.928 - coal_bonus:
                chunk[y, local_x] = 15

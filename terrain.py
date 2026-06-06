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
        base_height = rows // 2
        for local_x in range(chunk_cols):
            absolute_x = offset_x + local_x
            surface_y = base_height + int(math.sin((absolute_x + seed) * 0.09) * 4)
            surface_y = max(2, min(rows - 3, surface_y))
            top_block = 6 if math.sin((absolute_x + seed) * 0.025) < -0.35 else 1
            mid_block = 6 if top_block == 6 else 2
            chunk[surface_y, local_x] = top_block
            chunk[surface_y + 1:min(surface_y + 4, rows), local_x] = mid_block
            chunk[min(surface_y + 4, rows):rows, local_x] = 3
    add_caves_and_ores(chunk, rows, chunk_cols, offset_x, seed)
    return chunk

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

            cave_a = smooth_cave_value(absolute_x, y, seed)
            cave_b = smooth_cave_value(absolute_x + seed, y * 2, seed + 99)
            if cave_a > 0.62 and cave_b > 0.48:
                chunk[y, local_x] = 0
                continue

            ore_roll = cave_noise(absolute_x, y, seed + 777)
            if block == 3 and ore_roll > 0.985:
                chunk[y, local_x] = 23
            elif block == 3 and ore_roll > 0.970:
                chunk[y, local_x] = 34
            elif block == 3 and ore_roll > 0.955:
                chunk[y, local_x] = 17
            elif block == 3 and ore_roll > 0.925:
                chunk[y, local_x] = 15

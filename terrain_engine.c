// terrain_engine.c
#include <stdlib.h>
#include <math.h>

float simple_noise(int x, int seed) {
    int n = x + seed * 57;
    n = (n << 13) ^ n;
    return (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0);
}

float smooth_interpolate(float a, float b, float x) {
    float ft = x * 3.1415927;
    float f = (1 - cos(ft)) * 0.5;
    return  a * (1 - f) + b * f;
}

float generate_noise(float x, int seed) {
    // 使用 floor 取整，完美支援負數座標，這是無限世界的關鍵
    int integer_X = (int)floor(x); 
    float fractional_X = x - integer_X;
    float v1 = simple_noise(integer_X, seed);
    float v2 = simple_noise(integer_X + 1, seed);
    return smooth_interpolate(v1, v2, fractional_X);
}

float random_chance(int x, int y, int seed) {
    int n = x * 374761393 + y * 668265263 + seed;
    n = (n ^ (n >> 13)) * 1274126177;
    return (float)(n & 0x0FFFFFFF) / (float)0x0FFFFFFF;
}

// 核心 API：每次只生成一個寬度為 chunk_cols 的獨立區塊
void generate_chunk_c(char* chunk_ptr, int rows, int chunk_cols, int offset_x, int seed) {
    int base_height = rows / 2;

    for (int i = 0; i < rows * chunk_cols; ++i) {
        chunk_ptr[i] = 0; 
    }

    for (int local_x = 0; local_x < chunk_cols; ++local_x) {
        // 換算成絕對世界座標
        int absolute_x = offset_x + local_x; 

        // 1. 地形高低
        float elevation = 0;
        float freq = 0.05f, amp = 6.0f, max_amp = 0;
        for(int o = 0; o < 3; o++) { 
            elevation += generate_noise((absolute_x + seed * 100) * freq, seed) * amp;
            max_amp += amp; amp *= 0.5f; freq *= 2.0f;
        }
        elevation /= max_amp;

        // 2. 生態系溫度
        float temperature = generate_noise((absolute_x + seed * 200) * 0.015f, seed + 1);
        
        int surface_y = base_height + (int)(elevation * 8.0f);
        int block_top = 1; 
        int block_mid = 2; 
        int is_ocean = 0, is_desert = 0, is_jungle = 0;

        if (temperature < -0.2f) {
            is_ocean = 1; surface_y += 6; block_top = 6; block_mid = 6;
        } else if (temperature < 0.1f) {
            is_desert = 1; block_top = 6; block_mid = 6;
        } else if (temperature > 0.4f) {
            is_jungle = 1; surface_y -= 2; block_top = 1; block_mid = 2;
        }

        if (surface_y < 2) surface_y = 2;
        if (surface_y > rows - 3) surface_y = rows - 3;

        // 寫入區塊記憶體
        chunk_ptr[surface_y * chunk_cols + local_x] = block_top; 
        for (int y = surface_y + 1; y < surface_y + 4 && y < rows; ++y) {
            chunk_ptr[y * chunk_cols + local_x] = block_mid; 
        }
        for (int y = surface_y + 4; y < rows; ++y) {
            chunk_ptr[y * chunk_cols + local_x] = 3; 
        }

        // 海洋注水
        int sea_level = base_height + 4;
        if (is_ocean) {
            for (int y = surface_y - 1; y >= sea_level; --y) {
                if (y > 0) chunk_ptr[y * chunk_cols + local_x] = 7; 
            }
        }

        // 樹木隨機生成
        if (!is_ocean && !is_desert && chunk_ptr[surface_y * chunk_cols + local_x] == 1) {
            float tree_chance = random_chance(absolute_x, surface_y, seed);
            if ((!is_jungle && tree_chance > 0.96f) || (is_jungle && tree_chance > 0.88f)) {
                int tree_height = is_jungle ? (random_chance(absolute_x, 1, seed) > 0.5f ? 7 : 9) : 4; 
                for (int ty = 1; ty <= tree_height; ++ty) {
                    if (surface_y - ty >= 0) chunk_ptr[(surface_y - ty) * chunk_cols + local_x] = 8;
                }
                int leaf_y = surface_y - tree_height;
                if (leaf_y >= 2) {
                    for (int ly = leaf_y - 2; ly <= leaf_y; ++ly) {
                        for (int lx = local_x - 2; lx <= local_x + 2; ++lx) {
                            if (lx >= 0 && lx < chunk_cols && chunk_ptr[ly * chunk_cols + lx] == 0) {
                                if (is_jungle || random_chance(absolute_x + lx - local_x, ly, seed) > 0.3f) {
                                    chunk_ptr[ly * chunk_cols + lx] = 9; 
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
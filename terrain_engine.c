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

float octave_noise_1d(float x, int seed, float base_freq, float base_amp, int octaves) {
    float value = 0.0f;
    float amp = base_amp;
    float freq = base_freq;
    float max_amp = 0.0f;
    for (int o = 0; o < octaves; ++o) {
        value += generate_noise(x * freq, seed + o * 31) * amp;
        max_amp += amp;
        amp *= 0.5f;
        freq *= 2.0f;
    }
    return max_amp == 0.0f ? 0.0f : value / max_amp;
}

// 核心 API：每次只生成一個寬度為 chunk_cols 的獨立區塊
void generate_chunk_c(char* chunk_ptr, int rows, int chunk_cols, int offset_x, int seed) {
    int base_height = rows / 2;
    int sea_level = base_height + 4;

    for (int i = 0; i < rows * chunk_cols; ++i) {
        chunk_ptr[i] = 0; 
    }

    for (int local_x = 0; local_x < chunk_cols; ++local_x) {
        // 換算成絕對世界座標
        int absolute_x = offset_x + local_x; 

        float elevation = octave_noise_1d((float)absolute_x + seed * 100.0f, seed, 0.035f, 6.0f, 4);
        float continental = octave_noise_1d((float)absolute_x + seed * 310.0f, seed + 17, 0.0065f, 1.0f, 3);
        float temperature = octave_noise_1d((float)absolute_x + seed * 200.0f, seed + 1, 0.010f, 1.0f, 3);
        float moisture = octave_noise_1d((float)absolute_x - seed * 150.0f, seed + 29, 0.012f, 1.0f, 3);

        int is_deep_ocean = continental < -0.42f;
        int is_ocean = continental < -0.22f;
        int is_beach = !is_ocean && continental < -0.12f;
        int is_desert = !is_ocean && !is_beach && temperature > 0.05f && moisture < -0.08f;
        int is_jungle = !is_ocean && !is_beach && temperature > 0.25f && moisture > 0.12f;
        int is_forest = !is_ocean && !is_beach && !is_desert && moisture > -0.05f;

        int surface_y = base_height + (int)(elevation * 9.0f);
        int block_top = 1; 
        int block_mid = 2; 

        if (is_deep_ocean) {
            surface_y = sea_level + 10 + (int)(elevation * 3.0f);
            block_top = 6;
            block_mid = 6;
        } else if (is_ocean) {
            surface_y = sea_level + 4 + (int)(elevation * 4.0f);
            block_top = 6;
            block_mid = 6;
        } else if (is_beach) {
            surface_y = sea_level - 1 + (int)(elevation * 2.0f);
            block_top = 6;
            block_mid = 6;
        } else if (is_desert) {
            surface_y += 1;
            block_top = 6;
            block_mid = 6;
        } else if (is_jungle) {
            surface_y -= 2;
        } else if (is_forest) {
            surface_y -= 1;
        }

        if (surface_y < 2) surface_y = 2;
        if (surface_y > rows - 8) surface_y = rows - 8;

        // 寫入區塊記憶體
        chunk_ptr[surface_y * chunk_cols + local_x] = block_top; 
        for (int y = surface_y + 1; y < surface_y + 4 && y < rows; ++y) {
            chunk_ptr[y * chunk_cols + local_x] = block_mid; 
        }
        for (int y = surface_y + 4; y < rows; ++y) {
            chunk_ptr[y * chunk_cols + local_x] = 3; 
        }

        if (is_ocean) {
            for (int y = surface_y - 1; y >= sea_level; --y) {
                if (y > 0) chunk_ptr[y * chunk_cols + local_x] = 7; 
            }
        }

        // 樹木隨機生成
        if (!is_ocean && !is_desert && chunk_ptr[surface_y * chunk_cols + local_x] == 1) {
            float tree_chance = random_chance(absolute_x, surface_y, seed);
            float tree_threshold = is_jungle ? 0.72f : (is_forest ? 0.82f : 0.96f);
            if (tree_chance > tree_threshold) {
                int tree_height = is_jungle ? (random_chance(absolute_x, 1, seed) > 0.5f ? 7 : 9) : (is_forest ? 5 : 4); 
                for (int ty = 1; ty <= tree_height; ++ty) {
                    if (surface_y - ty >= 0) chunk_ptr[(surface_y - ty) * chunk_cols + local_x] = 8;
                }
                int leaf_y = surface_y - tree_height;
                if (leaf_y >= 2) {
                    int leaf_radius = is_jungle ? 3 : 2;
                    for (int ly = leaf_y - 2; ly <= leaf_y + 1; ++ly) {
                        for (int lx = local_x - leaf_radius; lx <= local_x + leaf_radius; ++lx) {
                            if (lx >= 0 && lx < chunk_cols && chunk_ptr[ly * chunk_cols + lx] == 0) {
                                if (is_jungle || is_forest || random_chance(absolute_x + lx - local_x, ly, seed) > 0.3f) {
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

import cv2
import numpy as np
import random

# --- 1. 渲染系統核心常數 ---
WINDOW_NAME = '2D Minecraft'
TILE_SIZE = 40      
COLS, ROWS = 32, 18 
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE

STATE_GAME = 0
STATE_MENU = 1
STATE_INVENTORY = 2
STATE_CRAFTING_TABLE = 3
STATE_TRADER = 4
inventory_slots = 9

MAX_STACK = 64
SLOT_SIZE = 46
SLOT_STEP = 55
INVENTORY_PANEL_W = 600
INVENTORY_PANEL_H = 560

# --- 2. OpenCV 材質生成 (BGR 色彩空間) ---
textures = {}
def create_texture(block_id):
    tex = np.zeros((TILE_SIZE, TILE_SIZE, 3), dtype=np.uint8)
    if block_id == 1: 
        tex[:] = (34, 69, 139); tex[0:10, :] = (50, 205, 50)
    elif block_id == 2: 
        tex[:] = (34, 69, 139)
        for _ in range(25): cv2.circle(tex, (random.randint(0, TILE_SIZE-1), random.randint(0, TILE_SIZE-1)), 2, (20, 50, 100), -1)
    elif block_id == 3: 
        tex[:] = (128, 128, 128); cv2.line(tex, (0, 0), (TILE_SIZE, 0), (180, 180, 180), 2)
    elif block_id == 4: 
        tex[:] = (42, 56, 89)
        cv2.rectangle(tex, (4,4), (TILE_SIZE-5, TILE_SIZE-5), (20, 30, 60), 2)
        cv2.line(tex, (0,0), (TILE_SIZE, TILE_SIZE), (0,0,0), 1)
    elif block_id == 5: 
        tex[:] = (200, 220, 240)
        cv2.line(tex, (10, 30), (30, 10), (20, 40, 80), 4)
    elif block_id == 6: 
        tex[:] = (120, 201, 237) 
        for _ in range(10): cv2.circle(tex, (random.randint(0, TILE_SIZE-1), random.randint(0, TILE_SIZE-1)), 1, (90, 160, 200), -1)
    elif block_id == 7: 
        tex[:] = (230, 150, 50) 
        cv2.line(tex, (0, 5), (TILE_SIZE, 5), (255, 200, 100), 2)
        return tex 
    elif block_id == 8: 
        tex[:] = (21, 53, 84) 
        cv2.rectangle(tex, (0, 0), (10, TILE_SIZE), (10, 30, 50), -1)
        cv2.rectangle(tex, (TILE_SIZE-10, 0), (TILE_SIZE, TILE_SIZE), (10, 30, 50), -1)
    elif block_id == 9: 
        tex[:] = (40, 150, 40)
        for _ in range(20): cv2.circle(tex, (random.randint(0, TILE_SIZE-1), random.randint(0, TILE_SIZE-1)), 3, (20, 100, 20), -1)
        return tex
    elif block_id == 10:
        tex[:] = (60, 120, 190)
        for y in range(8, TILE_SIZE, 12):
            cv2.line(tex, (0, y), (TILE_SIZE, y), (35, 80, 140), 2)
        cv2.line(tex, (TILE_SIZE // 2, 0), (TILE_SIZE // 2, TILE_SIZE), (35, 80, 140), 2)
    elif block_id == 11:
        tex[:] = (80, 80, 80)
        cv2.line(tex, (12, 10), (28, 10), (50, 95, 160), 5)
        cv2.line(tex, (20, 12), (20, 32), (30, 55, 90), 4)
    elif block_id == 12:
        tex[:] = (80, 80, 80)
        cv2.line(tex, (10, 10), (30, 30), (50, 95, 160), 4)
        cv2.line(tex, (28, 8), (34, 14), (180, 180, 190), 4)
    elif block_id == 13:
        tex[:] = (80, 80, 80)
        cv2.line(tex, (20, 10), (20, 32), (30, 55, 90), 4)
        cv2.rectangle(tex, (10, 8), (30, 16), (50, 95, 160), -1)
    elif block_id == 14:
        tex[:] = (80, 80, 80)
        cv2.line(tex, (14, 12), (28, 28), (30, 55, 90), 4)
        cv2.ellipse(tex, (18, 12), (10, 8), -25, 0, 360, (50, 95, 160), -1)
    elif block_id == 15:
        tex[:] = (50, 50, 50)
        cv2.circle(tex, (20, 20), 10, (20, 20, 20), -1)
    elif block_id == 16:
        tex[:] = (80, 80, 80)
        cv2.line(tex, (20, 32), (20, 12), (30, 55, 90), 3)
        cv2.circle(tex, (20, 10), 6, (40, 220, 255), -1)
    elif block_id == 17:
        tex[:] = (120, 120, 120)
        for p in [(10, 10), (28, 18), (18, 30)]:
            cv2.circle(tex, p, 4, (80, 150, 200), -1)
    elif block_id == 18:
        tex[:] = (80, 80, 80)
        cv2.rectangle(tex, (9, 14), (31, 27), (130, 190, 220), -1)
    elif block_id in (19, 20, 21, 22):
        tex[:] = (80, 80, 80)
        color = (130, 190, 220)
        cv2.line(tex, (20, 12), (20, 34), (30, 55, 90), 4)
        cv2.rectangle(tex, (10, 8), (30, 16), color, -1)
        if block_id == 21:
            cv2.line(tex, (20, 8), (20, 34), color, 5)
        elif block_id == 22:
            cv2.rectangle(tex, (9, 8), (25, 18), color, -1)
    elif block_id == 23:
        tex[:] = (110, 110, 120)
        for p in [(12, 11), (25, 20), (18, 31)]:
            cv2.circle(tex, p, 4, (255, 230, 90), -1)
    elif block_id == 24:
        tex[:] = (80, 80, 80)
        cv2.circle(tex, (20, 20), 10, (255, 230, 90), -1)
    elif block_id in (25, 26, 27, 28):
        tex[:] = (80, 80, 80)
        color = (255, 230, 90)
        cv2.line(tex, (20, 12), (20, 34), (30, 55, 90), 4)
        cv2.rectangle(tex, (10, 8), (30, 16), color, -1)
        if block_id == 27:
            cv2.line(tex, (20, 8), (20, 34), color, 5)
        elif block_id == 28:
            cv2.rectangle(tex, (9, 8), (25, 18), color, -1)
    elif block_id == 29:
        tex[:] = (105, 105, 105)
        for _ in range(8):
            cv2.circle(tex, (random.randint(4, TILE_SIZE-5), random.randint(4, TILE_SIZE-5)), 3, (80, 80, 80), -1)
    elif block_id in (30, 31, 32, 33):
        tex[:] = (80, 80, 80)
        color = (155, 155, 155)
        cv2.line(tex, (20, 12), (20, 34), (30, 55, 90), 4)
        cv2.rectangle(tex, (10, 8), (30, 16), color, -1)
        if block_id == 32:
            cv2.line(tex, (20, 8), (20, 34), color, 5)
        elif block_id == 33:
            cv2.rectangle(tex, (9, 8), (25, 18), color, -1)
    elif block_id == 34:
        tex[:] = (120, 120, 120)
        for p in [(11, 12), (28, 18), (19, 30)]:
            cv2.circle(tex, p, 4, (30, 190, 240), -1)
    elif block_id == 35:
        tex[:] = (80, 80, 80)
        cv2.rectangle(tex, (9, 14), (31, 27), (30, 190, 240), -1)
    elif block_id in (36, 37, 38, 39):
        tex[:] = (80, 80, 80)
        color = (30, 190, 240)
        cv2.line(tex, (20, 12), (20, 34), (30, 55, 90), 4)
        cv2.rectangle(tex, (10, 8), (30, 16), color, -1)
        if block_id == 38:
            cv2.line(tex, (20, 8), (20, 34), color, 5)
        elif block_id == 39:
            cv2.rectangle(tex, (9, 8), (25, 18), color, -1)
    elif block_id == 40:
        tex[:] = (70, 70, 70)
        for x in (11, 20, 29):
            cv2.circle(tex, (x, 20), 5, (30, 190, 240), -1)
    elif block_id in (41, 42, 43, 44):
        tex[:] = (80, 80, 80)
        color = {41: (150,150,150), 42: (130,190,220), 43: (30,190,240), 44: (255,230,90)}[block_id]
        cv2.rectangle(tex, (7, 17), (31, 24), color, -1)
        cv2.rectangle(tex, (24, 12), (36, 17), color, -1)
        cv2.rectangle(tex, (11, 24), (17, 33), (30,55,90), -1)
        cv2.circle(tex, (8, 20), 3, (20,20,20), -1)
    elif block_id == 45:
        tex[:] = (45, 85, 140)
        cv2.rectangle(tex, (4, 8), (36, 34), (40, 95, 165), -1)
        cv2.rectangle(tex, (4, 8), (36, 34), (20, 45, 80), 2)
        cv2.rectangle(tex, (17, 18), (23, 24), (30, 190, 240), -1)
    elif block_id == 46:
        tex[:] = (80, 80, 80)
        cv2.rectangle(tex, (7, 20), (33, 34), (60, 120, 190), -1)
        cv2.line(tex, (5, 20), (20, 8), (21, 53, 84), 3)
        cv2.line(tex, (20, 8), (35, 20), (21, 53, 84), 3)
    elif block_id in (47, 48, 49, 50, 51):
        tex[:] = (65, 65, 65)
        colors = {
            47: ((235, 235, 235), (40, 120, 230)),
            48: ((120, 150, 230), (75, 95, 190)),
            49: ((45, 80, 165), (25, 45, 120)),
            50: ((220, 220, 220), (150, 150, 150)),
            51: ((55, 105, 175), (25, 55, 95)),
        }
        body, detail = colors[block_id]
        cv2.ellipse(tex, (20, 21), (13, 10), -18, 0, 360, body, -1)
        cv2.circle(tex, (27, 15), 6, body, -1)
        cv2.rectangle(tex, (10, 27), (22, 32), detail, -1)
        cv2.circle(tex, (30, 14), 2, (255, 255, 255), -1)
        
    cv2.rectangle(tex, (0,0), (TILE_SIZE-1, TILE_SIZE-1), (0,0,0), 1)
    return tex

for i in range(1, 52): textures[i] = create_texture(i)

def get_menu_action(mouse_x, mouse_y):
    buttons = [
        ("back", HEIGHT // 2 - 20),
        ("save_quit", HEIGHT // 2 + 50),
    ]
    btn_w, btn_h, btn_x = 400, 50, WIDTH // 2 - 200
    for action, btn_y in buttons:
        if btn_x <= mouse_x <= btn_x + btn_w and btn_y <= mouse_y <= btn_y + btn_h:
            return action
    return None

def get_inventory_panel_rect():
    px = (WIDTH - INVENTORY_PANEL_W) // 2
    py = (HEIGHT - INVENTORY_PANEL_H) // 2
    return px, py, INVENTORY_PANEL_W, INVENTORY_PANEL_H

def get_inventory_slot_rect(index):
    px, py, _, _ = get_inventory_panel_rect()
    grid_start_x, grid_start_y = px + 50, py + 265
    col, row = index % 9, index // 9
    slot_x = grid_start_x + col * SLOT_STEP
    slot_y = grid_start_y + row * SLOT_STEP if row < 3 else py + 455
    return slot_x, slot_y, SLOT_SIZE, SLOT_SIZE

def get_crafting_slot_rect(index):
    px, py, _, _ = get_inventory_panel_rect()
    craft_start_x, craft_start_y = px + 150, py + 80
    col, row = index % 2, index // 2
    return craft_start_x + col * SLOT_STEP, craft_start_y + row * SLOT_STEP, SLOT_SIZE, SLOT_SIZE

def get_crafting_output_rect():
    px, py, _, _ = get_inventory_panel_rect()
    craft_start_x, craft_start_y = px + 150, py + 80
    arrow_x, arrow_y = craft_start_x + 130, craft_start_y + 35
    return arrow_x + 60, arrow_y - 15, 50, 50

def get_table_slot_rect(index):
    px, py, _, _ = get_inventory_panel_rect()
    craft_start_x, craft_start_y = px + 95, py + 70
    col, row = index % 3, index // 3
    return craft_start_x + col * SLOT_STEP, craft_start_y + row * SLOT_STEP, SLOT_SIZE, SLOT_SIZE

def get_table_output_rect():
    px, py, _, _ = get_inventory_panel_rect()
    return px + 370, py + 125, 50, 50

def rect_contains(rect, mouse_x, mouse_y):
    x, y, w, h = rect
    return x <= mouse_x <= x + w and y <= mouse_y <= y + h

def get_inventory_slot_at(mouse_x, mouse_y):
    for i in range(36):
        if rect_contains(get_inventory_slot_rect(i), mouse_x, mouse_y):
            return i
    return None

def get_crafting_slot_at(mouse_x, mouse_y):
    for i in range(4):
        if rect_contains(get_crafting_slot_rect(i), mouse_x, mouse_y):
            return i
    return None

def get_table_slot_at(mouse_x, mouse_y):
    for i in range(9):
        if rect_contains(get_table_slot_rect(i), mouse_x, mouse_y):
            return i
    return None

def draw_item_stack(canvas, item, x, y, size=32):
    if item["id"] != 0 and item["id"] in textures:
        mini_tex = cv2.resize(textures[item["id"]], (size, size))
        pad = max(0, (SLOT_SIZE - size) // 2)
        canvas[y+pad:y+pad+size, x+pad:x+pad+size] = mini_tex
        cv2.putText(canvas, str(item["count"]), (x + 25, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

def get_hovered_item(mouse_x, mouse_y, inventory=None, crafting_grid=None, table_grid=None, output=None, table_output=None):
    if crafting_grid:
        for i, item in enumerate(crafting_grid):
            if rect_contains(get_crafting_slot_rect(i), mouse_x, mouse_y) and item["id"] != 0:
                return item
    if table_grid:
        for i, item in enumerate(table_grid):
            if rect_contains(get_table_slot_rect(i), mouse_x, mouse_y) and item["id"] != 0:
                return item
    if inventory:
        for i, item in enumerate(inventory):
            if rect_contains(get_inventory_slot_rect(i), mouse_x, mouse_y) and item["id"] != 0:
                return item
    if output and rect_contains(get_crafting_output_rect(), mouse_x, mouse_y) and output["id"] != 0:
        return output
    if table_output and rect_contains(get_table_output_rect(), mouse_x, mouse_y) and table_output["id"] != 0:
        return table_output
    return None

def get_item_rarity_color(item_id):
    if item_id in (47, 48, 49, 50, 51):
        return (120, 230, 160)
    if item_id in (41, 42, 43, 44, 46):
        return (120, 255, 255)
    if item_id in (23, 24, 25, 26, 27, 28):
        return (255, 235, 90)
    if item_id in (34, 35, 36, 37, 38, 39):
        return (30, 210, 255)
    if item_id in (17, 18, 19, 20, 21, 22):
        return (180, 220, 240)
    if item_id in (29, 30, 31, 32, 33):
        return (190, 190, 190)
    if item_id in (11, 12, 13, 14):
        return (90, 150, 230)
    return (255, 255, 255)

def get_item_tip_lines(item, item_names, tool_speeds=None, weapon_damage=None, placeable_blocks=None):
    item_id = item["id"]
    lines = [item_names.get(item_id, f"Item {item_id}")]
    lines.append(f"Count: {item['count']}")
    if weapon_damage and item_id in weapon_damage:
        lines.append(f"Attack: {weapon_damage[item_id]}")
    if tool_speeds and item_id in tool_speeds:
        speeds = tool_speeds[item_id]
        parts = []
        if "stone" in speeds and speeds["stone"] > 1:
            parts.append(f"Stone x{speeds['stone']:.1f}")
        if "dirt" in speeds and speeds["dirt"] > 1:
            parts.append(f"Dirt x{speeds['dirt']:.1f}")
        if "wood" in speeds and speeds["wood"] > 1:
            parts.append(f"Wood x{speeds['wood']:.1f}")
        if parts:
            lines.append("Mine: " + "  ".join(parts))
    if placeable_blocks and item_id in placeable_blocks:
        lines.append("Placeable block")
    if item_id in (47, 48, 49, 50, 51):
        lines.append("Food: right click to eat")
    return lines

def draw_item_tooltip(canvas, item, mouse_x, mouse_y, item_names, tool_speeds=None, weapon_damage=None, placeable_blocks=None):
    if not item or item["id"] == 0:
        return
    lines = get_item_tip_lines(item, item_names, tool_speeds, weapon_damage, placeable_blocks)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.48
    thickness = 1
    sizes = [cv2.getTextSize(line, font, scale, thickness)[0] for line in lines]
    box_w = max(w for w, _ in sizes) + 24
    box_h = 22 + len(lines) * 22
    x = min(mouse_x + 18, WIDTH - box_w - 8)
    y = min(mouse_y + 18, HEIGHT - box_h - 8)
    x, y = max(8, x), max(8, y)

    cv2.rectangle(canvas, (x+3, y+3), (x+box_w+3, y+box_h+3), (0, 0, 0), -1)
    cv2.rectangle(canvas, (x, y), (x+box_w, y+box_h), (32, 28, 38), -1)
    border = get_item_rarity_color(item["id"])
    cv2.rectangle(canvas, (x, y), (x+box_w, y+box_h), border, 2)

    cv2.putText(canvas, lines[0], (x+12, y+24), font, 0.55, border, 1)
    for idx, line in enumerate(lines[1:], start=1):
        cv2.putText(canvas, line, (x+12, y+24+idx*22), font, scale, (235, 235, 235), thickness)

# --- 3. UI 與畫面渲染 ---
def draw_hud(canvas, hp, hunger, inventory, selected_slot, level=1, xp=0, xp_next=10, money=0):
    for i in range(10):
        hx, hy = 20 + i * 22, 20
        cv2.rectangle(canvas, (hx, hy), (hx+16, hy+16), (0,0,0), -1)
        if i < hp: cv2.rectangle(canvas, (hx+2, hy+2), (hx+14, hy+14), (50,50,200), -1)

    for i in range(10):
        hx, hy = 20 + i * 22, 45
        cv2.rectangle(canvas, (hx, hy), (hx+16, hy+16), (0,0,0), -1)
        if i < hunger: cv2.rectangle(canvas, (hx+2, hy+2), (hx+14, hy+14), (50,150,250), -1)

    xp_ratio = 0 if xp_next <= 0 else max(0.0, min(1.0, xp / xp_next))
    cv2.rectangle(canvas, (20, 70), (240, 84), (20, 35, 30), -1)
    cv2.rectangle(canvas, (22, 72), (22 + int(216 * xp_ratio), 82), (70, 210, 90), -1)
    cv2.rectangle(canvas, (20, 70), (240, 84), (0, 0, 0), 1)
    cv2.putText(canvas, f"Lv {level}  XP {xp}/{xp_next}", (20, 103), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (120, 255, 150), 1)
    cv2.putText(canvas, f"$ {money}", (160, 103), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (70, 230, 255), 1)

    bar_w = inventory_slots * 42
    bar_x = (WIDTH - bar_w) // 2
    bar_y = HEIGHT - 50
    
    overlay = canvas[bar_y-5 : HEIGHT, bar_x-5 : bar_x+bar_w+5].copy()
    cv2.rectangle(overlay, (0,0), (bar_w+10, 60), (0,0,0), -1)
    cv2.addWeighted(overlay, 0.5, canvas[bar_y-5 : HEIGHT, bar_x-5 : bar_x+bar_w+5], 0.5, 0, canvas[bar_y-5 : HEIGHT, bar_x-5 : bar_x+bar_w+5])
    
    for i in range(inventory_slots):
        sx, sy = bar_x + i * 42, bar_y
        cv2.rectangle(canvas, (sx, sy), (sx+38, sy+38), (100,100,100), -1)
        if i == selected_slot: cv2.rectangle(canvas, (sx-2, sy-2), (sx+40, sy+40), (255,255,255), 2)
        else: cv2.rectangle(canvas, (sx, sy), (sx+38, sy+38), (50,50,50), 2)
            
        item = inventory[i]
        if item["id"] != 0 and item["id"] in textures:
            mini_tex = cv2.resize(textures[item["id"]], (24, 24))
            canvas[sy+7:sy+31, sx+7:sx+31] = mini_tex
            cv2.putText(canvas, str(item["count"]), (sx+20, sy+35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)

def draw_minecraft_menu(base_canvas, mouse_x, mouse_y):
    overlay = base_canvas.copy()
    cv2.rectangle(overlay, (0, 0), (WIDTH, HEIGHT), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, base_canvas, 0.4, 0, base_canvas)
    cv2.putText(base_canvas, "Game Menu", (WIDTH//2 - 120, HEIGHT//2 - 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    
    buttons = [{"text": "Back to Game", "y": HEIGHT // 2 - 20}, {"text": "Save and Quit", "y": HEIGHT // 2 + 50}]
    btn_w, btn_h, btn_x = 400, 50, WIDTH // 2 - 200
    for btn in buttons:
        btn_y = btn["y"]
        is_hover = (btn_x <= mouse_x <= btn_x + btn_w) and (btn_y <= mouse_y <= btn_y + btn_h)
        bg_color, border_color, text_color = ((180, 180, 180), (255, 255, 255), (255, 255, 100)) if is_hover else ((100, 100, 100), (0, 0, 0), (255, 255, 255))
        cv2.rectangle(base_canvas, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), bg_color, -1)
        cv2.rectangle(base_canvas, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), border_color, 2)
        
        text_size = cv2.getTextSize(btn["text"], cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        text_x = btn_x + (btn_w - text_size[0]) // 2
        text_y = btn_y + (btn_h + text_size[1]) // 2
        cv2.putText(base_canvas, btn["text"], (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
    return base_canvas

def draw_inventory_screen(base_canvas, inventory, crafting_grid, crafting_output, mouse_x, mouse_y, cursor_item, item_names=None, tool_speeds=None, weapon_damage=None, placeable_blocks=None):
    item_names = item_names or {}
    canvas = base_canvas.copy()
    overlay = canvas.copy()
    cv2.rectangle(overlay, (0, 0), (WIDTH, HEIGHT), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, canvas, 0.5, 0, canvas)
    
    px, py, panel_w, panel_h = get_inventory_panel_rect()
    cv2.rectangle(canvas, (px, py), (px + panel_w, py + panel_h), (150, 150, 150), -1)
    cv2.rectangle(canvas, (px, py), (px + panel_w, py + panel_h), (50, 50, 50), 3)
    cv2.putText(canvas, "Inventory & Crafting", (px + 20, py + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    selected_item = get_hovered_item(mouse_x, mouse_y, inventory=inventory, crafting_grid=crafting_grid, output=crafting_output)
    name_text = item_names.get(selected_item["id"], "") if selected_item else "Hover an item for details"
    cv2.rectangle(canvas, (px + 300, py + 16), (px + panel_w - 18, py + 45), (90, 90, 90), -1)
    cv2.putText(canvas, name_text[:28], (px + 312, py + 37), cv2.FONT_HERSHEY_SIMPLEX, 0.5, get_item_rarity_color(selected_item["id"]) if selected_item else (230, 230, 230), 1)
    
    for i in range(36):
        slot_x, slot_y, slot_w, slot_h = get_inventory_slot_rect(i)
        
        is_hover = rect_contains((slot_x, slot_y, slot_w, slot_h), mouse_x, mouse_y)
        bg_color = (180, 180, 180) if is_hover else (100, 100, 100)
        cv2.rectangle(canvas, (slot_x, slot_y), (slot_x + slot_w, slot_y + slot_h), bg_color, -1)
        cv2.rectangle(canvas, (slot_x, slot_y), (slot_x + slot_w, slot_y + slot_h), (50, 50, 50), 1)
        
        item = inventory[i]
        draw_item_stack(canvas, item, slot_x, slot_y)

    for i in range(4):
        cx, cy, cw, ch = get_crafting_slot_rect(i)
        is_hover = rect_contains((cx, cy, cw, ch), mouse_x, mouse_y)
        bg_color = (180, 180, 180) if is_hover else (100, 100, 100)
        cv2.rectangle(canvas, (cx, cy), (cx + cw, cy + ch), bg_color, -1)
        cv2.rectangle(canvas, (cx, cy), (cx + cw, cy + ch), (40, 40, 40), 1)
        
        item = crafting_grid[i]
        draw_item_stack(canvas, item, cx, cy)

    craft_start_x, craft_start_y = px + 150, py + 80
    arrow_x, arrow_y = craft_start_x + 130, craft_start_y + 35
    cv2.line(canvas, (arrow_x, arrow_y), (arrow_x + 40, arrow_y), (50, 50, 50), 4)
    cv2.line(canvas, (arrow_x + 30, arrow_y - 10), (arrow_x + 40, arrow_y), (50, 50, 50), 4)
    cv2.line(canvas, (arrow_x + 30, arrow_y + 10), (arrow_x + 40, arrow_y), (50, 50, 50), 4)

    out_x, out_y, out_w, out_h = get_crafting_output_rect()
    is_hover_out = rect_contains((out_x, out_y, out_w, out_h), mouse_x, mouse_y)
    bg_out = (200, 200, 200) if is_hover_out else (120, 120, 120)
    cv2.rectangle(canvas, (out_x, out_y), (out_x + out_w, out_y + out_h), bg_out, -1)
    cv2.rectangle(canvas, (out_x, out_y), (out_x + out_w, out_y + out_h), (20, 20, 20), 2)
    
    if crafting_output["id"] != 0:
        mini_tex = cv2.resize(textures[crafting_output["id"]], (36, 36))
        canvas[out_y+7:out_y+43, out_x+7:out_x+43] = mini_tex
        cv2.putText(canvas, str(crafting_output["count"]), (out_x + 30, out_y + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    if cursor_item["id"] != 0:
        floating_tex = cv2.resize(textures[cursor_item["id"]], (32, 32))
        x1, x2 = max(0, mouse_x - 16), min(WIDTH, mouse_x + 16)
        y1, y2 = max(0, mouse_y - 16), min(HEIGHT, mouse_y + 16)
        if (x2 - x1 == 32) and (y2 - y1 == 32):
            canvas[y1:y2, x1:x2] = floating_tex
            cv2.putText(canvas, str(cursor_item["count"]), (mouse_x + 4, mouse_y + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 100), 1)

    draw_item_tooltip(canvas, selected_item, mouse_x, mouse_y, item_names, tool_speeds, weapon_damage, placeable_blocks)
    return canvas

def draw_crafting_table_screen(base_canvas, inventory, table_grid, table_output, mouse_x, mouse_y, cursor_item, item_names=None, tool_speeds=None, weapon_damage=None, placeable_blocks=None):
    item_names = item_names or {}
    canvas = base_canvas.copy()
    overlay = canvas.copy()
    cv2.rectangle(overlay, (0, 0), (WIDTH, HEIGHT), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, canvas, 0.5, 0, canvas)

    px, py, panel_w, panel_h = get_inventory_panel_rect()
    cv2.rectangle(canvas, (px, py), (px + panel_w, py + panel_h), (150, 150, 150), -1)
    cv2.rectangle(canvas, (px, py), (px + panel_w, py + panel_h), (50, 50, 50), 3)
    cv2.putText(canvas, "Crafting Table", (px + 20, py + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    selected_item = get_hovered_item(mouse_x, mouse_y, inventory=inventory, table_grid=table_grid, table_output=table_output)
    name_text = item_names.get(selected_item["id"], "") if selected_item else "3x3 crafting unlocked"
    cv2.rectangle(canvas, (px + 300, py + 16), (px + panel_w - 18, py + 45), (90, 90, 90), -1)
    cv2.putText(canvas, name_text[:28], (px + 312, py + 37), cv2.FONT_HERSHEY_SIMPLEX, 0.5, get_item_rarity_color(selected_item["id"]) if selected_item else (230, 230, 230), 1)

    for i in range(9):
        sx, sy, sw, sh = get_table_slot_rect(i)
        bg_color = (180, 180, 180) if rect_contains((sx, sy, sw, sh), mouse_x, mouse_y) else (100, 100, 100)
        cv2.rectangle(canvas, (sx, sy), (sx + sw, sy + sh), bg_color, -1)
        cv2.rectangle(canvas, (sx, sy), (sx + sw, sy + sh), (40, 40, 40), 1)
        draw_item_stack(canvas, table_grid[i], sx, sy)

    arrow_x, arrow_y = px + 305, py + 148
    cv2.line(canvas, (arrow_x, arrow_y), (arrow_x + 45, arrow_y), (50, 50, 50), 4)
    cv2.line(canvas, (arrow_x + 35, arrow_y - 10), (arrow_x + 45, arrow_y), (50, 50, 50), 4)
    cv2.line(canvas, (arrow_x + 35, arrow_y + 10), (arrow_x + 45, arrow_y), (50, 50, 50), 4)

    out_x, out_y, out_w, out_h = get_table_output_rect()
    bg_out = (200, 200, 200) if rect_contains((out_x, out_y, out_w, out_h), mouse_x, mouse_y) else (120, 120, 120)
    cv2.rectangle(canvas, (out_x, out_y), (out_x + out_w, out_y + out_h), bg_out, -1)
    cv2.rectangle(canvas, (out_x, out_y), (out_x + out_w, out_y + out_h), (20, 20, 20), 2)
    if table_output["id"] != 0:
        mini_tex = cv2.resize(textures[table_output["id"]], (36, 36))
        canvas[out_y+7:out_y+43, out_x+7:out_x+43] = mini_tex
        cv2.putText(canvas, str(table_output["count"]), (out_x + 30, out_y + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    for i in range(36):
        slot_x, slot_y, slot_w, slot_h = get_inventory_slot_rect(i)
        bg_color = (180, 180, 180) if rect_contains((slot_x, slot_y, slot_w, slot_h), mouse_x, mouse_y) else (100, 100, 100)
        cv2.rectangle(canvas, (slot_x, slot_y), (slot_x + slot_w, slot_y + slot_h), bg_color, -1)
        cv2.rectangle(canvas, (slot_x, slot_y), (slot_x + slot_w, slot_y + slot_h), (50, 50, 50), 1)
        draw_item_stack(canvas, inventory[i], slot_x, slot_y)

    if cursor_item["id"] != 0:
        floating_tex = cv2.resize(textures[cursor_item["id"]], (32, 32))
        x1, x2 = max(0, mouse_x - 16), min(WIDTH, mouse_x + 16)
        y1, y2 = max(0, mouse_y - 16), min(HEIGHT, mouse_y + 16)
        if (x2 - x1 == 32) and (y2 - y1 == 32):
            canvas[y1:y2, x1:x2] = floating_tex
            cv2.putText(canvas, str(cursor_item["count"]), (mouse_x + 4, mouse_y + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 100), 1)

    draw_item_tooltip(canvas, selected_item, mouse_x, mouse_y, item_names, tool_speeds, weapon_damage, placeable_blocks)
    return canvas

def get_trader_trade_rect(index):
    panel_w = 760
    panel_x = (WIDTH - panel_w) // 2
    row_y = 155 + index * 62
    return panel_x + 36, row_y, panel_w - 72, 50

def get_trader_trade_at(mouse_x, mouse_y, trade_count):
    for i in range(trade_count):
        if rect_contains(get_trader_trade_rect(i), mouse_x, mouse_y):
            return i
    return None

def draw_trader_screen(base_canvas, trades, mouse_x, mouse_y, item_names, level, xp, xp_next, money, message=""):
    canvas = base_canvas.copy()
    overlay = canvas.copy()
    cv2.rectangle(overlay, (0, 0), (WIDTH, HEIGHT), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.55, canvas, 0.45, 0, canvas)

    panel_w, panel_h = 760, 540
    panel_x, panel_y = (WIDTH - panel_w) // 2, (HEIGHT - panel_h) // 2
    cv2.rectangle(canvas, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), (82, 86, 92), -1)
    cv2.rectangle(canvas, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), (30, 35, 40), 3)
    cv2.putText(canvas, "Wandering Trader", (panel_x + 28, panel_y + 42), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 245, 210), 2)
    cv2.putText(canvas, f"Level {level}   XP {xp}/{xp_next}   $ {money}", (panel_x + 410, panel_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (140, 255, 180), 1)
    cv2.putText(canvas, "Click a trade. ESC closes.", (panel_x + 28, panel_y + 78), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (225, 225, 225), 1)

    for i, trade in enumerate(trades):
        x, y, w, h = get_trader_trade_rect(i)
        hover = rect_contains((x, y, w, h), mouse_x, mouse_y)
        bg = (118, 125, 132) if hover else (96, 102, 109)
        cv2.rectangle(canvas, (x, y), (x + w, y + h), bg, -1)
        cv2.rectangle(canvas, (x, y), (x + w, y + h), (38, 42, 48), 2)

        result = trade["result"]
        if result["id"] in textures:
            icon = cv2.resize(textures[result["id"]], (34, 34))
            canvas[y+8:y+42, x+10:x+44] = icon
        name = item_names.get(result["id"], f"Item {result['id']}")
        cv2.putText(canvas, f"{name} x{result['count']}", (x + 56, y + 21), cv2.FONT_HERSHEY_SIMPLEX, 0.52, get_item_rarity_color(result["id"]), 1)
        cv2.putText(canvas, trade.get("desc", ""), (x + 56, y + 42), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (225, 225, 225), 1)
        cv2.putText(canvas, trade.get("cost_text", ""), (x + 420, y + 31), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (90, 235, 255), 1)

    if message:
        cv2.rectangle(canvas, (panel_x + 28, panel_y + panel_h - 58), (panel_x + panel_w - 28, panel_y + panel_h - 22), (52, 58, 64), -1)
        cv2.putText(canvas, message[:72], (panel_x + 42, panel_y + panel_h - 34), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 245, 245), 1)
    return canvas

# --- 【無限世界核心修復】現在 draw_game_scene 只負責渲染裁剪後的 visible_world 矩陣 ---
def draw_game_scene(sky_color, visible_world, player_data, mining_data, particles, frame_count, camera_subpixel_x, camera_subpixel_y, target_data=None, mobs=None, animals=None, birds=None, dropped_items=None, planes=None, sunbirds=None, npcs=None, projectiles=None):
    bgr_sky = (sky_color[2], sky_color[1], sky_color[0])
    canvas = np.full((HEIGHT, WIDTH, 3), bgr_sky, dtype=np.uint8)
    
    # 直接在 visible_world 上進行全螢幕循環繪製 (效能極高)
    for y in range(min(visible_world.shape[0], ROWS + 2)):
        for x in range(min(visible_world.shape[1], COLS + 2)): 
            block_id = visible_world[y, x]
            if block_id != 0:
                sx = x * TILE_SIZE - camera_subpixel_x
                sy = y * TILE_SIZE - camera_subpixel_y
                if -TILE_SIZE <= sx < WIDTH and -TILE_SIZE <= sy < HEIGHT:
                    dst_x1, dst_x2 = max(0, sx), min(WIDTH, sx + TILE_SIZE)
                    dst_y1, dst_y2 = max(0, sy), min(HEIGHT, sy + TILE_SIZE)
                    src_x1, src_x2 = dst_x1 - sx, TILE_SIZE - max(0, sx + TILE_SIZE - WIDTH)
                    src_y1, src_y2 = dst_y1 - sy, TILE_SIZE - max(0, sy + TILE_SIZE - HEIGHT)
                    canvas[dst_y1:dst_y2, dst_x1:dst_x2] = textures[block_id][src_y1:src_y2, src_x1:src_x2]

    is_mining, mx, my, progress, max_time = mining_data
    if is_mining:
        damage_ratio = progress / max_time
        px, py = mx * TILE_SIZE - camera_subpixel_x, my * TILE_SIZE - camera_subpixel_y
        if -TILE_SIZE <= px < WIDTH and -TILE_SIZE <= py < HEIGHT:
            cv2.rectangle(canvas, (px, py), (px+TILE_SIZE, py+TILE_SIZE), (0,0,0), int(TILE_SIZE*0.2*damage_ratio)+1)

    if target_data and target_data[0]:
        _, tx, ty = target_data
        ox, oy = tx * TILE_SIZE - camera_subpixel_x, ty * TILE_SIZE - camera_subpixel_y
        if -TILE_SIZE <= ox < WIDTH and -TILE_SIZE <= oy < HEIGHT:
            cv2.rectangle(canvas, (ox, oy), (ox+TILE_SIZE-1, oy+TILE_SIZE-1), (255,255,255), 2)
            cv2.rectangle(canvas, (ox+2, oy+2), (ox+TILE_SIZE-3, oy+TILE_SIZE-3), (20,20,20), 1)

    ppx, ppy, vel_x, is_grounded, facing_right = player_data[:5]
    is_swimming = len(player_data) > 5 and player_data[5]
    screen_px = WIDTH // 2 - TILE_SIZE // 2 
    screen_py = HEIGHT // 2 - TILE_SIZE // 2
    center_x = screen_px + TILE_SIZE // 2

    for drop in dropped_items or []:
        spx = int(drop["x"] - (ppx - screen_px))
        spy = int(drop["y"] - (ppy - screen_py))
        if -20 <= spx < WIDTH and -20 <= spy < HEIGHT and drop.get("id") in textures:
            bob = int(np.sin(frame_count * 0.12 + drop.get("age", 0) * 0.05) * 2)
            mini_tex = cv2.resize(textures[drop["id"]], (18, 18))
            x1, y1 = max(0, spx), max(0, spy + bob)
            x2, y2 = min(WIDTH, spx + 18), min(HEIGHT, spy + 18 + bob)
            sx1, sy1 = x1 - spx, y1 - (spy + bob)
            sx2, sy2 = sx1 + (x2 - x1), sy1 + (y2 - y1)
            if x2 > x1 and y2 > y1:
                canvas[y1:y2, x1:x2] = mini_tex[sy1:sy2, sx1:sx2]
            cv2.putText(canvas, str(drop.get("count", 1)), (spx + 10, spy + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1)

    for animal in animals or []:
        spx = int(animal["x"] - (ppx - screen_px))
        spy = int(animal["y"] - (ppy - screen_py))
        if -TILE_SIZE <= spx < WIDTH and -TILE_SIZE <= spy < HEIGHT:
            kind = animal.get("type", "cow")
            if kind == "pig":
                body, detail = (120, 155, 230), (90, 110, 200)
            elif kind == "sheep":
                body, detail = (235, 235, 235), (150, 150, 150)
            elif kind == "chicken":
                body, detail = (245, 245, 245), (30, 60, 230)
                cv2.ellipse(canvas, (spx+18, spy+25), (13, 10), 0, 0, 360, body, -1)
                cv2.circle(canvas, (spx+29, spy+17), 7, body, -1)
                cv2.circle(canvas, (spx+32, spy+16), 2, (0,0,0), -1)
                cv2.line(canvas, (spx+34, spy+18), (spx+39, spy+17), detail, 2)
                cv2.line(canvas, (spx+14, spy+34), (spx+12, spy+40), (40,120,230), 2)
                cv2.line(canvas, (spx+23, spy+34), (spx+24, spy+40), (40,120,230), 2)
                continue
            elif kind == "deer":
                body, detail = (55, 100, 155), (25, 55, 90)
                cv2.rectangle(canvas, (spx+5, spy+17), (spx+35, spy+32), body, -1)
                cv2.rectangle(canvas, (spx+26, spy+7), (spx+38, spy+20), body, -1)
                cv2.line(canvas, (spx+30, spy+7), (spx+25, spy+0), detail, 2)
                cv2.line(canvas, (spx+35, spy+7), (spx+40, spy+0), detail, 2)
                cv2.circle(canvas, (spx+35, spy+12), 2, (0,0,0), -1)
                for lx in (9, 15, 27, 33):
                    cv2.line(canvas, (spx+lx, spy+32), (spx+lx-1, spy+40), detail, 2)
                continue
            else:
                body, detail = (70, 110, 160), (35, 55, 90)
            cv2.rectangle(canvas, (spx+5, spy+17), (spx+35, spy+34), body, -1)
            cv2.rectangle(canvas, (spx+24, spy+9), (spx+38, spy+23), body, -1)
            cv2.circle(canvas, (spx+34, spy+15), 2, (0,0,0), -1)
            cv2.rectangle(canvas, (spx+8, spy+34), (spx+14, spy+40), detail, -1)
            cv2.rectangle(canvas, (spx+28, spy+34), (spx+34, spy+40), detail, -1)

    for bird in birds or []:
        spx = int(bird["x"] - (ppx - screen_px))
        spy = int(bird["y"] - (ppy - screen_py))
        if -40 <= spx < WIDTH + 40 and -20 <= spy < HEIGHT:
            kind = bird.get("type", "sparrow")
            color = {"hawk": (45, 75, 130), "crow": (25, 25, 25), "sparrow": (90, 110, 135)}.get(kind, (80,80,80))
            wing = 16 if kind == "hawk" else 12
            flap = int(np.sin(frame_count * 0.25 + bird.get("phase", 0)) * 8)
            cv2.line(canvas, (spx, spy), (spx+wing, spy+flap), color, 2)
            cv2.line(canvas, (spx+wing, spy+flap), (spx+wing*2, spy), color, 2)
            cv2.circle(canvas, (spx+wing, spy), 3 if kind != "hawk" else 4, color, -1)

    for sunbird in sunbirds or []:
        spx = int(sunbird["x"] - (ppx - screen_px))
        spy = int(sunbird["y"] - (ppy - screen_py))
        if -50 <= spx < WIDTH + 50 and -20 <= spy < HEIGHT:
            flap = int(np.sin(frame_count * 0.28 + sunbird.get("phase", 0)) * 10)
            cv2.circle(canvas, (spx+14, spy), 8, (40, 210, 255), -1)
            cv2.line(canvas, (spx+2, spy), (spx+14, spy+flap), (20, 170, 255), 3)
            cv2.line(canvas, (spx+14, spy+flap), (spx+30, spy), (20, 170, 255), 3)
            cv2.circle(canvas, (spx+18, spy-2), 2, (255,255,255), -1)

    for plane in planes or []:
        spx = int(plane["x"] - (ppx - screen_px))
        spy = int(plane["y"] - (ppy - screen_py))
        if -90 <= spx < WIDTH + 90 and -30 <= spy < HEIGHT:
            cv2.rectangle(canvas, (spx, spy), (spx+58, spy+12), (210, 210, 215), -1)
            cv2.rectangle(canvas, (spx+45, spy-8), (spx+57, spy+12), (160, 160, 170), -1)
            cv2.line(canvas, (spx+18, spy+6), (spx+5, spy+24), (190, 190, 200), 4)
            cv2.line(canvas, (spx+26, spy+6), (spx+45, spy+25), (190, 190, 200), 4)
            cv2.circle(canvas, (spx+9, spy+6), 3, (90, 180, 255), -1)
            cv2.putText(canvas, plane.get("banner", ""), (spx+8, spy+30), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1)

    for mob in mobs or []:
        spx = int(mob["x"] - (ppx - screen_px))
        spy = int(mob["y"] - (ppy - screen_py))
        if -TILE_SIZE * 2 <= spx < WIDTH + TILE_SIZE and -TILE_SIZE * 2 <= spy < HEIGHT + TILE_SIZE:
            mob_type = mob.get("type")
            if mob_type == "ancient_boss":
                pulse = int(np.sin(frame_count * 0.12 + mob.get("phase", 0)) * 5)
                body = (72, 48, 128)
                armor = (35, 70, 150)
                glow = (70, 220, 255)
                cv2.rectangle(canvas, (spx+2, spy+18), (spx+78, spy+84), body, -1)
                cv2.rectangle(canvas, (spx+14, spy+2), (spx+66, spy+30), body, -1)
                cv2.rectangle(canvas, (spx+10, spy+36), (spx+70, spy+62), armor, 2)
                cv2.circle(canvas, (spx+25, spy+16), 5, glow, -1)
                cv2.circle(canvas, (spx+55, spy+16), 5, glow, -1)
                cv2.line(canvas, (spx+12, spy+2), (spx+2, spy-13-pulse), (40, 40, 80), 4)
                cv2.line(canvas, (spx+68, spy+2), (spx+78, spy-13+pulse), (40, 40, 80), 4)
                cv2.rectangle(canvas, (spx-8, spy+40), (spx+8, spy+72), (45, 45, 95), -1)
                cv2.rectangle(canvas, (spx+72, spy+40), (spx+88, spy+72), (45, 45, 95), -1)
                cv2.rectangle(canvas, (spx+12, spy+84), (spx+30, spy+96), (35, 35, 75), -1)
                cv2.rectangle(canvas, (spx+50, spy+84), (spx+68, spy+96), (35, 35, 75), -1)
                max_hp = max(1, mob.get("max_hp", 120))
                hp_w = max(0, min(86, int(mob.get("hp", 0) / max_hp * 86)))
                cv2.rectangle(canvas, (spx-4, spy-22), (spx+90, spy-12), (15,15,20), -1)
                cv2.rectangle(canvas, (spx, spy-20), (spx+hp_w, spy-14), (40,40,220), -1)
                cv2.putText(canvas, "BOSS", (spx+18, spy-27), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80,220,255), 1)
                continue
            if mob_type == "skeleton":
                body = (210, 210, 210)
                detail = (60, 60, 60)
            elif mob_type == "slime":
                body = (60, 210, 80)
                if not mob.get("aggro", False):
                    body = tuple(max(0, int(c * 0.75)) for c in body)
                squish = int(np.sin(frame_count * 0.18 + mob.get("phase", 0)) * 3)
                cv2.rectangle(canvas, (spx+7, spy+15+squish), (spx+33, spy+36), body, -1)
                cv2.circle(canvas, (spx+16, spy+24), 2, (0,0,0), -1)
                cv2.circle(canvas, (spx+25, spy+24), 2, (0,0,0), -1)
                cv2.rectangle(canvas, (spx+8, spy-5), (spx+32, spy-2), (20,20,20), -1)
                cv2.rectangle(canvas, (spx+8, spy-5), (spx+8+max(0, min(24, int(mob.get("hp", 0) / 9 * 24))), spy-2), (60,60,220), -1)
                continue
            elif mob_type == "green_jet":
                flame = int(np.sin(frame_count * 0.3 + mob.get("phase", 0)) * 4)
                body = (70, 230, 70) if mob.get("aggro", False) else (45, 150, 45)
                cv2.circle(canvas, (spx+20, spy+18), 13, body, -1)
                cv2.rectangle(canvas, (spx+13, spy+27), (spx+27, spy+35), (40, 120, 40), -1)
                cv2.line(canvas, (spx+15, spy+35), (spx+11, spy+43+flame), (20, 120, 255), 3)
                cv2.line(canvas, (spx+25, spy+35), (spx+29, spy+43-flame), (20, 120, 255), 3)
                cv2.circle(canvas, (spx+15, spy+16), 2, (0,0,0), -1)
                cv2.circle(canvas, (spx+25, spy+16), 2, (0,0,0), -1)
                cv2.rectangle(canvas, (spx+8, spy-5), (spx+32, spy-2), (20,20,20), -1)
                cv2.rectangle(canvas, (spx+8, spy-5), (spx+8+max(0, min(24, int(mob.get("hp", 0) / 8 * 24))), spy-2), (60,60,220), -1)
                continue
            elif mob_type == "crystal_wisp":
                glow = int(30 + 20 * np.sin(frame_count * 0.18 + mob.get("phase", 0)))
                body = (230, 220, 120) if mob.get("aggro", False) else (180, 170, 95)
                cv2.circle(canvas, (spx+20, spy+20), 14, (body[0]//2, body[1]//2, min(255, body[2]+glow)), 1)
                pts = np.array([[spx+20, spy+4], [spx+32, spy+20], [spx+20, spy+36], [spx+8, spy+20]], np.int32)
                cv2.fillConvexPoly(canvas, pts, body)
                cv2.circle(canvas, (spx+16, spy+19), 2, (255,255,255), -1)
                cv2.circle(canvas, (spx+24, spy+19), 2, (255,255,255), -1)
                cv2.rectangle(canvas, (spx+8, spy-5), (spx+32, spy-2), (20,20,20), -1)
                cv2.rectangle(canvas, (spx+8, spy-5), (spx+8+max(0, min(24, int(mob.get("hp", 0) / 9 * 24))), spy-2), (60,60,220), -1)
                continue
            elif mob_type == "cave_spider":
                body = (55, 45, 95)
                detail = (20, 20, 35)
                cv2.ellipse(canvas, (spx+20, spy+24), (16, 10), 0, 0, 360, body, -1)
                for lx in (6, 13, 26, 33):
                    cv2.line(canvas, (spx+20, spy+24), (spx+lx, spy+36), detail, 2)
                cv2.circle(canvas, (spx+16, spy+22), 2, (0,0,255), -1)
                cv2.circle(canvas, (spx+24, spy+22), 2, (0,0,255), -1)
                hp_w = max(0, min(24, int(mob.get("hp", 0) / 14 * 24)))
                cv2.rectangle(canvas, (spx+8, spy-5), (spx+32, spy-2), (20,20,20), -1)
                cv2.rectangle(canvas, (spx+8, spy-5), (spx+8+hp_w, spy-2), (60,60,220), -1)
                continue
            elif mob_type == "cave_zombie":
                body = (45, 110, 130)
                detail = (20, 60, 70)
            else:
                body = (60, 160, 70)
                detail = (30, 80, 40)
            if not mob.get("aggro", False):
                body = tuple(max(0, int(c * 0.75)) for c in body)
            cv2.rectangle(canvas, (spx+9, spy+8), (spx+31, spy+36), body, -1)
            cv2.rectangle(canvas, (spx+12, spy+2), (spx+28, spy+14), body, -1)
            cv2.circle(canvas, (spx+16, spy+8), 2, (0,0,0), -1)
            cv2.circle(canvas, (spx+24, spy+8), 2, (0,0,0), -1)
            cv2.rectangle(canvas, (spx+8, spy+36), (spx+17, spy+40), detail, -1)
            cv2.rectangle(canvas, (spx+23, spy+36), (spx+32, spy+40), detail, -1)
            hp_w = max(0, min(24, int(mob.get("hp", 0) / 12 * 24)))
            cv2.rectangle(canvas, (spx+8, spy-5), (spx+32, spy-2), (20,20,20), -1)
            cv2.rectangle(canvas, (spx+8, spy-5), (spx+8+hp_w, spy-2), (60,60,220), -1)

    for npc in npcs or []:
        spx = int(npc["x"] - (ppx - screen_px))
        spy = int(npc["y"] - (ppy - screen_py))
        if -TILE_SIZE <= spx < WIDTH and -TILE_SIZE <= spy < HEIGHT:
            wave = int(np.sin(npc.get("wave", 0)) * 4)
            job = npc.get("job", "wanderer")
            cloth = {
                "builder": (80, 120, 190),
                "miner": (85, 85, 120),
                "merchant": (160, 80, 170),
                "trader": (170, 105, 175),
                "guard": (110, 130, 135),
                "wanderer": (90, 145, 120),
            }.get(job, (80, 120, 190))
            label = {"builder": "Build", "miner": "Mine", "merchant": "Shop", "trader": "Trade", "guard": "Guard", "wanderer": "Walk"}.get(job, "NPC")
            cv2.rectangle(canvas, (spx+10, spy+12), (spx+30, spy+36), cloth, -1)
            cv2.circle(canvas, (spx+20, spy+8), 8, (120, 170, 220), -1)
            cv2.circle(canvas, (spx+17, spy+7), 2, (0,0,0), -1)
            cv2.circle(canvas, (spx+23, spy+7), 2, (0,0,0), -1)
            cv2.line(canvas, (spx+10, spy+18), (spx+3, spy+24+wave), (70, 90, 150), 3)
            cv2.line(canvas, (spx+30, spy+18), (spx+38, spy+24-wave), (70, 90, 150), 3)
            if job == "miner":
                cv2.line(canvas, (spx+12, spy+17), (spx+28, spy+28), (150, 150, 150), 2)
            elif job == "guard":
                cv2.rectangle(canvas, (spx+28, spy+18), (spx+36, spy+31), (150, 150, 150), 1)
            elif job in ("merchant", "trader"):
                cv2.rectangle(canvas, (spx+12, spy+25), (spx+29, spy+31), (30, 190, 240), -1)
                cv2.circle(canvas, (spx+31, spy+25), 3, (70, 230, 255), -1)
            cv2.putText(canvas, label, (spx-2, spy-5), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,220), 1)

    for shot in projectiles or []:
        spx = int(shot["x"] - (ppx - screen_px))
        spy = int(shot["y"] - (ppy - screen_py))
        if 0 <= spx < WIDTH and 0 <= spy < HEIGHT:
            cv2.circle(canvas, (spx, spy), 4, (40, 240, 255), -1)
            cv2.circle(canvas, (spx, spy), 7, (20, 120, 180), 1)

    if is_swimming:
        direction = 1 if facing_right else -1
        body_y = screen_py + 18
        kick = int(np.sin(frame_count * 0.25) * 5)
        cv2.rectangle(canvas, (center_x-18, body_y-6), (center_x+12, body_y+8), (144, 175, 221), -1)
        cv2.circle(canvas, (center_x + direction * 18, body_y - 1), 8, (144, 175, 221), -1)
        cv2.rectangle(canvas, (center_x-20, body_y+8+kick), (center_x-2, body_y+14+kick), (156, 70, 52), -1)
        cv2.rectangle(canvas, (center_x-15, body_y+8-kick), (center_x+3, body_y+14-kick), (156, 70, 52), -1)
        cv2.circle(canvas, (center_x + direction * 21, body_y - 3), 2, (0,0,0), -1)
    else:
        cv2.rectangle(canvas, (center_x-10, screen_py+4), (center_x+10, screen_py+20), (144, 175, 221), -1) 
        cv2.rectangle(canvas, (center_x-8, screen_py+20), (center_x+8, screen_py+34), (175, 166, 0), -1)    
        leg_offset = int(np.sin(frame_count * 0.1) * 6) if (abs(vel_x) > 0.5 and is_grounded) else 0
        cv2.rectangle(canvas, (center_x-8, screen_py+34), (center_x-2+leg_offset, screen_py+40), (156, 70, 52), -1) 
        cv2.rectangle(canvas, (center_x+2, screen_py+34), (center_x+8-leg_offset, screen_py+40), (156, 70, 52), -1) 
        cv2.circle(canvas, (center_x + 3 if facing_right else center_x - 3, screen_py+10), 2, (0,0,0), -1)

    for p in particles[:]:
        spx = int(p[0] - (ppx - screen_px))
        spy = int(p[1] - (ppy - screen_py))
        if 0 <= spx < WIDTH and 0 <= spy < HEIGHT: 
            cv2.rectangle(canvas, (spx, spy), (spx + p[6], spy + p[6]), p[5], -1)
            
    return canvas

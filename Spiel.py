import os
import sys
import subprocess
import pgzrun

# Globale Konstanten
WIDTH = 1200
HEIGHT = 780

# Charakter Konstantanten
MOVE_SPEED = 5
JUMP_SPEED = 20
WALK_ANIM_DELAY = 5
WALK_FRAMES = ["alienyellow_walk1.png", "alienyellow_walk2.png"]
GRAVITY = 0.8
MAX_FALL_SPEED = 15

# Startbutton Konstanten
START_BUTTON_TEXT = "Start"
RESTART_BUTTON_TEXT = "Neustart"
START_BUTTON_WIDTH = 240
START_BUTTON_HEIGHT = 70
START_BUTTON_X = WIDTH // 2
START_BUTTON_Y = HEIGHT // 2

game_started = False
is_dead = False
level_completed = False

# Tile-Konstanten
TILE_SIZE = 60

# Tile-IDs (0 = leer, 1 = Metallplattform, 2 = Hohlraum)
TILE_IMAGES = {
    0: None,  # Leer
    1: "metalCenter.png",
}

# Bilder vorher laden und skalieren (Caching)
tile_sprites = {}
import pygame
for tile_id, image_name in TILE_IMAGES.items():
    if image_name:
        try:
            img = pygame.image.load(f"Images/{image_name}")
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            tile_sprites[tile_id] = img
        except Exception:
            pass

# Map-Layout (0 = leer, 1 = Plattform, etc.)
tilemap = [
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1],
    [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1],
]


def draw_tilemap():
    """Zeichne alle Tiles der Map"""
    for row, tiles in enumerate(tilemap):
        for col, tile_id in enumerate(tiles):
            if tile_id and tile_id in tile_sprites:
                x = col * TILE_SIZE - camera_x
                y = row * TILE_SIZE - camera_y
                screen.surface.blit(tile_sprites[tile_id], (x, y))


def get_tile_rect(row, col):
    return Rect((col * TILE_SIZE, row * TILE_SIZE), (TILE_SIZE, TILE_SIZE))


def get_solid_tiles(actor):
    left_col = int(actor.left // TILE_SIZE)
    right_col = int((actor.right - 1) // TILE_SIZE)
    top_row = int(actor.top // TILE_SIZE)
    bottom_row = int((actor.bottom - 1) // TILE_SIZE)
    tiles = []
    for row in range(max(0, top_row), min(len(tilemap), bottom_row + 1)):
        for col in range(max(0, left_col), min(len(tilemap[row]), right_col + 1)):
            if tilemap[row][col] > 0:
                tiles.append((row, col))
    return tiles


def resolve_horizontal_collisions(dx):
    if dx == 0:
        return
    for row, col in get_solid_tiles(charakter):
        tile_rect = get_tile_rect(row, col)
        if dx > 0 and charakter.right > tile_rect.left and charakter.left < tile_rect.left:
            charakter.right = tile_rect.left
        elif dx < 0 and charakter.left < tile_rect.right and charakter.right > tile_rect.right:
            charakter.left = tile_rect.right


def is_on_ground():
    if charakter.bottom >= HEIGHT:
        return True
    foot_row = int(charakter.bottom // TILE_SIZE)
    if foot_row >= len(tilemap):
        return False
    left_col = int(charakter.left // TILE_SIZE)
    right_col = int((charakter.right - 1) // TILE_SIZE)
    for col in range(max(0, left_col), min(len(tilemap[0]), right_col + 1)):
        if tilemap[foot_row][col] > 0:
            tile_top = foot_row * TILE_SIZE
            if charakter.bottom >= tile_top - 1 and charakter.bottom <= tile_top + 2:
                return True
    return False


def resolve_vertical_collisions():
    for row, col in get_solid_tiles(charakter):
        tile_rect = get_tile_rect(row, col)
        if charakter.vy > 0 and charakter.bottom > tile_rect.top and charakter.top < tile_rect.top:
            # Landen auf dem Tile
            charakter.bottom = tile_rect.top
            charakter.vy = 0
        elif charakter.vy < 0 and charakter.top < tile_rect.bottom and charakter.bottom > tile_rect.bottom:
            # Kopf trifft ein Tile: abprallen
            charakter.top = tile_rect.bottom
            charakter.vy = -charakter.vy * 0.4


# Charakter
charakter = Actor("alienyellow_stand.png", anchor=("center", "bottom"))
charakter.midbottom = (200, 100)
charakter.walk_frame = 0
charakter.walk_tick = 0

def draw():
    screen.fill("black")

    # Zeichne Startbutton, wenn das Spiel noch nicht gestartet ist
    if not game_started:
        button_left = START_BUTTON_X - START_BUTTON_WIDTH // 2
        button_top = START_BUTTON_Y - START_BUTTON_HEIGHT // 2
        button_rect = Rect((button_left, button_top), (START_BUTTON_WIDTH, START_BUTTON_HEIGHT))
        screen.draw.filled_rect(button_rect, "darkblue")
        screen.draw.text(START_BUTTON_TEXT, center=(START_BUTTON_X, START_BUTTON_Y), fontsize=48, color="white")
        screen.draw.text("Drücke R, um zu starten", center=(WIDTH // 2, START_BUTTON_Y - 90), fontsize=32, color="white")
        return

    if is_dead:
        screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 2 - 120), fontsize=72, color="red")
        screen.draw.text("Du bist gefallen. Drücke R zum Neustart", center=(WIDTH // 2, HEIGHT // 2 - 40), fontsize=36, color="white")
        button_left = START_BUTTON_X - START_BUTTON_WIDTH // 2
        button_top = HEIGHT // 2 + 40
        button_rect = Rect((button_left, button_top), (START_BUTTON_WIDTH, START_BUTTON_HEIGHT))
        screen.draw.filled_rect(button_rect, "darkred")
        screen.draw.text(RESTART_BUTTON_TEXT, center=(START_BUTTON_X, button_top + START_BUTTON_HEIGHT // 2), fontsize=48, color="white")
        return

    if level_completed:
        screen.draw.text("Level geschafft!", center=(WIDTH // 2, HEIGHT // 2 - 80), fontsize=72, color="yellow")
        screen.draw.text("Drücke F für neues Level", center=(WIDTH // 2, HEIGHT // 2 - 20), fontsize=36, color="white")
        return

    # Zeichne Karte und Charakter
    draw_tilemap()
    screen_x = charakter.x - camera_x
    screen_y = charakter.y - camera_y
    old_x, old_y = charakter.x, charakter.y
    charakter.x, charakter.y = screen_x, screen_y
    charakter.draw()
    charakter.x, charakter.y = old_x, old_y
    

charakter.vx = 0
charakter.vy = 0
def update():
    global is_dead, level_completed
    moving = False
    dx = 0

    # x-Geschwindigkeit berechnen (links/rechts)
    if keyboard.left:
        dx = -MOVE_SPEED
        moving = True
    elif keyboard.right:
        dx = MOVE_SPEED
        moving = True

    charakter.x += dx
    resolve_horizontal_collisions(dx)

    # Wechsel zwischen Stehen und Gehen
    if moving:
        charakter.walk_tick += 1
        if charakter.walk_tick >= WALK_ANIM_DELAY:
            charakter.walk_tick = 0
            charakter.walk_frame = 1 - charakter.walk_frame
        charakter.image = WALK_FRAMES[charakter.walk_frame]
    else:
        charakter.walk_frame = 0
        charakter.walk_tick = 0
        charakter.image = "alienyellow_stand.png"
    
    if not game_started or is_dead or level_completed:
        return

    # y-Geschwindigkeit berechnen (Springen und Schwerkraft)
    if keyboard.space and is_on_ground() and charakter.vy == 0:
        charakter.vy = -JUMP_SPEED
    charakter.vy += GRAVITY
    # Begrenze die Fallgeschwindigkeit
    if charakter.vy > MAX_FALL_SPEED:
        charakter.vy = MAX_FALL_SPEED
    charakter.y += charakter.vy
    resolve_vertical_collisions()

    # Kamera dem Spieler folgen lassen
    global camera_x, camera_y
    max_camera_x = max(0, len(tilemap[0]) * TILE_SIZE - WIDTH)
    max_camera_y = max(0, len(tilemap) * TILE_SIZE - HEIGHT)
    camera_x = max(0, min(int(charakter.x - WIDTH // 3), max_camera_x))
    camera_y = max(0, min(int(charakter.y - HEIGHT // 3), max_camera_y))

    # Verhindere, dass der Charakter unter den Boden fällt
    if charakter.bottom > HEIGHT:
        charakter.bottom = HEIGHT
        charakter.vy = 0
        is_dead = True

    # Wechsel in den Level-Fertig-Modus, wenn der Charakter das rechte Levelende erreicht
    if not is_dead and not level_completed and charakter.right >= len(tilemap[0]) * TILE_SIZE - 10:
        level_completed = True


def reset_game():
    global is_dead, game_started, camera_x, camera_y
    is_dead = False
    game_started = True
    charakter.midbottom = (200, 100)
    charakter.vx = 0
    charakter.vy = 0
    charakter.walk_frame = 0
    charakter.walk_tick = 0
    charakter.image = "alienyellow_stand.png"
    camera_x = 0
    camera_y = 0


def on_key_down(key):
    global game_started, is_dead, level_completed
    if key == keys.R:
        if not game_started or is_dead:
            reset_game()
    elif key == keys.F and level_completed:
        start_next_level()


def on_mouse_down(pos):
    global game_started, is_dead
    button_left = START_BUTTON_X - START_BUTTON_WIDTH // 2
    button_right = START_BUTTON_X + START_BUTTON_WIDTH // 2
    if not game_started and not is_dead:
        button_top = START_BUTTON_Y - START_BUTTON_HEIGHT // 2
        button_bottom = START_BUTTON_Y + START_BUTTON_HEIGHT // 2
        if button_left <= pos[0] <= button_right and button_top <= pos[1] <= button_bottom:
            game_started = True
        return

    if is_dead:
        button_top = HEIGHT // 2 + 40
        button_bottom = button_top + START_BUTTON_HEIGHT
        if button_left <= pos[0] <= button_right and button_top <= pos[1] <= button_bottom:
            reset_game()

pgzrun.go()
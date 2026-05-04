import pgzrun

# Konstanten
WIDTH = 1200
HEIGHT = 800

MOVE_SPEED = 5
JUMP_SPEED = 20
WALK_ANIM_DELAY = 5
WALK_FRAMES = ["alienyellow_walk1.png", "alienyellow_walk2.png"]
GRAVITY = 0.8
MAX_FALL_SPEED = 15

# Charakter
charakter = Actor("alienyellow_stand.png", anchor=("center", "bottom"))
charakter.midbottom = (200, 100)
charakter.walk_frame = 0
charakter.walk_tick = 0

def draw():
    screen.fill("black")
    # Zeichne Charakter
    charakter.draw()
    

# Bewegungslogik

charakter.vx = 0
charakter.vy = 0
def update():
    moving = False

    # x-Geschwindigkeit berechnen (links/rechts)
    if keyboard.left:
        charakter.x -= MOVE_SPEED
        moving = True
    elif keyboard.right:
        charakter.x += MOVE_SPEED
        moving = True

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
    
    # y-Geschwindigkeit berechnen (Springen und Schwerkraft)
    if charakter.bottom >= HEIGHT and keyboard.space:
        charakter.vy = -JUMP_SPEED
    charakter.vy += GRAVITY
    # Begrenze die Fallgeschwindigkeit
    if charakter.vy > MAX_FALL_SPEED:
        charakter.vy = MAX_FALL_SPEED
    charakter.y += charakter.vy
    # Verhindere, dass der Charakter unter den Boden fällt
    if charakter.bottom > HEIGHT:
        charakter.bottom = HEIGHT
        charakter.vy = 0


pgzrun.go()
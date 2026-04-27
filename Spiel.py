import pgzrun

# Konstanten
WIDTH = 1200
HEIGHT = 800

MOVE_SPEED = 5
JUMP_SPEED = 20
WALK_ANIM_DELAY = 5
WALK_FRAMES = ["alienyellow_walk1.png", "alienyellow_walk2.png"]

# Charakter
charakter = Actor("alienyellow_stand.png", anchor=("center", "bottom"))
charakter.midbottom = (1200, 800)
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
    
    # y-Geschwindiigkeit berechnen (Springen und Schwerkraft)
    if charakter.on_ground and keyboard.space:
        charakter.vy = -JUMP_SPEED




pgzrun.go()
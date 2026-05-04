import pgzrun

# Globale Konstanten
WIDTH = 1200
HEIGHT = 800

# Charakter Konstanten
MOVE_SPEED = 5
JUMP_SPEED = 20
WALK_ANIM_DELAY = 5
WALK_FRAMES = ["alienyellow_walk1.png", "alienyellow_walk2.png"]
GRAVITY = 0.8
MAX_FALL_SPEED = 15

# Startbutton Konstanten
START_BUTTON_TEXT = "Start"
START_BUTTON_WIDTH = 240
START_BUTTON_HEIGHT = 70
START_BUTTON_X = WIDTH // 2
START_BUTTON_Y = HEIGHT // 2

game_started = False

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
        screen.draw.text("Klicke hier, um zu starten", center=(WIDTH // 2, START_BUTTON_Y - 90), fontsize=32, color="white")
        return

    # Zeichne Charakter
    charakter.draw()
    

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
    
    if not game_started:
        return

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


def on_mouse_down(pos):
    # Überprüfe, ob der Startbutton angeklickt wurde
    global game_started
    if game_started:
        return

    button_left = START_BUTTON_X - START_BUTTON_WIDTH // 2
    button_right = START_BUTTON_X + START_BUTTON_WIDTH // 2
    button_top = START_BUTTON_Y - START_BUTTON_HEIGHT // 2
    button_bottom = START_BUTTON_Y + START_BUTTON_HEIGHT // 2
    if button_left <= pos[0] <= button_right and button_top <= pos[1] <= button_bottom:
        game_started = True


pgzrun.go()
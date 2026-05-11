import pgzrun
import random

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

# Plattformkonstanten
PLATFORM_SPACING_X = 240
PLATFORM_Y_MIN = HEIGHT - 180
PLATFORM_Y_MAX = HEIGHT - 260
PLATFORM_AHEAD_MARGIN = 600

# Bat-Konstanten
BAT_COUNT = 5
BAT_SPEED_MIN = 2
BAT_SPEED_MAX = 4
BAT_RANGE = 160
BAT_HEIGHTS = [HEIGHT - 280, HEIGHT - 320, HEIGHT - 360, HEIGHT - 420]

# Startbutton Konstanten
START_BUTTON_TEXT = "Start"
START_BUTTON_WIDTH = 240
START_BUTTON_HEIGHT = 70
START_BUTTON_X = WIDTH // 2
START_BUTTON_Y = HEIGHT // 2

# Weitere Konstanten
game_started = False
game_over = False
camera_x = 0
next_platform_x = 1200

# Hilfsfunktion zum Erstellen einer Plattform
def create_platform(x, y):
    plat = Actor("metalplatform.png", anchor=("center", "bottom"))
    plat.midbottom = (x, y)
    return plat

# Startplattform
start_platform = create_platform(200, HEIGHT)

# Charakter
charakter = Actor("alienyellow_stand.png", anchor=("center", "bottom"))
charakter.midbottom = (200, start_platform.top)
charakter.walk_frame = 0
charakter.walk_tick = 0

# Metallplattformen
metalplatforms = [
    start_platform,
    create_platform(150, HEIGHT),
    create_platform(330, HEIGHT),
    create_platform(530, HEIGHT),
    create_platform(760, HEIGHT - 180),
    create_platform(980, HEIGHT),
    create_platform(1180, HEIGHT - 140),
    create_platform(1400, HEIGHT - 200),
]

# Fledermäuse
bats = []

def create_bat(x, y, speed):
    bat = Actor("bat_fly.png", anchor=("center", "center"))
    bat.x = x
    bat.y = y
    bat.vx = speed
    bat.left_bound = x - BAT_RANGE
    bat.right_bound = x + BAT_RANGE
    return bat

for i in range(BAT_COUNT):
    x = 600 + i * 280 + random.randint(-80, 80)
    y = random.choice(BAT_HEIGHTS)
    speed = random.choice([-BAT_SPEED_MIN, BAT_SPEED_MIN, -BAT_SPEED_MAX, BAT_SPEED_MAX])
    bats.append(create_bat(x, y, speed))

# Plattformen nachladen, wenn die Kamera nach rechts wandert
def spawn_platforms():
    global next_platform_x
    while next_platform_x < camera_x + WIDTH + PLATFORM_AHEAD_MARGIN:
        y = random.choice([HEIGHT, HEIGHT - 140, HEIGHT - 180, HEIGHT - 220])
        spacing = random.randrange(170, 260)
        platform = create_platform(next_platform_x, y)
        metalplatforms.append(platform)
        next_platform_x += spacing

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

    # Zeichne Plattformen, Fledermäuse und Charakter mit Kamera-Offset
    for platform in metalplatforms:
        platform_screen_x = platform.x - camera_x
        if -100 < platform_screen_x < WIDTH + 100:
            screen.blit(platform.image, (platform_screen_x - platform.width // 2, platform.y - platform.height))
    
    for bat in bats:
        bat_screen_x = bat.x - camera_x
        if -100 < bat_screen_x < WIDTH + 100:
            screen.blit(bat.image, (bat_screen_x - bat.width // 2, bat.y - bat.height // 2))
    
    charakter_screen_x = charakter.x - camera_x
    screen.blit(charakter.image, (charakter_screen_x - charakter.width // 2, charakter.y - charakter.height))

    if game_over:
        screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2), fontsize=80, color="red", owidth=2, ocolor="black")
        screen.draw.text("Drücke R, um neu zu starten", center=(WIDTH // 2, HEIGHT // 2 + 80), fontsize=40, color="white")
    

charakter.vx = 0
charakter.vy = 0
def update():
    global game_over, camera_x
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
    
    if not game_started or game_over:
        return

    # y-Geschwindigkeit berechnen (Springen und Schwerkraft)
    on_platform = any(
        charakter.right > platform.left and charakter.left < platform.right and charakter.bottom == platform.top
        for platform in metalplatforms
    )
    if (charakter.bottom >= HEIGHT or on_platform) and keyboard.space:
        charakter.vy = -JUMP_SPEED

    charakter.vy += GRAVITY
    # Begrenze die Fallgeschwindigkeit
    if charakter.vy > MAX_FALL_SPEED:
        charakter.vy = MAX_FALL_SPEED
    previous_bottom = charakter.bottom
    previous_top = charakter.top
    charakter.y += charakter.vy

    # Plattform-Unterseite blockiert den Sprung von unten
    if charakter.vy < 0:
        for platform in metalplatforms:
            if charakter.right > platform.left and charakter.left < platform.right:
                if previous_top >= platform.bottom >= charakter.top:
                    charakter.top = platform.bottom
                    charakter.vy = 0
                    break

    # Landung auf einer Metallplattform prüfen
    landing_top = None
    for platform in metalplatforms:
        if charakter.vy >= 0 and charakter.right > platform.left and charakter.left < platform.right:
            if previous_bottom <= platform.top <= charakter.bottom:
                if landing_top is None or platform.top < landing_top:
                    landing_top = platform.top
    if landing_top is not None:
        charakter.bottom = landing_top
        charakter.vy = 0

    # Verhindere, dass der Charakter unter den Boden fällt
    if charakter.bottom > HEIGHT:
        charakter.bottom = HEIGHT
        charakter.vy = 0

    # Game over, wenn der Charakter auf dem Boden auftrifft und nicht auf einer Plattform steht
    on_floor_platform = any(
        platform.top == HEIGHT and charakter.right > platform.left and charakter.left < platform.right
        for platform in metalplatforms
    )
    if charakter.bottom >= HEIGHT and not on_floor_platform:
        game_over = True
        charakter.image = "alienyellow_hurt.png"
        charakter.vy = 0

    # Kamera dem Charakter folgen lassen
    global camera_x
    camera_x = charakter.x - WIDTH // 3
    if camera_x < 0:
        camera_x = 0

    # Bat-Bewegung aktualisieren
    for bat in bats:
        bat.x += bat.vx
        if bat.x < bat.left_bound:
            bat.x = bat.left_bound
            bat.vx = -bat.vx
        elif bat.x > bat.right_bound:
            bat.x = bat.right_bound
            bat.vx = -bat.vx

    # Weitere Plattformen nachladen, damit beim Scrollen immer neue kommen
    spawn_platforms()


def on_mouse_down(pos):
    # Überprüfe, ob der Startbutton angeklickt wurde
    global game_started, game_over
    if game_started or game_over:
        return

    button_left = START_BUTTON_X - START_BUTTON_WIDTH // 2
    button_right = START_BUTTON_X + START_BUTTON_WIDTH // 2
    button_top = START_BUTTON_Y - START_BUTTON_HEIGHT // 2
    button_bottom = START_BUTTON_Y + START_BUTTON_HEIGHT // 2
    if button_left <= pos[0] <= button_right and button_top <= pos[1] <= button_bottom:
        game_started = True

# Neustart bei Game Over
def on_key_down(key):
    global game_started, game_over
    if key == keys.R and game_over:
        game_over = False
        game_started = False
        charakter.image = "alienyellow_stand.png"
        charakter.midbottom = (200, 100)
        charakter.vx = 0
        charakter.vy = 0

pgzrun.go()
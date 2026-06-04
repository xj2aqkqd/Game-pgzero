import pygame
import random

# Globale Konstantanten
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
BAT_COUNT = 10
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
game_won = False
camera_x = 0
next_platform_x = 1200

background_image = None
try:
    bg = pygame.image.load("Images/weltraum.jpg")
    background_image = pygame.transform.scale(bg, (WIDTH, HEIGHT))
except Exception:
    background_image = None

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
    create_platform(1700, HEIGHT - 160),
]

goal_platform = create_platform(2500, HEIGHT - 140)
metalplatforms.append(goal_platform)

 # Zielelement   
goal = Actor("alienblue.png", anchor=("center", "bottom"))
goal.x = goal_platform.x
goal.bottom = goal_platform.top

# Fledermäuse
bats = []
# Funktion zum Erstellen einer Fledermaus
def create_bat(x, y, speed):
    bat = Actor("bat_fly.png", anchor=("center", "center"))
    bat.x = x
    bat.y = y
    bat.vx = speed
    bat.left_bound = x - BAT_RANGE
    bat.right_bound = x + BAT_RANGE
    return bat
# Fledermäuse zufällig im Level verteilen
if BAT_COUNT > 1:
    level_start = 600
    level_end = 5000
    step = (level_end - level_start) / (BAT_COUNT - 1)
    for i in range(BAT_COUNT):
        x = int(level_start + i * step + random.randint(-40, 40))
        y = random.choice(BAT_HEIGHTS)
        speed = random.choice([-BAT_SPEED_MIN, BAT_SPEED_MIN, -BAT_SPEED_MAX, BAT_SPEED_MAX])
        bats.append(create_bat(x, y, speed))
else:
    x = 1200
    y = random.choice(BAT_HEIGHTS)
    speed = random.choice([-BAT_SPEED_MIN, BAT_SPEED_MIN, -BAT_SPEED_MAX, BAT_SPEED_MAX])
    bats.append(create_bat(x, y, speed))

# Plattformen nachladen, wenn die Kamera nach rechts wandert
def platforms_overlap(p1, p2):
    if p1.right <= p2.left or p1.left >= p2.right:
        return False
    return abs(p1.top - p2.top) < 100


def bat_collides_with_platform(bat, next_x, next_y):
    bat_rect = Rect((next_x - bat.width // 2, next_y - bat.height // 2), (bat.width, bat.height))
    for platform in metalplatforms:
        platform_rect = Rect((platform.left, platform.top), (platform.width, platform.height))
        if bat_rect.colliderect(platform_rect):
            return True
    return False


def unstick_bat(bat):
    if not bat_collides_with_platform(bat, bat.x, bat.y):
        return
    for offset in range(1, 101):
        for candidate in (bat.x + offset, bat.x - offset):
            if bat.left_bound <= candidate <= bat.right_bound and not bat_collides_with_platform(bat, candidate, bat.y):
                bat.x = candidate
                return
    for offset in range(1, 51):
        new_y = bat.y - offset
        if new_y >= 0 and not bat_collides_with_platform(bat, bat.x, new_y):
            bat.y = new_y
            return


def spawn_platforms():
    global next_platform_x
    while next_platform_x < camera_x + WIDTH + PLATFORM_AHEAD_MARGIN:
        spacing = random.randrange(220, 320)
        next_platform_x += spacing
        y_choices = [HEIGHT, HEIGHT - 140, HEIGHT - 180, HEIGHT - 220]
        random.shuffle(y_choices)
        placed = False
        for y in y_choices:
            platform = create_platform(next_platform_x, y)
            if not any(platforms_overlap(platform, existing) for existing in metalplatforms):
                metalplatforms.append(platform)
                placed = True
                break
        if not placed:
            # Falls alle möglichen Höhen knapp sind, setze auf den Boden
            metalplatforms.append(create_platform(next_platform_x, HEIGHT))


def draw():
    if background_image:
        screen.surface.blit(background_image, (0, 0))
    else:
        screen.blit("weltraum.jpg", (0, 0))

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

    goal_screen_x = goal.x - camera_x
    if -100 < goal_screen_x < WIDTH + 100:
        screen.blit(goal.image, (goal_screen_x - goal.width // 2, goal.y - goal.height))

        arrow_tip = (goal_screen_x, goal.y - goal.height - 10)
        arrow_base = (goal_screen_x, goal.y - goal.height - 80)
        screen.draw.line(arrow_base, arrow_tip, "white")
        screen.draw.line((arrow_tip[0] - 10, arrow_tip[1] + 15), arrow_tip, "white")
        screen.draw.line((arrow_tip[0] + 10, arrow_tip[1] + 15), arrow_tip, "white")
        screen.draw.text(
            "Rette mich!",
            midtop=(goal_screen_x, arrow_base[1] - 40),
            fontsize=40,
            color="yellow",
            owidth=2,
            ocolor="black",
        )

    charakter_screen_x = charakter.x - camera_x
    screen.blit(charakter.image, (charakter_screen_x - charakter.width // 2, charakter.y - charakter.height))

    if game_won:
        screen.draw.text("You Win!", center=(WIDTH // 2, HEIGHT // 2), fontsize=80, color="yellow", owidth=2, ocolor="black")
        return

    if game_over:
        screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2), fontsize=80, color="red", owidth=2, ocolor="black")
        screen.draw.text("Drücke R, um neu zu starten", center=(WIDTH // 2, HEIGHT // 2 + 80), fontsize=40, color="white")
    

charakter.vx = 0
charakter.vy = 0
def update():
    global game_over, game_won, camera_x
    if not game_started or game_over or game_won:
        return

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
    
    if not game_started or game_over or game_won:
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

    if any(charakter.colliderect(bat) for bat in bats):
        game_over = True
        charakter.image = "alienyellow_hurt.png"
        charakter.vy = 0

    # Siegbedingung
    if charakter.colliderect(goal):
        game_won = True
        charakter.image = "alienyellow_stand.png"
        charakter.vy = 0

    # Kamera dem Charakter folgen lassen
    global camera_x
    camera_x = charakter.x - WIDTH // 3
    if camera_x < 0:
        camera_x = 0

    # Bat-Bewegung aktualisieren
    for bat in bats:
        next_x = bat.x + bat.vx
        if bat_collides_with_platform(bat, next_x, bat.y):
            bat.vx = -bat.vx
            # Versuche, aus der Plattform hinauszurutschen
            step = 1 if bat.vx > 0 else -1
            candidate_x = bat.x + step
            while bat.left_bound <= candidate_x <= bat.right_bound and bat_collides_with_platform(bat, candidate_x, bat.y):
                candidate_x += step
            if bat.left_bound <= candidate_x <= bat.right_bound and not bat_collides_with_platform(bat, candidate_x, bat.y):
                bat.x = candidate_x
        else:
            bat.x = next_x

        if bat.x < bat.left_bound:
            bat.x = bat.left_bound
            bat.vx = -bat.vx
        elif bat.x > bat.right_bound:
            bat.x = bat.right_bound
            bat.vx = -bat.vx

        unstick_bat(bat)

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
    global game_started, game_over, game_won
    if key == keys.R and game_over:
        game_over = False
        game_started = False
        charakter.image = "alienyellow_stand.png"
        charakter.midbottom = (200, 100)
        charakter.vx = 0
        charakter.vy = 0

if __name__ == "__main__":
    pgzrun.go()
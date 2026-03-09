import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
run = True
fps = 60

# Load assets ONCE
Bg = pygame.image.load("Assets/Map_assets/Background.png")
Mg = pygame.image.load("Assets/Map_assets/Midground.png")
Fg = pygame.image.load("Assets/Map_assets/Frontground.png")

# Character frames (load once!)
player_static = pygame.image.load("Assets/Character/static.png")
player_R1 = pygame.image.load("Assets/Character/Right_1.png")
player_R2 = pygame.image.load("Assets/Character/Right_2.png")
player_L1 = pygame.image.load("Assets/Character/Left_1.png")
player_L2 = pygame.image.load("Assets/Character/Left_2.png")
NPC = pygame.image.load("Assets/Character/NPC.png")

running_speed = 400
normal_speed = 250

# World & player setup
world_width = 3840
floor_rect = pygame.Rect(0, 637, world_width, 720)
world_rect = pygame.Rect(0, 0, world_width, 637)
hitbox = player_static.get_rect(center=(world_rect.centerx, 360))  # use static size
player_position = pygame.Vector2(hitbox.center)
camera_x = 0

velocity = 0
gravity = 300  # m/s^2
height = player_static.get_height()

# Animation state
frame = 0
animation_speed = 0.15  # seconds per frame
last_frame_time = 0
facing_right = True  # default facing


# Solve the physics
def Physics(dt):
    global velocity
    velocity += gravity * dt
    player_position.y += velocity * dt
    if hitbox.bottom >= 637:
        player_position.y = 637
        velocity = 0
    return velocity


def move(keys, dt):
    global facing_right, hitbox
    direction = pygame.Vector2(0, 0)

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        direction.x -= 1
        facing_right = False
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        direction.x += 1
        facing_right = True

    speed = running_speed if keys[pygame.K_LSHIFT] else normal_speed

    if direction.length() > 0:
        direction.normalize_ip()
        player_position.x += direction.x * speed * dt

    # Clamp to world
    hitbox.centerx = player_position.x
    hitbox.centery = player_position.y
    hitbox.clamp_ip(world_rect)
    player_position.x = hitbox.centerx
    player_position.y = hitbox.centery

    return direction


def update_camera(dt):
    global camera_x
    target = player_position.x - 640
    lerp_speed = 8 * dt
    camera_x += (target - camera_x) * lerp_speed
    camera_x = max(0, min(camera_x, world_width - 1280))


def get_current_player_image(direction, current_time):
    global frame, last_frame_time

    if direction.length() == 0:
        return player_static

    # Walking animation
    if current_time - last_frame_time > animation_speed:
        frame = (frame + 1) % 2
        last_frame_time = current_time

    if facing_right:
        return [player_R1, player_R2][frame]
    else:
        return [player_L1, player_L2][frame]


# Main loop
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    dt = clock.tick(fps) / 1000.0
    current_time = pygame.time.get_ticks() / 1000.0

    direction = move(keys, dt)
    update_camera(dt)
    Physics(dt)

    # Draw layers
    screen.blit(Bg, (-camera_x * 0.2, 0))
    screen.blit(Mg, (-camera_x * 0.6, 0))

    # Draw player (camera relative)
    player_img = get_current_player_image(direction, current_time)
    player_draw_x = player_position.x - camera_x
    player_draw_y = (player_position.y - player_img.get_height() // 2) - 65
    screen.blit(player_img, (player_draw_x, player_draw_y))
    screen.blit(NPC, (-camera_x * 1.0, 490))

    screen.blit(Fg, (-camera_x * 1.0, 0))

    pygame.display.update()

pygame.quit()

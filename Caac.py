#Je code en anglais dit moi si tu comprends pas qlq chose Arnaud
import pygame
import random
import math
import time
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

CHEATS_ENABLED = False

pygame.mixer.init()
shoot_sound = pygame.mixer.Sound("audio/shoot.mp3")
tripleshoot_sound = pygame.mixer.Sound("audio/shoottriple.mp3")
scattershoot_sound = pygame.mixer.Sound("audio/scattershoot.mp3")

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Caac")
clock = pygame.time.Clock()



# Variables, couleur etc..
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BEIGE = (245, 245, 220)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

FLOOR_COLORS = [
    BROWN,  # marron
    (100, 100, 100),  # gris
    (0, 100, 100),  # Cyan
    (139, 0, 0),  # rouge
    (75, 0, 130),  # violet
    (25, 25, 25),  # gris fonce
]


ROOM_TYPES = ["normal", "treasure", "boss", "shop", "devil", "angel"]
ENEMY_TYPES = ["fly", "spider", "pooter", "charger"]

fly_sprites = []
boss_sprites = []
pooter_sprites = []
spider_sprites = []
obstacle_sprites = []
charger_sprites = []
isaac_sprites = {
    "idle": {
        "up": [],
        "down": [],
        "left": [],
        "right": []
    },
    "walk": {
        "up": [],
        "down": [],
        "left": [],
        "right": []
    }
}

# Load sprites with error handling
def load_sprite_frames(base_name, directions, frame_count):
    frames = {}
    for direction in directions:
        frames[direction] = []
        for i in range(frame_count):
            try:
                sprite_path = os.path.join(script_dir, "sprites", f"{base_name}_{direction}_{i}.png")
                sprite = pygame.image.load(sprite_path).convert_alpha()
                frames[direction].append(pygame.transform.scale(sprite, (80, 80)))
            except (FileNotFoundError, pygame.error) as e:
                print(f"Error loading {base_name}_{direction}_{i}.png: {e}")
                # Fallback - create a colored rectangle so we can see missing sprites
                surf = pygame.Surface((50, 50), pygame.SRCALPHA)
                color = (255, 0, 255) if direction == "up" else \
                        (0, 255, 255) if direction == "down" else \
                        (255, 255, 0) if direction == "left" else \
                        (0, 255, 0)
                surf.fill(color)
                frames[direction].append(surf)
    return frames

# Load idle (1 frame per direction)
isaac_sprites["idle"] = load_sprite_frames("isaac_idle", ["up", "down", "left", "right"], 1)

# Load walk (3 frames per direction)
isaac_sprites["walk"] = load_sprite_frames("isaac_walk", ["up", "down", "left", "right"], 2)
sprite_path = os.path.join(script_dir, "sprites", "obstacle.png")
try:
    obstacle_sprites.append(pygame.image.load(sprite_path).convert_alpha())
except FileNotFoundError:
    print('Sprite pas trouvé')


for i in range(3): #fly_0.png, fly_1.png, fly_2.png et les autres
    sprite_path = os.path.join(script_dir, "sprites", f"fly_{i}.png")
    try:
        fly_sprites.append(pygame.image.load(sprite_path).convert_alpha())
    except FileNotFoundError:
        print(f"Sprite pas trouvé")
        fly_sprites.append(None)  # erreur qui ne devrait pas arriver

for i in range(1): #fly_0.png, fly_1.png, fly_2.png et les autres
    sprite_path = os.path.join(script_dir, "sprites", f"boss_{i}.png")
    try:
        boss_sprites.append(pygame.image.load(sprite_path).convert_alpha())
    except FileNotFoundError:
        print(f"Sprite pas trouvé")
        boss_sprites.append(None)  # erreur qui ne devrait pas arriver

for i in range(3): #fly_0.png, fly_1.png, fly_2.png et les autres
    sprite_path = os.path.join(script_dir, "sprites", f"charger_{i}.png")
    try:
        charger_sprites.append(pygame.image.load(sprite_path).convert_alpha())
    except FileNotFoundError:
        print(f"Sprite pas trouvé")
        charger_sprites.append(None)  # erreur qui ne devrait pas arriver

for i in range(3):
    sprite_path = os.path.join(script_dir, "sprites", f"pooter_{i}.png")
    try:
        pooter_sprites.append(pygame.image.load(sprite_path).convert_alpha())
    except FileNotFoundError:
        print(f"Sprite pas trouvé")
        pooter_sprites.append(None)  # erreur qui ne devrait pas arriver 

for i in range(3):
    sprite_path = os.path.join(script_dir, "sprites", f"spider_{i}.png")
    try:
        spider_sprites.append(pygame.image.load(sprite_path).convert_alpha())
    except FileNotFoundError:
        print(f"Sprite pas trouvé")
        pooter_sprites.append(None)  # erreur qui ne devrait pas arriver 

 
# Scale a 64 pixels
obstacle_sprites = [pygame.transform.scale(sprite, (64, 64)) for sprite in obstacle_sprites]
fly_sprites = [pygame.transform.scale(sprite, (54, 54)) for sprite in fly_sprites]
pooter_sprites = [pygame.transform.scale(sprite, (64, 64)) for sprite in pooter_sprites]
spider_sprites = [pygame.transform.scale(sprite, (48, 48)) for sprite in spider_sprites]
charger_sprites = [pygame.transform.scale(sprite, (64, 64)) for sprite in charger_sprites]
boss_sprites = [pygame.transform.scale(sprite, (172, 172)) for sprite in boss_sprites]


DEVIL_ITEMS = [
    ("pacte_sang", "Dégâts x2, -2 Coeurs"),
    ("abaddon", "Vitesse et Dégâts ++, -2 Coeurs"),
    ("pentagram", "Toutes Stats ++, -1 Coeur")
]

ANGEL_ITEMS = [
    ("ailes_sacrees", "Vol + Vitesse ++"),
    ("couronne_divine", "Aura Sacrée + Dégâts ++"),
    ("calice_sacre", "Régénération + Max HP ++"),
    ("aureole", "Triple Tir Sacré")
]

def start_screen():
    screen.fill(BLACK)
    font_large = pygame.font.SysFont("Arial", 64)
    font_small = pygame.font.SysFont("Arial", 32)

    title = font_large.render("Caac", True, RED)
    start_text = font_small.render("Appuyez sur ENTRÉE pour Commencer", True, WHITE)
    controls_text = font_small.render("Flèches pour Tirer, WASD pour Bouger", True, WHITE)
    controls_text = font_small.render("Espace pour esquiver", True, WHITE)

    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
    screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT//2 + 50))
    pygame.display.flip()

def game_over_screen(score):
    screen.fill(BLACK)
    font = pygame.font.SysFont("Arial", 64)
    font_small = pygame.font.SysFont("Arial", 32)
    game_over_text = font.render("PARTIE TERMINÉE", True, RED)
    restart_text = font_small.render("Appuyez sur ENTRÉE pour recommencer", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)

    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//3))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 100))
    pygame.display.flip()

class Isaac:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.size = 25
        self.health = 6  # 3 coeurs, 1 = un demi coeur
        self.max_health = 6
        self.damage = 5
        self.fire_rate = 0.7
        self.speed = 3
        self.tears = []
        self.shoot_delay = 15
        self.shoot_timer = 0
        self.coins = 0
        self.items = []
        self.invincibility_frames = 0
        self.invincibility_duration = 60  # 1 seconde a 60 FPS
        self.score = 0
        self.pickup_text = ""
        self.pickup_timer = 0
        self.triple_shot = False
        self.homing = False
        self.explosive = False
        self.scatter = False
        self.spectral = False
        self.laser = False
        self.flying = False
        self.holy_aura = False
        self.aura_damage = 1
        self.regen = False
        self.holy_triple = False
        self.laser_damage = 2
        self.regen_timer = 0
        self.laser_direction = (1, 0)
        self.shooting = False
        self.dx = 0
        self.dy = 0
        self.dash_cooldown = 0
        self.dash_duration = 10  # Frames
        self.is_dashing = False
        self.current_state = "idle"
        self.current_direction = "down"
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 10  # Higher = slower animation
        self.was_moving = False


    def draw(self):
        # Draw Isaac
        try:
            # Get current animation frames
            frames = isaac_sprites[self.current_state][self.current_direction]
            # Ensure current_frame is within bounds
            self.current_frame = min(self.current_frame, len(frames) - 1)
            sprite = frames[self.current_frame]
            
            # Draw the sprite
            if sprite:
                sprite_rect = sprite.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(sprite, sprite_rect)
                
        except Exception as e:
            print(f"Error drawing sprite: {e}")
            # Fallback drawing
            pygame.draw.circle(screen, (255, 0, 255), (int(self.x), int(self.y)), self.size)

        # Draw laser si actif et tire
        if self.laser and self.shooting:
            # Calcule position laser base sur la direction
            offset_distance = self.size + 10  # debut du laser un peu apres Isaac pour pas clip
            laser_start_x = self.x + self.laser_direction[0] * offset_distance
            laser_start_y = self.y + self.laser_direction[1] * offset_distance

            # Calculate fin du laser base sur la direction
            laser_end_x = self.x + self.laser_direction[0] * WIDTH
            laser_end_y = self.y + self.laser_direction[1] * HEIGHT

            laser_thickness = 20
            pygame.draw.line(screen, RED, (laser_start_x, laser_start_y), (laser_end_x, laser_end_y), laser_thickness)

        # Draw aura sacré
        if self.holy_aura:
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 100, 3)

        if self.invincibility_frames > 0 and self.invincibility_frames % 10 < 5:
            return  # Skip drawing pour creer effet de flash

        # Draw ailes
        if self.flying:
            pygame.draw.polygon(screen, WHITE, [(self.x - 20, self.y), (self.x - 30, self.y - 10), (self.x - 20, self.y - 20)])
            pygame.draw.polygon(screen, WHITE, [(self.x + 20, self.y), (self.x + 30, self.y - 10), (self.x + 20, self.y - 20)])

        # Draw coeurs
        for i in range(self.max_health // 2):
            if self.health >= (i + 1) * 2:
                pygame.draw.circle(screen, RED, (30 + i * 30, 30), 10)  # Full
            elif self.health >= i * 2 + 1:
                pygame.draw.arc(screen, RED, (20 + i * 30, 20, 20, 20), 0, math.pi, 2)  # Half

        # Draw pieces
        font = pygame.font.SysFont("Arial", 20)
        coin_text = font.render(f"{self.coins}$", True, YELLOW)
        screen.blit(coin_text, (WIDTH - 100, 30))

    def shoot(self, dx, dy, current_room):
        if self.laser:
            # Update laser direction que si tire
            if self.shooting:
                self.laser_direction = (dx, dy)
        elif not self.laser:
            # Normal tears ou triple tir
            if self.shoot_timer <= 0:
                tear_speed = 7 if not self.triple_shot else 4
                properties = {
                    'homing': self.homing,
                    'explosive': self.explosive,
                    'spectral': self.spectral,
                    'triple_shot': self.triple_shot
                }

                if self.holy_triple:
                    self.triple_shot = True

                # Triple tir
                if self.triple_shot:
                    pygame.mixer.Sound.play(tripleshoot_sound)
                    pygame.mixer.music.stop()
                    self.tears.append(Tear(self.x, self.y, dx * tear_speed, dy * tear_speed, self.damage, properties))

                    # Calculer angles pour les tears gauches droites
                    angle = math.atan2(dy, dx)
                    left_angle = angle - math.pi / 12  # 15 degrees a gauche
                    right_angle = angle + math.pi / 12  # pareil droit

                    # gauche tir
                    self.tears.append(Tear(
                        self.x, self.y,
                        tear_speed * math.cos(left_angle),
                        tear_speed * math.sin(left_angle),
                        self.damage, properties
                    ))

                    # droit tir
                    self.tears.append(Tear(
                        self.x, self.y,
                        tear_speed * math.cos(right_angle),
                        tear_speed * math.sin(right_angle),
                        self.damage, properties
                    ))
                else:
                    # Single tir
                    pygame.mixer.Sound.play(shoot_sound)
                    pygame.mixer.music.stop()
                    self.tears.append(Tear(self.x, self.y, dx * tear_speed, dy * tear_speed, self.damage, properties))

                # Eparpillement (jsp comment dire en francais)
                if self.scatter:
                    pygame.mixer.Sound.play(scattershoot_sound)
                    pygame.mixer.music.stop()
                    for _ in range(3):
                        scatter_angle = random.uniform(0, 2 * math.pi)
                        scatter_speed = tear_speed * 0.6
                        self.tears.append(Tear(
                            self.x, self.y,
                            scatter_speed * math.cos(scatter_angle),
                            scatter_speed * math.sin(scatter_angle),
                            self.damage * 0.5, properties
                        ))

                # Reset tir timer base sur la cadence des tirs
                self.shoot_timer = self.shoot_delay / self.fire_rate

    def update(self, current_room):
        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        keys = pygame.key.get_pressed()

        # Reset vitesse
        self.is_moving = (self.dx != 0 or self.dy != 0)
        
        # Update state
        is_moving = (abs(self.dx) > 0.1 or abs(self.dy) > 0.1)  # Small threshold

        # State transitions
        if is_moving:
            self.current_state = "walk"
            # Update direction based on primary movement axis
            if abs(self.dy) > abs(self.dx):  # Vertical movement dominant
                self.current_direction = "down" if self.dy > 0 else "up"
            else:  # Horizontal movement dominant
                self.current_direction = "right" if self.dx > 0 else "left"
        else:
            self.current_state = "idle"

        # Animation frame updates
        self.animation_timer += 1
        
        # Only change frames when appropriate
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            frames = isaac_sprites[self.current_state][self.current_direction]
            
            # For walk animation, cycle through frames
            if self.current_state == "walk":
                self.current_frame = (self.current_frame + 1) % len(frames)
            # For idle, stay on first frame (or cycle if you have multiple idle frames)
            else:
                self.current_frame = 0

        # Reset animation when state changes
        if is_moving != self.was_moving:
            self.current_frame = 0
            self.animation_timer = 0
            
        self.was_moving = is_moving
        

        # Update vitesse modifier pour clavier azerty
        if keys[pygame.K_a]: self.dx = -1
        if keys[pygame.K_d]: self.dx = 1
        if keys[pygame.K_w]: self.dy = -1
        if keys[pygame.K_s]: self.dy = 1
        # Normaliser vitesse diagonale
        if self.dx != 0 and self.dy != 0:
            self.dx *= 0.7071
            self.dy *= 0.7071

        # Dash
        if keys[pygame.K_SPACE] and self.dash_cooldown == 0:
            self.is_dashing = True
            self.dash_cooldown = 60  # 1 seconde

        if self.is_dashing:
            self.x += self.dx * 10
            self.y += self.dy * 10
            self.dash_duration -= 1
            if self.dash_duration <= 0:
                self.is_dashing = False
                self.dash_duration = 5  # Reset temps dash

        # Mouvements normaux
        if not self.is_dashing:
            self.x += self.dx * self.speed
            self.y += self.dy * self.speed


        # Update laser degats que si tir
        if self.laser and self.shooting:
            # Calculater laser fin baser sur la direction
            laser_end_x = self.x + self.laser_direction[0] * WIDTH
            laser_end_y = self.y + self.laser_direction[1] * HEIGHT

            for enemy in current_room.enemies[:]:
                # Check si l'ennemi est dans la zone
                if self.laser_direction[0] != 0:  # Horizontal laser
                    if abs(enemy.y - self.y) < 10:
                        if (self.laser_direction[0] > 0 and enemy.x > self.x) or (self.laser_direction[0] < 0 and enemy.x < self.x):
                            enemy.health -= self.laser_damage
                            if enemy.health <= 0:
                                current_room.enemies.remove(enemy)
                                self.score += 100
                elif self.laser_direction[1] != 0:  # Vertical laser
                    if abs(enemy.x - self.x) < 10:
                        if (self.laser_direction[1] > 0 and enemy.y > self.y) or (self.laser_direction[1] < 0 and enemy.y < self.y):
                            enemy.health -= self.laser_damage
                            if enemy.health <= 0:
                                current_room.enemies.remove(enemy)
                                self.score += 100

        # Update des autres trucs
        if self.holy_aura:
            for enemy in current_room.enemies[:]:
                if math.dist((self.x, self.y), (enemy.x, enemy.y)) < 100:  # radius de l'aura sacré
                    enemy.health -= self.aura_damage
                    if enemy.health <= 0:
                        current_room.enemies.remove(enemy)
                        self.score += 100

        if self.regen:
            self.regen_timer += 1
            if self.regen_timer >= 1000:  # Heal toutes les 3 secondes
                self.health = min(self.health + 1, self.max_health)
                self.regen_timer = 0

        # Update tirs
        for tear in self.tears[:]:
            tear.update(current_room)
            if tear.lifetime <= 0:
                self.tears.remove(tear)

    def point_line_distance(self, px, py, x1, y1, x2, y2):
        # Calculer distance entre point (px, py) et segment (x1, y1) to (x2, y2) NE PAS MODIFIER J'AI SAIGNER ICI
        numerator = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1)
        denominator = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
        return numerator / denominator

    def check_wall_collision(self, room):
        # Garde Isaac dans la room sauf pr les portes
        if self.x < room.x + self.size and not (HEIGHT//2 - 30 < self.y < HEIGHT//2 + 30):
            self.x = room.x + self.size
        elif self.x > room.x + room.width - self.size and not (HEIGHT//2 - 30 < self.y < HEIGHT//2 + 30):
            self.x = room.x + room.width - self.size

        if self.y < room.y + self.size and not (WIDTH//2 - 30 < self.x < WIDTH//2 + 30):
            self.y = room.y + self.size
        elif self.y > room.y + room.height - self.size and not (WIDTH//2 - 30 < self.x < WIDTH//2 + 30):
            self.y = room.y + room.height - self.size


def draw_stats(isaac):
    font = pygame.font.SysFont("Arial", 20)
    stats = [
        f"Damage: {isaac.damage}",
        f"Speed: {isaac.speed}",
        f"Fire Rate: {isaac.fire_rate}",
        f"Health: {isaac.health}/{isaac.max_health}",
        f"Coins: {isaac.coins}"
    ]
    for i, stat in enumerate(stats):
        text = font.render(stat, True, WHITE)
        screen.blit(text, (WIDTH - 200, 450 + i * 20))  # Affiche stats


class Particle:
    def __init__(self, x, y, color, size, dx, dy, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.dx = dx
        self.dy = dy
        self.lifetime = lifetime

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)  # Coupe entre temps
        return self.lifetime > 0

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class Tear:
    def __init__(self, x, y, dx, dy, damage, properties=None):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.size = 8
        self.lifetime = 60
        self.properties = properties or {}
        self.hit_enemies = set()

    def update(self, current_room):
        next_x = self.x + self.dx
        next_y = self.y + self.dy

        # Check mur collisions (sauf si tirs spectraux)
        if not self.properties.get('spectral'):
            if next_x < 50 or next_x > WIDTH - 50 or next_y < 50 or next_y > HEIGHT - 50:
                # Particules si mur touche
                for _ in range(10):
                    particle = Particle(
                        self.x, self.y,
                        color=BLUE,
                        size=random.randint(2, 5),
                        dx=random.uniform(-1, 1),
                        dy=random.uniform(-1, 1),
                        lifetime=random.randint(10, 20)
                    )
                    current_room.particles.append(particle)
                return True  # Signal pour enlever le tir

        if self.properties.get('homing') and current_room.enemies:
            closest = min(current_room.enemies, key=lambda e: math.dist((self.x, self.y), (e.x, e.y)))
            angle = math.atan2(closest.y - self.y, closest.x - self.x)
            homing_strength = 0.2 if self.properties.get('triple_shot') else 0.3
            self.dx += math.cos(angle) * homing_strength
            self.dy += math.sin(angle) * homing_strength

        self.x = next_x
        self.y = next_y
        self.lifetime -= 1
        return False


    def draw(self):
        color = BLUE
        if self.properties.get('explosive'): color = RED
        if self.properties.get('spectral'): color = (200, 200, 255, 128)

        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)


class Enemy:
    def __init__(self, enemy_type, x, y, health, floor_level=1):
        self.type = enemy_type
        self.x = x
        self.y = y
        self.health = health
        self.base_speed = 4 if enemy_type == "spider" else 2
        self.max_speed = 8  # Cap pour vitesse maximum
        self.speed = min(self.base_speed * 0.5 + (floor_level * 0.3), self.max_speed) if enemy_type == "boss" else self.base_speed
        self.projectiles = []
        self.shoot_cooldown = 120
        self.charge_cooldown = 180
        self.charge_timer = 0
        self.charging = False   
        self.sprites = fly_sprites 
        self.sprites0 = spider_sprites
        self.sprites1 = pooter_sprites
        self.sprites3 = charger_sprites 
        self.sprites4 = boss_sprites 
        self.current_frame = 0      # initial
        self.animation_speed = 7    # vitesse animation /!\ plus haut = moins vite
        self.frame_counter = 0      # compteur
        if enemy_type == "boss":
            self.shoot_delay = 320
            self.spawn_timer = 200
            self.spawn_cooldown = 200
        else:
            self.shoot_delay = 240
        self.size = 20 if enemy_type != "boss" else 30
        self.floor_level = floor_level

    def draw(self, screen):
        # tas de bla bla qui dessine les ennemies
        if self.type == "fly":
            if self.sprites[self.current_frame]: 
               screen.blit(self.sprites[self.current_frame], (self.x, self.y))
        elif self.type == "spider":
            if self.sprites0[self.current_frame]: 
                sprite_width, sprite_height = self.sprites0[self.current_frame].get_size()
                screen.blit(self.sprites0[self.current_frame], (self.x - sprite_width // 2, self.y - sprite_height // 2))
        elif self.type == "pooter":
            if self.sprites1[self.current_frame]: 
                sprite_width, sprite_height = self.sprites1[self.current_frame].get_size()
                screen.blit(self.sprites1[self.current_frame], (self.x - sprite_width // 2, self.y - sprite_height // 2))
        elif self.type == 'charger':
            if self.sprites3[self.current_frame]: 
                sprite_width, sprite_height = self.sprites3[self.current_frame].get_size()
                screen.blit(self.sprites3[self.current_frame], (self.x - sprite_width // 2, self.y - sprite_height // 2))
        if self.type == "boss":
            if self.sprites4[0]: 
                sprite_width, sprite_height = self.sprites4[0].get_size()
                screen.blit(self.sprites4[0], (self.x - sprite_width // 2, self.y - sprite_height // 2))
    def update(self):
        if self.type == "fly":
            self.frame_counter += 0.5
            if self.frame_counter >= self.animation_speed:
                self.frame_counter = 0
                self.current_frame = (self.current_frame + 1) % len(self.sprites)
        if self.type == "pooter":
            self.frame_counter += 0.10
            if self.frame_counter >= self.animation_speed:
                self.frame_counter = 0
                self.current_frame = (self.current_frame + 1) % len(self.sprites1)
        if self.type == "spider":
            self.frame_counter += 1
            if self.frame_counter >= self.animation_speed:
                self.frame_counter = 0
                self.current_frame = (self.current_frame + 1) % len(self.sprites0)
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1                                                                
            self.current_frame = (self.current_frame + 1) % len(self.sprites1)
        if self.type == 'charger':
            if self.charge_timer > 0:
                self.frame_counter = 0
                self.charge_timer -= 1
        if self.type == "boss":
            if len(self.sprites4) > 0:
                self.frame_counter += 1
                if self.frame_counter >= self.animation_speed:
                    self.frame_counter = 0
                    self.current_frame = (self.current_frame + 1) % len(self.sprites4)
            if self.spawn_timer > 0:
                self.spawn_timer -= 1

    def move_towards(self, target_x, target_y):
        # IA des ennemis pour venir a Isaac
        if self.type == "fly":
            angle = math.atan2(target_y - self.y, target_x - self.x)
            self.x += math.cos(angle + math.sin(time.time() * 2)) * self.speed
            self.y += math.sin(angle + math.sin(time.time() * 2)) * self.speed
        elif self.type == "spider":
            if random.randint(0, 100) < 5:  # 5% de changer de direction
                angle = math.atan2(target_y - self.y, target_x - self.x)
                self.x += math.cos(angle) * self.speed  * 5
                self.y += math.sin(angle) * self.speed * 5
        if self.type == "pooter":
            if self.shoot_cooldown <= 0:
                self.shoot(target_x, target_y)
                self.shoot_cooldown = self.shoot_delay
        if self.type == 'charger':
            if not self.charging and self.charge_timer <= 0:
                self.current_frame = 0
                if random.random() < 0.005:
                    self.current_frame = 1
                    self.charging = True
                    self.speed *= 3
                    self.charge_timer = 30

            if self.charging:
                self.current_frame = 2
                angle = math.atan2(target_y - self.y, target_x - self.x)
                self.x += math.cos(angle) * self.speed
                self.y += math.sin(angle) * self.speed
                if self.charge_timer <= 0:
                    self.charging = False
                    self.speed /= 3
        if self.type == "boss":
            angle = math.atan2(target_y - self.y, target_x - self.x)
            self.x += math.cos(angle + math.sin(time.time() * 2)) * self.speed
            self.y += math.sin(angle + math.sin(time.time() * 2)) * self.speed

    def check_collision(self, isaac):
        if math.dist((self.x, self.y), (isaac.x, isaac.y)) < self.size + isaac.size:
            if isaac.invincibility_frames <= 0:
                isaac.health -= 1
                isaac.invincibility_frames = isaac.invincibility_duration
                return True
            if isaac.health <=0:
                game_over = True
        return False

    def shoot(self, target_x, target_y):
        if self.type == "boss":
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                dx = math.cos(rad) * 5
                dy = math.sin(rad) * 5
                self.projectiles.append(Projectile(self.x, self.y, dx, dy))
        else:
            # Tirs ennemis normaux
            angle = math.atan2(target_y - self.y, target_x - self.x)
            dx = math.cos(angle) * 5
            dy = math.sin(angle) * 5
            self.projectiles.append(Projectile(self.x, self.y, dx, dy))

    def spawn_minion(self, current_room):
        if self.type == "boss" and self.spawn_timer <= 0:
            num_minions = min(self.floor_level, 4)  # Cap a 4 minions
            for _ in range(num_minions):
                enemy_type = random.choice(["fly", "spider"])
                x = self.x + random.randint(-100, 100)
                y = self.y + random.randint(-100, 100)
                current_room.enemies.append(Enemy(enemy_type, x, y, 10, self.floor_level))
            self.spawn_timer = 600  # Reset timer

class Projectile:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.size = 5

    def update(self):
        next_x = self.x + self.dx
        next_y = self.y + self.dy

        # Check mur collisions
        if next_x < 50 or next_x > WIDTH - 50 or next_y < 50 or next_y > HEIGHT - 50:
            return True  # Signal pr enlever tirs

        self.x = next_x
        self.y = next_y
        return False

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.size)


class Floor:
    def __init__(self, level):
        self.level = level
        self.rooms = {}
        self.room_count = random.randint(8, 12)
        self.current_position = (0, 0)
        self.boss_defeated = False
        self.visited_rooms = set()
        self.generate_floor()

    def generate_floor(self):
        # romm dans laquelle isaac spawn au debut du jeu et de chaque etage
        self.rooms[(0, 0)] = Room("start", self.level)
        self.visited_rooms.add((0, 0))

        # Genere ttes les positions
        positions = []
        for _ in range(self.room_count):
            if not positions:
                positions = self.get_valid_adjacent_positions()
            if positions:
                pos = positions.pop(0)
                self.rooms[pos] = Room("normal", self.level)

        # Replace les rooms normales avec les rooms speciales
        normal_positions = [(x, y) for (x, y) in self.rooms.keys() if (x, y) != (0, 0)]
        special_rooms = ["treasure", "shop", "boss"]

        # code pr faire en sorte que la room boos n'a pas de room en dessous la sienne pr les rooms anges et demon
        boss_placed = False
        while not boss_placed and normal_positions:
            pos = random.choice(normal_positions)
            x, y = pos
            if (x, y + 1) not in self.rooms:
                self.rooms[pos] = Room("boss", self.level)
                boss_placed = True
                normal_positions.remove(pos)

        # PLacer autres rooms o(treasure, shop)
        for room_type in ["treasure", "shop"]:
            if normal_positions:
                pos = random.choice(normal_positions)
                normal_positions.remove(pos)
                self.rooms[pos] = Room(room_type, self.level)

        # Update ttes les portes
        self.update_all_doors()

    # Je sais meme plus a force ca fait 5h je suis dessus j'en ai marre
    def get_valid_adjacent_positions(self):
        valid = []
        for room_pos in self.rooms.keys():
            for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
                new_pos = (room_pos[0] + dx, room_pos[1] + dy)
                if new_pos not in self.rooms:
                    valid.append(new_pos)
        return valid

    def update_all_doors(self):
        for pos, room in self.rooms.items():
            x, y = pos
            room.doors["top"] = (x, y-1) in self.rooms
            room.doors["bottom"] = (x, y+1) in self.rooms
            room.doors["left"] = (x-1, y) in self.rooms
            room.doors["right"] = (x+1, y) in self.rooms

class Room:
    def __init__(self, room_type="normal", floor_level=1):
        self.type = room_type
        self.width = WIDTH - 100
        self.height = HEIGHT - 100
        self.x = 50
        self.y = 50
        self.enemies = []
        self.particles = []
        self.doors = {"top": False, "bottom": False, "left": False, "right": False}
        self.cleared = room_type in ["start", "treasure"]
        self.items = []
        self.floor_level = floor_level
        self.obstacles = []
        self.size = 20
        self.spriteobstacle = obstacle_sprites
        if room_type == "normal":
            self.spawn_enemies(floor_level)
            self.spawn_obstacles()
        elif room_type == "boss":
            self.spawn_boss(floor_level)
            self.spawn_obstacles()
        elif room_type == "treasure":
            self.spawn_treasure()
        elif room_type == "shop":
            self.spawn_shop_items()


    def spawn_obstacles(self):
        num_obstacles = random.randint(1, 4)
        safe_radius = 100

        for _ in range(num_obstacles):
            while True:
                x = random.randint(self.x + 100, self.x + self.width - 100)
                y = random.randint(self.y + 100, self.y + self.height - 100)

                # Check si la position n'interfere pas avec le safe radius pr pas qu'on soit bloquer en gros
                center_safe = math.dist((x, y), (WIDTH//2, HEIGHT//2)) > safe_radius
                top_safe = math.dist((x, y), (WIDTH//2, 50)) > safe_radius
                bottom_safe = math.dist((x, y), (WIDTH//2, HEIGHT-50)) > safe_radius
                left_safe = math.dist((x, y), (50, HEIGHT//2)) > safe_radius
                right_safe = math.dist((x, y), (WIDTH-50, HEIGHT//2)) > safe_radius

                # Check distance des autres obstacles
                obstacles_safe = all(math.dist((x, y), (obs['x'], obs['y'])) > 100 for obs in self.obstacles)

                if center_safe and top_safe and bottom_safe and left_safe and right_safe and obstacles_safe:
                    self.obstacles.append({
                        'x': x,
                        'y': y,
                        'size': 40,
                        'health': 3
                    })
                    break


    def spawn_enemies(self, floor_level):
        num_enemies = random.randint(3, 5 + floor_level)
        enemy_health = 10 + (floor_level * 5)
        safe_radius = 150

        for _ in range(num_enemies):
            enemy_type = random.choice(ENEMY_TYPES)

            while True:
                x = random.randint(self.x + 50, self.x + self.width - 50)
                y = random.randint(self.y + 50, self.y + self.height - 50)

                # Check distance du centre ET des portes a peu pres pareil que obstacle
                center_safe = math.dist((x, y), (WIDTH//2, HEIGHT//2)) > safe_radius
                top_safe = math.dist((x, y), (WIDTH//2, 50)) > safe_radius
                bottom_safe = math.dist((x, y), (WIDTH//2, HEIGHT-50)) > safe_radius
                left_safe = math.dist((x, y), (50, HEIGHT//2)) > safe_radius
                right_safe = math.dist((x, y), (WIDTH-50, HEIGHT//2)) > safe_radius

                if center_safe and top_safe and bottom_safe and left_safe and right_safe:
                    self.enemies.append(Enemy(enemy_type, x, y, enemy_health))
                    break

    def spawn_boss(self, floor_level):
        boss_health = 100 + (floor_level * 25)  # Difficultéeeeeeeeeee!!!!!!
        self.enemies.append(Enemy("boss", WIDTH//2, HEIGHT//2, boss_health, self.floor_level))


    def spawn_treasure(self):
        self.items.append(random.choice([
            "degats_plus",
            "vie_plus",
            "tirs_plus",
            "vitesse_plus",
            "portee_plus",
            "taille_moins",
            "triple_tir",
            "tirs_guides",
            "tirs_explosifs",
            "tirs_disperses",
            "taille_geante",
            "tirs_spectraux",
        ]))

    def spawn_shop_items(self):
        self.shop_items = []
        self.shop_prices = []
        possible_items = [
            ("degats_plus", 15),
            ("vie_plus", 15),
            ("tirs_plus", 15),
            ("vitesse_plus", 10),
            ("portee_plus", 10),
            ("taille_moins", 20),
            ("triple_tir", 25),
            ("tirs_guides", 30),
            ("tirs_explosifs", 35),
            ("tirs_disperses", 30),
            ("taille_geante", 20),
            ("tirs_spectraux", 25)
        ]
            # Select 2 items aleatoires et leurs prix
        selected = random.sample(possible_items, 2)
        for item, price in selected:
            self.shop_items.append(item)
            self.shop_prices.append(price)

    def spawn_special_room(self, room_type):
        self.type = room_type
        self.items = []
        self.prices = []

        if room_type == "devil":
            selected = random.sample(DEVIL_ITEMS, 2)
            for item_info in selected:
                item, desc = item_info
                self.items.append(item)
                #prix correct selon l'objet
                if item == "pacte_sang":
                    self.prices.append(2)  # 2 cours (4 points de vie)
                elif item == "abaddon":
                    self.prices.append(2)
                elif item == "pentagram":
                    self.prices.append(1)
        elif room_type == "angel":
            selected = random.sample(ANGEL_ITEMS, 2)
            for item in selected:
                self.items.append(item[0])
                self.prices.append(0)  # GRATUITTTT

        # Pour etre sur qu'on puisse revenir a la room boss
        self.doors["top"] = True

    def draw(self):
        # Cycle les couleurs entre chaque etage en gros
        floor_color = FLOOR_COLORS[(self.floor_level - 1) % len(FLOOR_COLORS)]
        pygame.draw.rect(screen, floor_color, (self.x, self.y, self.width, self.height))

        for obstacle in self.obstacles:
            if self.spriteobstacle:  # Check if the list is not empty
                sprite_width, sprite_height = self.spriteobstacle[0].get_size()  # Access the first sprite
                screen.blit(self.spriteobstacle[0], (obstacle['x'] - sprite_width // 2, obstacle['y'] - sprite_height // 2))

        # Draw portes
        door_width = 60
        door_color = RED if self.enemies and self.type != "start" else BLACK
        if self.doors["top"]:
            pygame.draw.rect(screen, BLACK, (WIDTH//2 - door_width//2, self.y - 10, door_width, 20))
        if self.doors["bottom"]:
            pygame.draw.rect(screen, BLACK, (WIDTH//2 - door_width//2, self.y + self.height - 10, door_width, 20))
        if self.doors["left"]:
            pygame.draw.rect(screen, BLACK, (self.x - 10, HEIGHT//2 - door_width//2, 20, door_width))
        if self.doors["right"]:
            pygame.draw.rect(screen, BLACK, (self.x + self.width - 10, HEIGHT//2 - door_width//2, 20, door_width))

        # Draw items si c'est ds room ang / demon (qui lit mes commentaires meme lisez juste le nom de la fonction c'est pas complique...)
        if self.type in ["devil", "angel"] and self.items:
            for i, (item, price) in enumerate(zip(self.items, self.prices)):
                x = WIDTH//3 if i == 0 else 2 * WIDTH//3  # Positionner les items cote a cote
                y = HEIGHT//2

                # Draw tout le blabla nom item prix etc
                pygame.draw.circle(screen, YELLOW, (x, y), 15)

                font = pygame.font.SysFont("Arial", 20)
                item_text = font.render(item.replace("_", " ").title(), True, WHITE)
                screen.blit(item_text, (x - item_text.get_width()//2, y + 30))

                if self.type == "devil":
                    price_text = font.render(f"{price} <3", True, RED)
                    screen.blit(price_text, (x - price_text.get_width()//2, y + 50))

        # Draw la trapdoor qd le boss est tué
        if self.type == "boss" and not self.enemies:
            pygame.draw.rect(screen, BLACK, (WIDTH//2 - 30, HEIGHT//2 - 30, 60, 60))
            floor_color = FLOOR_COLORS[(self.floor_level - 1) % len(FLOOR_COLORS)]
            pygame.draw.circle(screen, floor_color, (WIDTH//2, HEIGHT//2), 10)
            font = pygame.font.SysFont("Arial", 20)
            text = font.render("Étage Suivant", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))

        # Draw items si c room treasure
        if self.type == "treasure" and self.items:
            pygame.draw.circle(screen, YELLOW, (WIDTH//2, HEIGHT//2), 15)

        # Draw items du shop
        if self.type == "shop" and self.shop_items:
            for i, (item, price) in enumerate(zip(self.shop_items, self.shop_prices)):
                x = WIDTH//3 if i == 0 else 2 * WIDTH//3
                pygame.draw.circle(screen, YELLOW, (x, HEIGHT//2), 15)
                # Draw prix
                font = pygame.font.SysFont("Arial", 20)
                price_text = font.render(f"{price}$", True, WHITE)
                screen.blit(price_text, (x - price_text.get_width()//2, HEIGHT//2 + 30))

        # Draw si c room treasure partie 2
        if self.type == "treasure" and self.items:
            pygame.draw.circle(screen, YELLOW, (WIDTH//2, HEIGHT//2), 15)
            # Draw nom item
            font = pygame.font.SysFont("Arial", 20)
            item_text = font.render(self.items[0].replace("_", " ").title(), True, WHITE)
            screen.blit(item_text, (WIDTH//2 - item_text.get_width()//2, HEIGHT//2 + 30))

        # Draw items du shop partie 2
        if self.type == "shop" and self.shop_items:
            for i, (item, price) in enumerate(zip(self.shop_items, self.shop_prices)):
                x = WIDTH//3 if i == 0 else 2 * WIDTH//3
                pygame.draw.circle(screen, YELLOW, (x, HEIGHT//2), 15)
                # Draw prix
                font = pygame.font.SysFont("Arial", 20)
                price_text = font.render(f"{price}$", True, WHITE)
                item_text = font.render(item.replace("_", " ").title(), True, WHITE)
                screen.blit(price_text, (x - price_text.get_width()//2, HEIGHT//2 + 30))
                screen.blit(item_text, (x - item_text.get_width()//2, HEIGHT//2 + 50))

        font = pygame.font.SysFont("Arial", 24)
        floor_text = font.render(f"Étage {self.floor_level}", True, WHITE)
        screen.blit(floor_text, (10, HEIGHT - 30))

class Game:
    def __init__(self):
        self.current_floor = 1
        self.floor = Floor(self.current_floor)
        self.cheats_enabled = False

    def change_room(self, direction, isaac):
        dx, dy = 0, 0
        if direction == "top": dy = -1
        elif direction == "bottom": dy = 1
        elif direction == "left": dx = -1
        elif direction == "right": dx = 1

        new_pos = (self.floor.current_position[0] + dx, self.floor.current_position[1] + dy)
        if new_pos in self.floor.rooms:
            self.floor.current_position = new_pos
            self.floor.visited_rooms.add(new_pos)
            if direction == "top": isaac.y = HEIGHT - 100
            elif direction == "bottom": isaac.y = 100
            elif direction == "left": isaac.x = WIDTH - 100
            elif direction == "right": isaac.x = 100

    def next_floor(self, isaac):
        self.current_floor += 1
        self.floor = Floor(self.current_floor)
        isaac.x = WIDTH // 2
        isaac.y = HEIGHT // 2
        isaac.health = min(isaac.health + 2, isaac.max_health)  # Heal 1 coeurs entre chaque etage car je suis gentil


    def draw_minimap(self):
        map_size = 10
        # Afficher toutes les salles visitées + adjacentes
        visible_positions = set()
        for pos in self.floor.visited_rooms:
            visible_positions.add(pos)
            # Ajouter les salles adjacentes
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                adjacent_pos = (pos[0] + dx, pos[1] + dy)
                if adjacent_pos in self.floor.rooms:
                    visible_positions.add(adjacent_pos)

        # Dessiner toutes les salles visibles
        for pos in visible_positions:
            room = self.floor.rooms.get(pos)
            if not room:
                continue

            x, y = pos
            map_x = WIDTH - 120 + (x * 15)
            map_y = 100 + (y * 15)

            # Couleur de base
            if pos == self.floor.current_position:
                color = WHITE
            elif pos in self.floor.visited_rooms:
                color = (50, 50, 50)  # Salle visitée
            else:
                color = (150, 150, 150)  # Salle non visitée mais adjacente

            pygame.draw.rect(screen, color, (map_x, map_y, map_size, map_size))

            # Dessiner les icônes spéciales même pour les salles non visitées
            if room.type in ["boss", "shop", "treasure", "devil", "angel"]:
                icon_color = color if pos in self.floor.visited_rooms else (150, 150, 150)  # Gris si non visitée

                if room.type == "boss":
                    pygame.draw.circle(screen, (190, 0, 0), (map_x + map_size//2, map_y + map_size//2), 3)
                elif room.type == "shop":
                    pygame.draw.circle(screen, (200, 200, 0), (map_x + map_size//2, map_y + map_size//2), 3)  # Jaune foncé
                elif room.type == "treasure":
                    pygame.draw.circle(screen, (0, 0, 200), (map_x + map_size//2, map_y + map_size//2), 3)  # Bleu foncé
                elif room.type == "devil":
                    pygame.draw.circle(screen, (100, 0, 100), (map_x + map_size//2, map_y + map_size//2), 3)  # Violet foncé
                elif room.type == "angel":
                    pygame.draw.circle(screen, (0, 0, 100), (map_x + map_size//2, map_y + map_size//2), 3)  # Bleu nuit


def main():
    # Start screen
    in_start_screen = True
    while in_start_screen:
        start_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    in_start_screen = False

    # reset jeu
    def reset_game():
        return Game(), Isaac()

    # debut jeu et setup isaac
    game, isaac = reset_game()
    running = True
    game_over = False

    while running:
        if game_over:
            game_over_screen(isaac.score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game, isaac = reset_game()
                        game_over = False
            continue

        # Clear screen
        screen.fill(BLACK)

        # Get room
        current_room = game.floor.rooms[game.floor.current_position]

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    global CHEATS_ENABLED
                    CHEATS_ENABLED = not CHEATS_ENABLED
                elif CHEATS_ENABLED:
                    if event.key == pygame.K_KP1 or event.key == pygame.K_1:
                        isaac.max_health += 1
                        isaac.health = isaac.max_health
                    if event.key == pygame.K_KP2 or event.key == pygame.K_2:
                        isaac.damage += 5
                    if event.key == pygame.K_KP3 or event.key == pygame.K_3:
                        isaac.coins += 50
                    if event.key == pygame.K_KP4 or event.key == pygame.K_4:
                        isaac.fire_rate += 1
                    if event.key == pygame.K_KP5 or event.key == pygame.K_5:
                        isaac.holy_aura = True
                    if event.key == pygame.K_KP6 or event.key == pygame.K_6:
                        isaac.triple_shot = True
                    if event.key == pygame.K_KP7 or event.key == pygame.K_7:
                        isaac.homing = True
                    if event.key == pygame.K_KP8 or event.key == pygame.K_8:
                        isaac.scattera = True
                    if event.key == pygame.K_KP9 or event.key == pygame.K_9:
                        isaac.spectral = True
                    if event.key == pygame.K_KP0 or event.key == pygame.K_0:
                        current_room.enemies.clear()

        # keybinds (a modifier pr les claviers azerty bande de losers)
        keys = pygame.key.get_pressed()

        # murs collisions
        isaac.check_wall_collision(current_room)

        # Update particules
        for particle in current_room.particles[:]:
            if not particle.update():
                current_room.particles.remove(particle)

        #draw particules
        for particle in current_room.particles:
            particle.draw()

        # TIR NE PAS MODIFIER
        isaac.shooting = False  # Reset tirs

        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            isaac.shooting = True  # Pas besoin de commentaire simple a comprendre

            if isaac.laser:
                # Update laser direction
                if keys[pygame.K_LEFT]: isaac.laser_direction = (-1, 0)
                if keys[pygame.K_RIGHT]: isaac.laser_direction = (1, 0)
                if keys[pygame.K_UP]: isaac.laser_direction = (0, -1)
                if keys[pygame.K_DOWN]: isaac.laser_direction = (0, 1)
            elif not isaac.laser:
                # Normal tirs
                if keys[pygame.K_LEFT]: isaac.shoot(-1, 0, current_room)
                if keys[pygame.K_RIGHT]: isaac.shoot(1, 0, current_room)
                if keys[pygame.K_UP]: isaac.shoot(0, -1, current_room)
                if keys[pygame.K_DOWN]: isaac.shoot(0, 1, current_room)

        # Collisions obstacles si isaac ne vole pas avec les ailes
        if not isaac.flying:
            for obstacle in current_room.obstacles:
                if math.dist((isaac.x, isaac.y), (obstacle['x'], obstacle['y'])) < isaac.size + obstacle['size'] // 2:
                    angle = math.atan2(isaac.y - obstacle['y'], isaac.x - obstacle['x'])
                    isaac.x = obstacle['x'] + math.cos(angle) * (isaac.size + obstacle['size'] // 2)
                    isaac.y = obstacle['y'] + math.sin(angle) * (isaac.size + obstacle['size'] // 2)

        # collisions tirs obstacles
        for tear in isaac.tears[:]:
            for obstacle in current_room.obstacles[:]:
                if math.dist((tear.x, tear.y), (obstacle['x'], obstacle['y'])) < tear.size + obstacle['size'] // 2:
                    if not tear.properties.get('spectral'):
                        isaac.tears.remove(tear)
                    obstacle['health'] -= 1
                    if obstacle['health'] <= 0:
                        current_room.obstacles.remove(obstacle)
                    break

        # Collisions tirs ennemis
        for enemy in current_room.enemies:
            if math.dist((enemy.x, enemy.y), (isaac.x, isaac.y)) < enemy.size + isaac.size:
                if isaac.invincibility_frames <= 0:
                    isaac.health -= 1
                    isaac.invincibility_frames = isaac.invincibility_duration
                    if isaac.health <= 0:
                        game_over = True
        # blabla treasure room
        if current_room.type == "treasure" and current_room.items:
            if math.dist((isaac.x, isaac.y), (WIDTH // 2, HEIGHT // 2)) < 30:
                item = current_room.items.pop()
                if item == "degats_plus":
                    isaac.damage += 2
                    isaac.pickup_text = "Dégâts Augmentés!"
                elif item == "vie_plus":
                    isaac.max_health += 2
                    isaac.health += 2
                    isaac.pickup_text = "Vie Augmentée!"
                elif item == "tirs_plus":
                    isaac.fire_rate += 0.2
                    isaac.pickup_text = "Cadence de Tir Augmentée!"
                elif item == "vitesse_plus":
                    isaac.speed += 1
                    isaac.pickup_text = "Vitesse Augmentée!"
                elif item == "portee_plus":
                    for tear in isaac.tears:
                        tear.lifetime += 20
                    isaac.pickup_text = "Portée Augmentée!"
                elif item == "taille_moins":
                    isaac.size = max(15, isaac.size - 5)
                    isaac.pickup_text = "Taille Réduite!"
                elif item == "triple_tir":
                    isaac.triple_shot = True
                    isaac.pickup_text = "Triple Tir!"
                elif item == "tirs_guides":
                    isaac.homing = True
                    isaac.pickup_text = "Tirs Guidés!"
                elif item == "tirs_explosifs":
                    isaac.explosive = True
                    isaac.pickup_text = "Tirs Explosifs!"
                elif item == "tirs_disperses":
                    isaac.scatter = True
                    isaac.pickup_text = "Tirs Dispersés!"
                elif item == "taille_geante":
                    isaac.size *= 1.5
                    isaac.health += 4
                    isaac.max_health += 4
                    isaac.damage += 1
                    isaac.pickup_text = "Taille Géante!"
                elif item == "tirs_spectraux":
                    isaac.spectral = True
                    isaac.pickup_text = "Tirs Spectraux!"
                isaac.pickup_timer = 60

        # Achats shop
        if current_room.type == "shop" and current_room.shop_items:
            for i, (item, price) in enumerate(zip(current_room.shop_items[:], current_room.shop_prices[:])):
                x = WIDTH//3 if i == 0 else 2 * WIDTH//3
                y = HEIGHT//2

                # Check des collision // pieces
                if math.dist((isaac.x, isaac.y), (x, y)) < 30 and isaac.coins >= price:
                    # Deduire les pieces
                    isaac.coins -= price
                    if item == "degats_plus":
                        isaac.damage += 1
                        isaac.pickup_text = "Dégâts Augmentés!"
                    elif item == "vie_plus":
                        isaac.max_health += 2
                        isaac.health += 2
                        isaac.pickup_text = "Vie Augmentée!"
                    elif item == "tirs_plus":
                        isaac.fire_rate += 0.2
                        isaac.pickup_text = "Cadence de Tir Augmentée!"
                    elif item == "vitesse_plus":
                        isaac.speed += 1
                        isaac.pickup_text = "Vitesse Augmentée!"
                    elif item == "portee_plus":
                        for tear in isaac.tears:
                            tear.lifetime += 20
                        isaac.pickup_text = "Portée Augmentée!"
                    elif item == "taille_moins":
                        isaac.size = max(15, isaac.size - 5)
                        isaac.pickup_text = "Taille Réduite!"
                    elif item == "triple_tir":
                        isaac.triple_shot = True
                        isaac.pickup_text = "Triple Tir!"
                    elif item == "tirs_guides":
                        isaac.homing = True
                        isaac.pickup_text = "Tirs Guidés!"
                    elif item == "tirs_explosifs":
                        isaac.explosive = True
                        isaac.pickup_text = "Tirs Explosifs!"
                    elif item == "tirs_disperses":
                        isaac.scatter = True
                        isaac.pickup_text = "Tirs Dispersés!"
                    elif item == "taille_geante":
                        isaac.size *= 1.5
                        isaac.health += 4
                        isaac.max_health += 4
                        isaac.damage += 1
                        isaac.pickup_text = "Taille Géante!"
                    elif item == "tirs_spectraux":
                        isaac.spectral = True
                        isaac.pickup_text = "Tirs Spectraux!"
                    isaac.pickup_timer = 60

                    # enlever item shop
                    current_room.shop_items.pop(i)
                    current_room.shop_prices.pop(i)
                    isaac.pickup_timer = 60
                    break


        if current_room.type in ["devil", "angel"]:
            #c'est la meme chose que les dernieres fois
            for i, (item, price) in enumerate(zip(current_room.items[:], current_room.prices[:])):
                x = WIDTH // 3 if i == 0 else 2 * WIDTH // 3
                y = HEIGHT // 2

                if math.dist((isaac.x, isaac.y), (x, y)) < 30:
                    if current_room.type == "devil":
                        required_health = price * 2  # Convertir les cœurs en points de vie
                        if isaac.health >= required_health:
                            isaac.health -= required_health
                            # Appliquer l'effet de l'objet
                            if item == "pacte_sang":
                                isaac.damage *= 1.5
                                isaac.pickup_text = "Dégats x1.5!"
                            elif item == "abaddon":
                                isaac.speed += 1
                                isaac.damage += 2
                                isaac.pickup_text = "Vitesse et Dégâts ++!"
                            elif item == "pentagram":
                                isaac.damage += 2
                                isaac.speed += 1
                                isaac.fire_rate += 0.2
                                isaac.pickup_text = "Toutes stats ++!"
                            # Retirer l'objet de la salle
                            current_room.items.pop(i)
                            current_room.prices.pop(i)
                            isaac.pickup_timer = 60
                            break

                    elif current_room.type == "angel":
                        if item == "ailes_sacrees":
                            isaac.flying = True
                            isaac.speed += 2
                            isaac.pickup_text = "Vol, Vitesse ++!"
                        elif item == "couronne_divine":
                            isaac.holy_aura = True
                            isaac.damage += 2
                            isaac.pickup_text = "Aura Sacrée, Dégâts ++!"
                        elif item == "calice_sacre":
                            isaac.max_health += 4
                            isaac.health += 4
                            isaac.regen = True
                            isaac.pickup_text = "Régénération, Max HP ++!"
                        elif item == "aureole":
                            isaac.holy_triple = True
                            isaac.pickup_text = "Triple Tir Sacré!"
                        current_room.items.pop(i)
                        current_room.prices.pop(i)
                        isaac.pickup_timer = 60
                        break

        # transitions entre les rooms
        if current_room.doors["top"] and isaac.y < 70 and WIDTH // 2 - 30 < isaac.x < WIDTH // 2 + 30:
            if not current_room.enemies or current_room.type == "start":
                game.change_room("top", isaac)
        elif current_room.doors["bottom"] and isaac.y > HEIGHT - 70 and WIDTH // 2 - 30 < isaac.x < WIDTH // 2 + 30:
            if not current_room.enemies or current_room.type == "start":
                game.change_room("bottom", isaac)
        elif current_room.doors["left"] and isaac.x < 70 and HEIGHT // 2 - 30 < isaac.y < HEIGHT // 2 + 30:
            if not current_room.enemies or current_room.type == "start":
                game.change_room("left", isaac)
        elif current_room.doors["right"] and isaac.x > WIDTH - 70 and HEIGHT // 2 - 30 < isaac.y < HEIGHT // 2 + 30:
            if not current_room.enemies or current_room.type == "start":
                game.change_room("right", isaac)

        # check de la progression de l'etage
        if current_room.type == "boss" and not current_room.enemies and math.dist((isaac.x, isaac.y), (WIDTH // 2, HEIGHT // 2)) < 30:
            game.next_floor(isaac)

        # Update jeu
        isaac.update(current_room)
        current_room.draw()

        # Update ennemies
        for enemy in current_room.enemies[:]:
            enemy.update()
            enemy.move_towards(isaac.x, isaac.y)
            enemy.draw(screen)

            if enemy.type == "pooter" or enemy.type == "boss":
                if enemy.shoot_cooldown <= 0:
                    enemy.shoot(isaac.x, isaac.y)
                    enemy.shoot_cooldown = enemy.shoot_delay
                enemy.shoot_cooldown -= 1
                for projectile in enemy.projectiles[:]:
                    if projectile.update():  # If hit wall
                        enemy.projectiles.remove(projectile)
                    else:
                        projectile.draw()
                    if math.dist((projectile.x, projectile.y), (isaac.x, isaac.y)) < isaac.size + projectile.size:
                        if isaac.invincibility_frames <= 0:
                            isaac.health -= 1
                            isaac.invincibility_frames = isaac.invincibility_duration
                        if isaac.health <= 0:
                            game_over = True
                        enemy.projectiles.remove(projectile)

            if enemy.type == "boss":
                enemy.spawn_minion(current_room)

            # Check tirs collisions partie 983475894375934
            for tear in isaac.tears[:]:
                if math.dist((tear.x, tear.y), (enemy.x, enemy.y)) < enemy.size + tear.size:
                    if enemy not in tear.hit_enemies:
                        enemy.health -= tear.damage
                        tear.hit_enemies.add(enemy)
                        if not tear.properties.get('spectral'):
                            if tear in isaac.tears:
                                isaac.tears.remove(tear)
                    if enemy.health <= 0:
                        current_room.enemies.remove(enemy)
                        current_room.cleared = True
                        isaac.score += 100
                        isaac.coins += 1
                        if enemy.type == "boss":
                            isaac.score += 1000
                            isaac.coins += 5
                            room_chance = random.random()
                            if room_chance < 0.3:  # Modifier ici la proba room demon
                                new_pos = (game.floor.current_position[0], game.floor.current_position[1] + 1)
                                if new_pos not in game.floor.rooms:
                                    game.floor.rooms[new_pos] = Room("devil", game.floor.level)
                                    game.floor.rooms[new_pos].spawn_special_room("devil")
                                    current_room.doors["bottom"] = True
                                    game.floor.rooms[new_pos].doors["top"] = True
                            elif room_chance < 0.5:  # proba room ange SUR room
                                new_pos = (game.floor.current_position[0], game.floor.current_position[1] + 1)
                                if new_pos not in game.floor.rooms:
                                    game.floor.rooms[new_pos] = Room("angel", game.floor.level)
                                    game.floor.rooms[new_pos].spawn_special_room("angel")
                                    current_room.doors["bottom"] = True
                                    game.floor.rooms[new_pos].doors["top"] = True
                        # Spawn particules si l'ennemie meurt
                        for _ in range(20):
                            particle = Particle(
                                enemy.x, enemy.y,
                                color=RED if enemy.type == "boss" else (150, 150, 150),
                                size=random.randint(3, 6),
                                dx=random.uniform(-2, 2),
                                dy=random.uniform(-2, 2),
                                lifetime=random.randint(15, 30)
                            )
                            current_room.particles.append(particle)
                        break

        # Draw tirs
        for tear in isaac.tears:
            if tear.update(current_room):  # Si tirs touche mur
                isaac.tears.remove(tear)
                continue
            tear.draw()

        if keys[pygame.K_TAB]:
          draw_stats(isaac)

        # Draw Isaac
        isaac.draw()

        # Draw texte
        if isaac.pickup_timer > 0:
            font = pygame.font.SysFont("Arial", 24)
            text = font.render(isaac.pickup_text, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
            isaac.pickup_timer -= 1

        # Draw systeme de cheat
        if CHEATS_ENABLED:
            font = pygame.font.SysFont("Arial", 20)
            cheat_text = font.render("TRICHE ACTIVÉ", True, RED)
            screen.blit(cheat_text, (10, 10))

            cheats_list = [
                "1: Vie Maximum",
                "2: Dégâts +",
                "3: +50 Pièces",
                "4: Cadence +",
                "5: Aura sacré",
                "6: Triple Tir",
                "7: Tirs Guidés",
                "8: Tirs éparpillés",
                "9: Tirs Spectraux",
                "0: Vider Salle",
            ]

            for i, cheat in enumerate(cheats_list):
                text = font.render(cheat, True, WHITE)
                screen.blit(text, (10, 40 + i * 20))

        # Draw minimap
        game.draw_minimap()

        # Update ecran
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

#Je code en anglais dit moi si tu comprends pas qlq chose Arnaud
import pygame
import random
import math
import time

CHEATS_ENABLED = False

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Binding of Pygame")
clock = pygame.time.Clock()



# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BEIGE = (245, 245, 220)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

FLOOR_COLORS = [
    BROWN,  # Brown
    (100, 100, 100),  # Gray
    (0, 100, 100),  # Dark Cyan
    (139, 0, 0),  # Dark Red
    (75, 0, 130),  # Purple
    (25, 25, 25),  # Dark Gray
]


ROOM_TYPES = ["normal", "treasure", "boss", "shop", "devil", "angel"]
ENEMY_TYPES = ["fly", "spider", "pooter", "charger"]

DEVIL_ITEMS = [
    ("pacte_sang", "Dégâts x2, -2 Coeurs"),
    ("brimstone", "Laser Démoniaque, -2 Coeurs"),
    ("abaddon", "Vitesse et Dégâts ++, -2 Coeurs"),
    ("pentagram", "Tous Stats ++, -1 Coeur")
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
    
    title = font_large.render("Binding Of Pygame", True, RED)
    start_text = font_small.render("Appuyez sur ENTRÉE pour Commencer", True, WHITE)
    controls_text = font_small.render("Flèches pour Tirer, WASD pour Bouger", True, WHITE)
    
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
    screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT//2 + 50))
    pygame.display.flip()

def game_over_screen(score):
    screen.fill(BLACK)
    font = pygame.font.SysFont("Arial", 64)
    game_over_text = font.render("PARTIE TERMINÉE", True, RED)
    restart_text = font.render("Appuyez sur ENTRÉE pour recommencer", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//3))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    screen.blit(restart_text, (WIDTH//5 - restart_text.get_width()//2, HEIGHT//2 + 100))
    pygame.display.flip()

class Isaac:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.size = 25
        self.health = 6  # 3 hearts
        self.max_health = 6
        self.damage = 3.5
        self.fire_rate = 1.0
        self.speed = 4
        self.tears = []
        self.shoot_delay = 15
        self.shoot_timer = 0
        self.coins = 0
        self.keys = 0
        self.bombs = 0
        self.items = []
        self.invincibility_frames = 0
        self.invincibility_duration = 60  # 1 second at 60 FPS
        self.score = 0
        self.pickup_text = ""
        self.pickup_timer = 0
        self.triple_shot = False
        self.homing = False
        self.explosive = False
        self.scatter = False
        self.spectral = False
        self.laser = False  # For Brimstone (devil item)
        self.flying = False  # For Ailes Sacrées (angel item)
        self.holy_aura = False  # For Couronne Divine (angel item)
        self.aura_damage = 2  # Damage per tick
        self.regen = False  # For Calice Sacré (angel item)
        self.holy_triple = False  # For Auréole (angel item)
        self.laser_damage = 2  # Damage per tick
        self.regen_timer = 0  # Timer for regeneration
        self.laser_direction = (1, 0)
        self.shooting = False  # Track if the player is actively shooting

    def draw(self):
        # Draw Isaac 
        pygame.draw.circle(screen, BEIGE, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, BLACK, (int(self.x - 8), int(self.y - 5)), 4)
        pygame.draw.circle(screen, BLACK, (int(self.x + 8), int(self.y - 5)), 4)

        # Draw laser if active and shooting
        if self.laser and self.shooting:
            # Calculate the offset starting position of the laser based on direction
            offset_distance = self.size + 10  # Start the laser slightly outside Isaac's body
            laser_start_x = self.x + self.laser_direction[0] * offset_distance
            laser_start_y = self.y + self.laser_direction[1] * offset_distance

            # Calculate the end point of the laser based on direction
            laser_end_x = self.x + self.laser_direction[0] * WIDTH
            laser_end_y = self.y + self.laser_direction[1] * HEIGHT

            # Draw a thicker laser line to match the hitbox
            laser_thickness = 20  # Adjust this value to match the hitbox range
            pygame.draw.line(screen, RED, (laser_start_x, laser_start_y), (laser_end_x, laser_end_y), laser_thickness)

        # Draw holy aura if active
        if self.holy_aura:
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 100, 3)

        if self.invincibility_frames > 0 and self.invincibility_frames % 10 < 5:
            return  # Skip drawing to create flashing effect

        # Draw wings if active
        if self.flying:
            # Draw wings
            pygame.draw.polygon(screen, WHITE, [(self.x - 20, self.y), (self.x - 30, self.y - 10), (self.x - 20, self.y - 20)])
            pygame.draw.polygon(screen, WHITE, [(self.x + 20, self.y), (self.x + 30, self.y - 10), (self.x + 20, self.y - 20)])
        
        # Draw hearts
        for i in range(self.max_health // 2):
            if self.health >= (i + 1) * 2:
                pygame.draw.circle(screen, RED, (30 + i * 30, 30), 10)  # Full 
            elif self.health >= i * 2 + 1:
                pygame.draw.arc(screen, RED, (20 + i * 30, 20, 20, 20), 0, math.pi, 2)  # Half 

        # Draw coin 
        font = pygame.font.SysFont("Arial", 20)
        coin_text = font.render(f"{self.coins}$", True, YELLOW)
        screen.blit(coin_text, (WIDTH - 100, 30))

    def shoot(self, dx, dy, current_room):
        if self.laser:
            # Update laser direction only when shooting
            if self.shooting:
                self.laser_direction = (dx, dy)
        elif not self.laser:
            # Normal tears or triple shot
            if self.shoot_timer <= 0:
                tear_speed = 7 if not self.triple_shot else 4
                properties = {
                    'homing': self.homing,
                    'explosive': self.explosive,
                    'spectral': self.spectral,
                    'triple_shot': self.triple_shot
                }

                # Enable triple shot if holy_triple is active
                if self.holy_triple:
                    self.triple_shot = True

                # Triple shot logic
                if self.triple_shot:
                    # Main tear
                    self.tears.append(Tear(self.x, self.y, dx * tear_speed, dy * tear_speed, self.damage, properties))
                    
                    # Calculate angles for left and right tears
                    angle = math.atan2(dy, dx)
                    left_angle = angle - math.pi / 12  # 15 degrees to the left
                    right_angle = angle + math.pi / 12  # 15 degrees to the right

                    # Left tear
                    self.tears.append(Tear(
                        self.x, self.y,
                        tear_speed * math.cos(left_angle),
                        tear_speed * math.sin(left_angle),
                        self.damage, properties
                    ))

                    # Right tear
                    self.tears.append(Tear(
                        self.x, self.y,
                        tear_speed * math.cos(right_angle),
                        tear_speed * math.sin(right_angle),
                        self.damage, properties
                    ))
                else:
                    # Single tear
                    self.tears.append(Tear(self.x, self.y, dx * tear_speed, dy * tear_speed, self.damage, properties))

                # Scatter shot logic
                if self.scatter:
                    for _ in range(3):
                        scatter_angle = random.uniform(0, 2 * math.pi)
                        scatter_speed = tear_speed * 0.6
                        self.tears.append(Tear(
                            self.x, self.y,
                            scatter_speed * math.cos(scatter_angle),
                            scatter_speed * math.sin(scatter_angle),
                            self.damage * 0.5, properties
                        ))

                # Reset shoot timer based on fire rate
                self.shoot_timer = self.shoot_delay / self.fire_rate

    def update(self, current_room):
        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        # Update laser damage only if shooting
        if self.laser and self.shooting:
            # Calculate the end point of the laser based on direction
            laser_end_x = self.x + self.laser_direction[0] * WIDTH
            laser_end_y = self.y + self.laser_direction[1] * HEIGHT

            # Deal damage to enemies in the laser's path
            for enemy in current_room.enemies[:]:
                # Check if the enemy is aligned with the laser's direction
                if self.laser_direction[0] != 0:  # Horizontal laser
                    if abs(enemy.y - self.y) < 10:  # Check if enemy is within a small vertical range
                        if (self.laser_direction[0] > 0 and enemy.x > self.x) or (self.laser_direction[0] < 0 and enemy.x < self.x):
                            enemy.health -= self.laser_damage
                            if enemy.health <= 0:
                                current_room.enemies.remove(enemy)
                                self.score += 100
                elif self.laser_direction[1] != 0:  # Vertical laser
                    if abs(enemy.x - self.x) < 10:  # Check if enemy is within a small horizontal range
                        if (self.laser_direction[1] > 0 and enemy.y > self.y) or (self.laser_direction[1] < 0 and enemy.y < self.y):
                            enemy.health -= self.laser_damage
                            if enemy.health <= 0:
                                current_room.enemies.remove(enemy)
                                self.score += 100

        # Update other effects (holy aura, regeneration, etc.)
        if self.holy_aura:
            for enemy in current_room.enemies[:]:
                if math.dist((self.x, self.y), (enemy.x, enemy.y)) < 100:  # Aura radius
                    enemy.health -= self.aura_damage
                    if enemy.health <= 0:
                        current_room.enemies.remove(enemy)
                        self.score += 100

        if self.regen:
            self.regen_timer += 1
            if self.regen_timer >= 1000:  # Heal every 3 seconds
                self.health = min(self.health + 1, self.max_health)
                self.regen_timer = 0

        # Update tears with current room
        for tear in self.tears[:]:
            tear.update(current_room)
            if tear.lifetime <= 0:
                self.tears.remove(tear)

    def point_line_distance(self, px, py, x1, y1, x2, y2):
        # Calculate the distance between a point (px, py) and a line segment (x1, y1) to (x2, y2)
        numerator = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1)
        denominator = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
        return numerator / denominator

    def check_wall_collision(self, room):
        # Keep Isaac inside room boundaries except at doors
        if self.x < room.x + self.size and not (HEIGHT//2 - 30 < self.y < HEIGHT//2 + 30):
            self.x = room.x + self.size
        elif self.x > room.x + room.width - self.size and not (HEIGHT//2 - 30 < self.y < HEIGHT//2 + 30):
            self.x = room.x + room.width - self.size
            
        if self.y < room.y + self.size and not (WIDTH//2 - 30 < self.x < WIDTH//2 + 30):
            self.y = room.y + self.size
        elif self.y > room.y + room.height - self.size and not (WIDTH//2 - 30 < self.x < WIDTH//2 + 30):
            self.y = room.y + room.height - self.size

    def game_over_screen():
        screen.fill(BLACK)
        font = pygame.font.SysFont("Arial", 64)
        game_over_text = font.render("GAME OVER", True, RED)
        restart_text = font.render("Press ENTER to restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
        pygame.display.flip()

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
        screen.blit(text, (WIDTH - 200, 450 + i * 20))  # Display stats on the right side


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
        self.size = max(0, self.size - 0.1)  # Shrink over time
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
        
        # Check wall collisions (unless spectral)
        if not self.properties.get('spectral'):
            if next_x < 50 or next_x > WIDTH - 50 or next_y < 50 or next_y > HEIGHT - 50:
                # Spawn particles when tear hits a wall
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
                return True  # Signal to remove tear
        
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
        self.max_speed = 8  # Cap for maximum speed
        self.speed = min(self.base_speed * 0.5 + (floor_level * 0.3), self.max_speed) if enemy_type == "boss" else self.base_speed
        self.projectiles = []
        self.shoot_cooldown = 60
        self.charge_cooldown = 180
        self.charge_timer = 0
        self.charging = False
        if enemy_type == "boss":
            self.shoot_delay = 400
            self.spawn_timer = 200  # 10 seconds between spawns
            self.spawn_cooldown = 200  # Initial delay
        else:
            self.shoot_delay = 120
        self.size = 20 if enemy_type != "boss" else 30
        self.floor_level = floor_level  # Add this line

    def draw(self):
        if self.type == "fly":
            # Draw outline
            pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.size + 2)
            # Draw fly body
            pygame.draw.circle(screen, (150, 150, 150), (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, (100, 100, 100), (int(self.x), int(self.y)), self.size - 5)
        elif self.type == "spider":
            # Draw outline
            pygame.draw.rect(screen, BLACK, (self.x - self.size - 2, self.y - self.size - 2, (self.size * 2) + 4, (self.size * 2) + 4))
            # Draw spider body
            pygame.draw.rect(screen, (30, 30, 30), (self.x - self.size, self.y - self.size, self.size * 2, self.size * 2))
        elif self.type == "pooter":
            # Draw outline
            pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.size + 2)
            # Draw pooter body
            pygame.draw.circle(screen, BROWN, (int(self.x), int(self.y)), self.size)
        elif self.type == 'charger':
            color = (255, 165, 0) if self.charging else (200, 50, 50)
            pygame.draw.rect(screen, color, (self.x-self.size, self.y-self.size, self.size*2, self.size*2))
        if self.type == "boss":
            size_mult = min(2.5, 1 + (self.health / 200))  # Capped size multiplier
            pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), int(self.size * size_mult) + 2)
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), int(self.size * size_mult))

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.type == 'charger':
            if self.charge_timer > 0:
                self.charge_timer -= 1
        if self.type == "boss":
            if self.spawn_timer > 0:
                self.spawn_timer -= 1
            
    def move_towards(self, target_x, target_y):
        if self.type == "fly":
            # Flies move in a wavy pattern
            angle = math.atan2(target_y - self.y, target_x - self.x)
            self.x += math.cos(angle + math.sin(time.time() * 2)) * self.speed
            self.y += math.sin(angle + math.sin(time.time() * 2)) * self.speed
        elif self.type == "spider":
            # Spiders move in quick bursts with pauses
            if random.randint(0, 100) < 5:  # 5% chance to change direction
                angle = math.atan2(target_y - self.y, target_x - self.x)
                self.x += math.cos(angle) * self.speed * 3
                self.y += math.sin(angle) * self.speed * 3
        if self.type == "pooter":
            if self.shoot_cooldown <= 0:
                self.shoot(target_x, target_y)
                self.shoot_cooldown = self.shoot_delay
        if self.type == 'charger':
            if not self.charging and self.charge_timer <= 0:
                if random.random() < 0.005:  # 2% chance to start charge
                    self.charging = True
                    self.speed *= 3
                    self.charge_timer = 60
            if self.charging:
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
        return False

    def shoot(self, target_x, target_y):
        if self.type == "boss":
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                dx = math.cos(rad) * 5
                dy = math.sin(rad) * 5
                self.projectiles.append(Projectile(self.x, self.y, dx, dy))
        else:
            # Normal enemy shooting
            angle = math.atan2(target_y - self.y, target_x - self.x)
            dx = math.cos(angle) * 5
            dy = math.sin(angle) * 5
            self.projectiles.append(Projectile(self.x, self.y, dx, dy))

    def spawn_minion(self, current_room):
        if self.type == "boss" and self.spawn_timer <= 0:
            num_minions = min(self.floor_level, 4)  # Cap at 4 minions
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
        
        # Check wall collisions
        if next_x < 50 or next_x > WIDTH - 50 or next_y < 50 or next_y > HEIGHT - 50:
            return True  # Signal to remove projectile
            
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
        self.generate_floor()

    def generate_floor(self):
        # Start room
        self.rooms[(0, 0)] = Room("start", self.level)

        # Generate all positions first
        positions = []
        for _ in range(self.room_count):
            if not positions:
                positions = self.get_valid_adjacent_positions()
            if positions:
                pos = positions.pop(0)
                self.rooms[pos] = Room("normal", self.level)

        # Replace random normal rooms with special rooms
        normal_positions = [(x, y) for (x, y) in self.rooms.keys() if (x, y) != (0, 0)]
        special_rooms = ["treasure", "shop", "boss"]

        # Ensure the boss room is placed where there is no room below it
        boss_placed = False
        while not boss_placed and normal_positions:
            pos = random.choice(normal_positions)
            x, y = pos
            # Check if there is no room below the boss room
            if (x, y + 1) not in self.rooms:
                self.rooms[pos] = Room("boss", self.level)
                boss_placed = True
                normal_positions.remove(pos)

        # Place other special rooms (treasure, shop)
        for room_type in ["treasure", "shop"]:
            if normal_positions:
                pos = random.choice(normal_positions)
                normal_positions.remove(pos)
                self.rooms[pos] = Room(room_type, self.level)

        # Update all room doors
        self.update_all_doors()

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
        self.floor_level = floor_level  # Add this line to track the current floor level
        self.obstacles = []
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
        num_obstacles = random.randint(3, 6)
        safe_radius = 100
        
        for _ in range(num_obstacles):
            while True:
                x = random.randint(self.x + 100, self.x + self.width - 100)
                y = random.randint(self.y + 100, self.y + self.height - 100)
                
                # Check if position is safe from doors and center
                center_safe = math.dist((x, y), (WIDTH//2, HEIGHT//2)) > safe_radius
                top_safe = math.dist((x, y), (WIDTH//2, 50)) > safe_radius
                bottom_safe = math.dist((x, y), (WIDTH//2, HEIGHT-50)) > safe_radius
                left_safe = math.dist((x, y), (50, HEIGHT//2)) > safe_radius
                right_safe = math.dist((x, y), (WIDTH-50, HEIGHT//2)) > safe_radius
                
                # Check distance from other obstacles
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
        safe_radius = 150  # Minimum distance from center
        
        for _ in range(num_enemies):
            enemy_type = random.choice(ENEMY_TYPES)
            
            while True:
                x = random.randint(self.x + 50, self.x + self.width - 50)
                y = random.randint(self.y + 50, self.y + self.height - 50)
                
                # Check distance from center AND all doors
                center_safe = math.dist((x, y), (WIDTH//2, HEIGHT//2)) > safe_radius
                top_safe = math.dist((x, y), (WIDTH//2, 50)) > safe_radius
                bottom_safe = math.dist((x, y), (WIDTH//2, HEIGHT-50)) > safe_radius
                left_safe = math.dist((x, y), (50, HEIGHT//2)) > safe_radius
                right_safe = math.dist((x, y), (WIDTH-50, HEIGHT//2)) > safe_radius
                
                if center_safe and top_safe and bottom_safe and left_safe and right_safe:
                    self.enemies.append(Enemy(enemy_type, x, y, enemy_health))
                    break

    def spawn_boss(self, floor_level):
        boss_health = 100 + (floor_level * 25)  # Reduced health scaling
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
            # Select 2 random items with their prices
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
            for item, desc in selected:
                self.items.append(item)
                self.prices.append(2)  # Cost in hearts
        elif room_type == "angel":
            selected = random.sample(ANGEL_ITEMS, 2)
            for item in selected:
                self.items.append(item[0])
                self.prices.append(0)  # Free but rare

        # Ensure the top door is open (leading back to the boss room)
        self.doors["top"] = True

    def draw(self):
        # Get floor color based on current level (cycle through colors if level exceeds color list)
        floor_color = FLOOR_COLORS[(self.floor_level - 1) % len(FLOOR_COLORS)]
        # Draw room with current floor color
        pygame.draw.rect(screen, floor_color, (self.x, self.y, self.width, self.height))

        for obstacle in self.obstacles:
            pygame.draw.rect(screen, GREEN, (obstacle['x'] - obstacle['size']//2, 
                                           obstacle['y'] - obstacle['size']//2, 
                                           obstacle['size'], 
                                           obstacle['size']))
        
        # Draw doors
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

        # Draw items if it's a devil or angel room
        if self.type in ["devil", "angel"] and self.items:
            for i, (item, price) in enumerate(zip(self.items, self.prices)):
                x = WIDTH//3 if i == 0 else 2 * WIDTH//3  # Position items side by side
                y = HEIGHT//2

                # Draw item circle
                pygame.draw.circle(screen, YELLOW, (x, y), 15)

                # Draw item name
                font = pygame.font.SysFont("Arial", 20)
                item_text = font.render(item.replace("_", " ").title(), True, WHITE)
                screen.blit(item_text, (x - item_text.get_width()//2, y + 30))

                # Draw price (only for devil items)
                if self.type == "devil":
                    price_text = font.render(f"{price} ❤️", True, RED)
                    screen.blit(price_text, (x - price_text.get_width()//2, y + 50))

        # Draw trapdoor in boss room when cleared
        if self.type == "boss" and not self.enemies:
            pygame.draw.rect(screen, BLACK, (WIDTH//2 - 30, HEIGHT//2 - 30, 60, 60))
            floor_color = FLOOR_COLORS[(self.floor_level - 1) % len(FLOOR_COLORS)]
            pygame.draw.circle(screen, floor_color, (WIDTH//2, HEIGHT//2), 10)
            font = pygame.font.SysFont("Arial", 20)
            text = font.render("Étage Suivant", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))

        # Draw items if it's a treasure room
        if self.type == "treasure" and self.items:
            pygame.draw.circle(screen, YELLOW, (WIDTH//2, HEIGHT//2), 15)

        # Draw shop items
        if self.type == "shop" and self.shop_items:
            for i, (item, price) in enumerate(zip(self.shop_items, self.shop_prices)):
                x = WIDTH//3 if i == 0 else 2 * WIDTH//3
                pygame.draw.circle(screen, YELLOW, (x, HEIGHT//2), 15)
                # Draw price
                font = pygame.font.SysFont("Arial", 20)
                price_text = font.render(f"{price}$", True, WHITE)
                screen.blit(price_text, (x - price_text.get_width()//2, HEIGHT//2 + 30))

        # Draw items if it's a treasure room
        if self.type == "treasure" and self.items:
            pygame.draw.circle(screen, YELLOW, (WIDTH//2, HEIGHT//2), 15)
            # Draw item name
            font = pygame.font.SysFont("Arial", 20)
            item_text = font.render(self.items[0].replace("_", " ").title(), True, WHITE)
            screen.blit(item_text, (WIDTH//2 - item_text.get_width()//2, HEIGHT//2 + 30))

        # Draw shop items
        if self.type == "shop" and self.shop_items:
            for i, (item, price) in enumerate(zip(self.shop_items, self.shop_prices)):
                x = WIDTH//3 if i == 0 else 2 * WIDTH//3
                pygame.draw.circle(screen, YELLOW, (x, HEIGHT//2), 15)
                # Draw price
                font = pygame.font.SysFont("Arial", 20)
                price_text = font.render(f"{price}$", True, WHITE)
                item_text = font.render(item.replace("_", " ").title(), True, WHITE)
                screen.blit(price_text, (x - price_text.get_width()//2, HEIGHT//2 + 30))
                screen.blit(item_text, (x - item_text.get_width()//2, HEIGHT//2 + 50))

        font = pygame.font.SysFont("Arial", 24)
        floor_text = font.render(f"Étage {self.floor_level}", True, WHITE)
        screen.blit(floor_text, (10, HEIGHT - 30))  # Moved to bottom left

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
            if direction == "top": isaac.y = HEIGHT - 100
            elif direction == "bottom": isaac.y = 100
            elif direction == "left": isaac.x = WIDTH - 100
            elif direction == "right": isaac.x = 100

    def next_floor(self, isaac):
        self.current_floor += 1
        self.floor = Floor(self.current_floor)
        isaac.x = WIDTH // 2
        isaac.y = HEIGHT // 2
        isaac.health = min(isaac.health + 2, isaac.max_health)  # Heal 1 heart between floors

    def game_over_screen():
        screen.fill(BLACK)
        font = pygame.font.SysFont("Arial", 64)
        game_over_text = font.render("PARTIE TERMINÉE", True, RED)
        restart_text = font.render("Appuyez sur ENTRÉE pour recommencer", True, WHITE)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
        pygame.display.flip()

    def draw_minimap(self):
        map_size = 10
        for pos, room in self.floor.rooms.items():
            x, y = pos
            map_x = WIDTH - 120 + (x * 15)  # Moved slightly left
            map_y = 100 + (y * 15)  # Moved down below coin counter
            
            # Draw room background - using darker gray for non-current rooms
            color = WHITE if pos == self.floor.current_position else (50, 50, 50)
            pygame.draw.rect(screen, color, (map_x, map_y, map_size, map_size))
            
            # Draw room type indicators
            if room.type == "boss":
                pygame.draw.circle(screen, RED, (map_x + map_size//2, map_y + map_size//2), 3)
            elif room.type == "shop":
                pygame.draw.circle(screen, YELLOW, (map_x + map_size//2, map_y + map_size//2), 3)
            elif room.type == "treasure":
                pygame.draw.circle(screen, BLUE, (map_x + map_size//2, map_y + map_size//2), 3)
            elif room.type == "devil":
                pygame.draw.circle(screen, (128, 0, 128), (map_x + map_size//2, map_y + map_size//2), 3)  # Purple for devil
            elif room.type == "angel":
                pygame.draw.circle(screen, (0, 0, 255), (map_x + map_size//2, map_y + map_size//2), 3)  # Blue for angel



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

    # Reset game function
    def reset_game():
        return Game(), Isaac()

    # Initialize game and Isaac
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

        # Get current room
        current_room = game.floor.rooms[game.floor.current_position]

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    global CHEATS_ENABLED
                    CHEATS_ENABLED = not CHEATS_ENABLED
                elif CHEATS_ENABLED:
                    if event.key == pygame.K_KP1 or event.key == pygame.K_1:
                        isaac.health = isaac.max_health
                    if event.key == pygame.K_KP2 or event.key == pygame.K_2:
                        isaac.damage += 5
                    if event.key == pygame.K_KP3 or event.key == pygame.K_3:
                        isaac.coins += 50
                    if event.key == pygame.K_KP4 or event.key == pygame.K_4:
                        isaac.fire_rate += 1
                    if event.key == pygame.K_KP5 or event.key == pygame.K_5:
                        isaac.laser = True
                    if event.key == pygame.K_KP6 or event.key == pygame.K_6:
                        isaac.triple_shot = True
                    if event.key == pygame.K_KP7 or event.key == pygame.K_7:
                        isaac.homing = True
                    if event.key == pygame.K_KP8 or event.key == pygame.K_8:
                        isaac.explosive = True
                    if event.key == pygame.K_KP9 or event.key == pygame.K_9:
                        isaac.spectral = True
                    if event.key == pygame.K_KP0 or event.key == pygame.K_0:
                        current_room.enemies.clear()

        # Handle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: isaac.x -= isaac.speed
        if keys[pygame.K_d]: isaac.x += isaac.speed
        if keys[pygame.K_w]: isaac.y -= isaac.speed
        if keys[pygame.K_s]: isaac.y += isaac.speed

        # Wall collisions
        isaac.check_wall_collision(current_room)

        # Update particles
        for particle in current_room.particles[:]:
            if not particle.update():
                current_room.particles.remove(particle)

        # Draw particles
        for particle in current_room.particles:
            particle.draw()

        # Handle shooting
        isaac.shooting = False  # Reset shooting flag at the start of each frame

        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            isaac.shooting = True  # Set shooting flag if any shooting key is pressed

            if isaac.laser:
                # Update laser direction immediately
                if keys[pygame.K_LEFT]: isaac.laser_direction = (-1, 0)
                if keys[pygame.K_RIGHT]: isaac.laser_direction = (1, 0)
                if keys[pygame.K_UP]: isaac.laser_direction = (0, -1)
                if keys[pygame.K_DOWN]: isaac.laser_direction = (0, 1)
            elif not isaac.laser:
                # Normal tears
                if keys[pygame.K_LEFT]: isaac.shoot(-1, 0, current_room)
                if keys[pygame.K_RIGHT]: isaac.shoot(1, 0, current_room)
                if keys[pygame.K_UP]: isaac.shoot(0, -1, current_room)
                if keys[pygame.K_DOWN]: isaac.shoot(0, 1, current_room)

        # Handle obstacle collisions (if not flying)
        if not isaac.flying:
            for obstacle in current_room.obstacles:
                if math.dist((isaac.x, isaac.y), (obstacle['x'], obstacle['y'])) < isaac.size + obstacle['size'] // 2:
                    # Push Isaac away from obstacle
                    angle = math.atan2(isaac.y - obstacle['y'], isaac.x - obstacle['x'])
                    isaac.x = obstacle['x'] + math.cos(angle) * (isaac.size + obstacle['size'] // 2)
                    isaac.y = obstacle['y'] + math.sin(angle) * (isaac.size + obstacle['size'] // 2)

        # Handle tear collisions with obstacles
        for tear in isaac.tears[:]:
            for obstacle in current_room.obstacles[:]:
                if math.dist((tear.x, tear.y), (obstacle['x'], obstacle['y'])) < tear.size + obstacle['size'] // 2:
                    if not tear.properties.get('spectral'):
                        isaac.tears.remove(tear)
                    obstacle['health'] -= 1
                    if obstacle['health'] <= 0:
                        current_room.obstacles.remove(obstacle)
                    break

        # Handle enemy collisions
        for enemy in current_room.enemies:
            if math.dist((enemy.x, enemy.y), (isaac.x, isaac.y)) < enemy.size + isaac.size:
                if isaac.invincibility_frames <= 0:
                    isaac.health -= 1
                    isaac.invincibility_frames = isaac.invincibility_duration
                    if isaac.health <= 0:
                        game_over = True

        # Handle treasure collection
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

        # Handle shop purchases
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
            for i, (item, price) in enumerate(zip(current_room.items[:], current_room.prices[:])):
                # Calculate the position of the item (left or right)
                x = WIDTH // 3 if i == 0 else 2 * WIDTH // 3
                y = HEIGHT // 2

                # Check if the player is close enough to pick up the item
                if math.dist((isaac.x, isaac.y), (x, y)) < 30:
                    if current_room.type == "devil" and isaac.health > price * 2:
                        # Deduct health for devil items
                        isaac.health -= price * 2

                        # Apply the item effect
                        if item == "pacte_sang":
                            isaac.damage *= 1.5
                            isaac.pickup_text = "Dégâts x1.5!"
                        elif item == "brimstone":
                            isaac.tears = []  # Clear tears
                            isaac.laser = True  # Enable laser
                            isaac.pickup_text = "Laser Démoniaque!"
                        elif item == "abaddon":
                            isaac.speed += 1
                            isaac.damage += 2
                            isaac.pickup_text = "Vitesse et Dégâts ++!"
                        elif item == "pentagram":
                            isaac.damage += 2
                            isaac.speed += 1
                            isaac.fire_rate += 0.2
                            isaac.pickup_text = "Tous Stats ++!"

                        # Remove the item from the room
                        current_room.items.pop(i)
                        current_room.prices.pop(i)
                        isaac.pickup_timer = 60  # Display pickup text for 60 frames
                        break  # Exit the loop after picking up an item

                    elif current_room.type == "angel":
                        # Apply the item effect (angel items are free)
                        if item == "ailes_sacrees":
                            isaac.flying = True  # Enable flying
                            isaac.speed += 2
                            isaac.pickup_text = "Vol, Vitesse ++!"
                        elif item == "couronne_divine":
                            isaac.holy_aura = True  # Enable holy aura
                            isaac.damage += 2
                            isaac.pickup_text = "Aura Sacrée + Dégâts ++!"
                        elif item == "calice_sacre":
                            isaac.max_health += 4
                            isaac.health += 4
                            isaac.regen = True  # Enable regeneration
                            isaac.pickup_text = "Régénération, Max HP ++!"
                        elif item == "aureole":
                            isaac.holy_triple = True  # Enable holy triple shot
                            isaac.pickup_text = "Triple Tir Sacré!"

                        # Remove the item from the room
                        current_room.items.pop(i)
                        current_room.prices.pop(i)
                        isaac.pickup_timer = 60  # Display pickup text for 60 frames
                        break  # Exit the loop after picking up an item

        # Handle room transitions
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

        # Check for floor progression
        if current_room.type == "boss" and not current_room.enemies and math.dist((isaac.x, isaac.y), (WIDTH // 2, HEIGHT // 2)) < 30:
            game.next_floor(isaac)

        # Update game state
        isaac.update(current_room)
        current_room.draw()

        # Update enemies
        for enemy in current_room.enemies[:]:
            enemy.update()
            enemy.move_towards(isaac.x, isaac.y)
            enemy.draw()

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
                        enemy.projectiles.remove(projectile)

            if enemy.type == "boss":
                enemy.spawn_minion(current_room)

            # Check tear collisions
            for tear in isaac.tears[:]:
                if math.dist((tear.x, tear.y), (enemy.x, enemy.y)) < enemy.size + tear.size:
                    if enemy not in tear.hit_enemies:  # Only damage enemy once
                        enemy.health -= tear.damage
                        tear.hit_enemies.add(enemy)
                        if not tear.properties.get('spectral'):
                            if tear in isaac.tears:
                                isaac.tears.remove(tear)
                    if enemy.health <= 0:
                        current_room.enemies.remove(enemy)
                        current_room.cleared = True
                        isaac.score += 100  # Points for killing enemy
                        isaac.coins += 1
                        if enemy.type == "boss":
                            isaac.score += 1000
                            isaac.coins += 5
                            # Add the new devil/angel room code here
                            room_chance = random.random()
                            if room_chance < 0.4:  # 50% chance for devil room
                                new_pos = (game.floor.current_position[0], game.floor.current_position[1] + 1)
                                if new_pos not in game.floor.rooms:
                                    # Create the devil room
                                    game.floor.rooms[new_pos] = Room("devil", game.floor.level)
                                    game.floor.rooms[new_pos].spawn_special_room("devil")
                                    # Open the bottom door of the boss room
                                    current_room.doors["bottom"] = True
                                    # Open the top door of the devil room
                                    game.floor.rooms[new_pos].doors["top"] = True
                            elif room_chance < 0.1:  # 40% chance for angel room (if devil room doesn't spawn)
                                new_pos = (game.floor.current_position[0], game.floor.current_position[1] + 1)
                                if new_pos not in game.floor.rooms:
                                    # Create the angel room
                                    game.floor.rooms[new_pos] = Room("angel", game.floor.level)
                                    game.floor.rooms[new_pos].spawn_special_room("angel")
                                    # Open the bottom door of the boss room
                                    current_room.doors["bottom"] = True
                                    # Open the top door of the angel room
                                    game.floor.rooms[new_pos].doors["top"] = True
                        # Spawn particles when enemy dies
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

        # Draw tears
        for tear in isaac.tears:
            if tear.update(current_room):  # If tear hits wall
                isaac.tears.remove(tear)
                continue
            tear.draw()

        if keys[pygame.K_TAB]:
          draw_stats(isaac)

        # Draw Isaac
        isaac.draw()

        # Draw pickup text if active
        if isaac.pickup_timer > 0:
            font = pygame.font.SysFont("Arial", 24)
            text = font.render(isaac.pickup_text, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
            isaac.pickup_timer -= 1

        # Draw cheats if enabled
        if CHEATS_ENABLED:
            font = pygame.font.SysFont("Arial", 20)
            cheat_text = font.render("TRICHE ACTIVÉ", True, RED)
            screen.blit(cheat_text, (10, 10))

            cheats_list = [
                "1: Vie Maximum",
                "2: Dégâts +",
                "3: +50 Pièces",
                "4: Cadence +",
                "5: Brimstone",
                "6: Triple Tir",
                "7: Tirs Guidés",
                "8: Tirs Explosifs",
                "9: Tirs Spectraux",
                "0: Vider Salle",
            ]

            for i, cheat in enumerate(cheats_list):
                text = font.render(cheat, True, WHITE)
                screen.blit(text, (10, 40 + i * 20))

        # Draw minimap
        game.draw_minimap()

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

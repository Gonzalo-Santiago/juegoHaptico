import ctypes
import os
import random
import math
try:
    import pygame
except ImportError:
    print("Por favor instala pygame: pip install pygame")
    exit(1)

import aircraft_art

# ==========================================
# 1. PUENTE C++ (Haptic Feedback)
# ========================================== 
dll_path = os.path.join(os.path.dirname(__file__), "falcon_bridge.dll")
if not os.path.exists(dll_path):
    print("Error: No se encontró falcon_bridge.dll.")
    exit(1)

falcon = ctypes.CDLL(dll_path)
falcon.init_falcon.restype = ctypes.c_int
falcon.get_position.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
falcon.set_force.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]

# ==========================================
# 2. CONFIGURACIÓN DEL JUEGO Y AUDIO
# ==========================================
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Falcon Strike - Vector Edition")
clock = pygame.time.Clock()

# Colores HUD
WHITE = (255, 255, 255)
RED = (255, 30, 30)
DARK_RED = (150, 0, 0)
CYAN = (0, 255, 255)
HUD_COLOR = (0, 200, 255)
BLACK = (0, 0, 0)

font_large = pygame.font.SysFont("Trebuchet MS", 36, bold=True)
font_small = pygame.font.SysFont("Consolas", 16)

# Fondo espacial simple
img_bg = pygame.Surface((WIDTH, HEIGHT))
img_bg.fill((10, 15, 30))
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)) for _ in range(100)]

# Imágenes Vectoriales
img_player = aircraft_art.draw_player_aircraft(0.7)
img_enemies = [
    aircraft_art.draw_enemy_standard(0.7),
    aircraft_art.draw_enemy_heavy(0.7),
    aircraft_art.draw_enemy_fast(0.7)
]

# Audio
assets_dir = os.path.join(os.path.dirname(__file__), "assets")
try:
    snd_shoot = pygame.mixer.Sound(os.path.join(assets_dir, "shoot.wav"))
    snd_shoot.set_volume(0.3)
    snd_exp = pygame.mixer.Sound(os.path.join(assets_dir, "explosion.wav"))
    snd_exp.set_volume(0.6)
except:
    # Fallback si falló el generador
    class DummySound:
        def play(self): pass
        def set_volume(self, v): pass
    snd_shoot = DummySound()
    snd_exp = DummySound()

# Declaraciones Globales de Grupos
all_sprites = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

# ==========================================
# 3. CLASES DEL JUEGO
# ==========================================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = img_player
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 40
        self.health = 100
        self.lives = 3 # NUEVO: Sistema de vidas
        self.score = 0
        self.tick = 0

    def update_position(self, px, pz):
        cx = WIDTH // 2
        cy = HEIGHT - 200
        
        target_x = cx + (px * 6000)
        target_y = cy - (pz * 6000)
        
        if target_x < 40: target_x = 40
        if target_x > WIDTH - 40: target_x = WIDTH - 40
        if target_y < 100: target_y = 100
        if target_y > HEIGHT - 50: target_y = HEIGHT - 50
        
        self.rect.centerx += int((target_x - self.rect.centerx) * 0.15)
        self.rect.centery += int((target_y - self.rect.centery) * 0.15)

    def draw_thruster(self, surface):
        self.tick += 1
        glow = aircraft_art.draw_thruster_glow(self.tick, 0.7)
        surface.blit(glow, (self.rect.centerx - glow.get_width()//2, self.rect.bottom - 5))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 25))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -25

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 15))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed_y = 12

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        tipo = random.randint(0, 2)
        self.image = img_enemies[tipo]
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(20, WIDTH - 20 - self.rect.width)
        self.rect.y = random.randrange(-150, -40)
        
        if tipo == 2:
            self.speed_y = random.randrange(6, 10)
        elif tipo == 1:
            self.speed_y = random.randrange(2, 4)
        else:
            self.speed_y = random.randrange(3, 7)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(20, WIDTH - 20 - self.rect.width)
            self.rect.y = random.randrange(-100, -40)

        # Probabilidad de disparar (NUEVO)
        if random.random() < 0.01:
            eb = EnemyBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(eb)
            enemy_bullets.add(eb)

class ExplosionParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 6)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 255
        self.color = random.choice([(255, 200, 0), (255, 100, 0), (255, 50, 50)])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 15
        self.size -= 0.1

    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            color = (*self.color, max(0, self.life))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

# ==========================================
# 4. FUNCIONES HUD Y MENÚS
# ==========================================
def draw_hud(surface, player, target_locked):
    pygame.draw.line(surface, HUD_COLOR, (10, 10), (150, 10), 2)
    pygame.draw.line(surface, HUD_COLOR, (10, 10), (10, 50), 2)
    pygame.draw.line(surface, HUD_COLOR, (WIDTH - 150, 10), (WIDTH - 10, 10), 2)
    pygame.draw.line(surface, HUD_COLOR, (WIDTH - 10, 10), (WIDTH - 10, 50), 2)
    
    score_lbl = font_small.render("SCORE", True, HUD_COLOR)
    score_val = font_large.render(f"{player.score:06d}", True, WHITE)
    surface.blit(score_lbl, (20, 15))
    surface.blit(score_val, (20, 30))
    
    health_lbl = font_small.render("HULL INTEGRITY", True, HUD_COLOR)
    surface.blit(health_lbl, (WIDTH - 140, 15))
    
    bar_x, bar_y, bar_w, bar_h = WIDTH - 140, 35, 120, 15
    pygame.draw.rect(surface, DARK_RED, (bar_x, bar_y, bar_w, bar_h))
    
    health_ratio = player.health / 100.0
    current_color = CYAN if player.health > 40 else RED
    pygame.draw.rect(surface, current_color, (bar_x, bar_y, int(bar_w * health_ratio), bar_h))
    
    for i in range(1, 5):
        pygame.draw.line(surface, BLACK, (bar_x + i * (bar_w // 5), bar_y), (bar_x + i * (bar_w // 5), bar_y + bar_h), 2)

    # Indicador de Vidas
    lives_lbl = font_small.render("LIVES", True, HUD_COLOR)
    surface.blit(lives_lbl, (20, 70))
    for i in range(player.lives):
        pygame.draw.rect(surface, CYAN, (20 + (i*15), 90, 10, 10))

    if target_locked:
        pygame.draw.line(surface, RED, (player.rect.centerx, player.rect.top - 10), (player.rect.centerx, 0), 1)
        lock_txt = font_small.render("TARGET LOCKED", True, RED)
        surface.blit(lock_txt, (player.rect.right + 10, player.rect.centery))
    else:
        pygame.draw.line(surface, (0, 100, 100), (player.rect.centerx, player.rect.top - 10), (player.rect.centerx, 0), 1)

# ==========================================
# 5. INICIALIZACIÓN
# ==========================================
print("Conectando con el Novint Falcon...")
if falcon.init_falcon() != 0:
    print("Error conectando al Falcon.")

enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
particles = []

player = Player()
all_sprites.add(player)

for i in range(5):
    e = Enemy()
    all_sprites.add(e)
    enemies.add(e)

px_falcon = ctypes.c_double()
py_falcon = ctypes.c_double()
pz_falcon = ctypes.c_double()

recoil_frames = 0
impact_frames = 0

running = True
game_over = False
last_shot = pygame.time.get_ticks()
shoot_delay = 120

while running:
    # Siempre leemos el falcon para no bloquear el driver
    falcon.get_position(ctypes.byref(px_falcon), ctypes.byref(py_falcon), ctypes.byref(pz_falcon))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    if game_over:
        # PANTALLA GAME OVER
        falcon.set_force(0.0, 0.0, 0.0)
        
        screen.fill((10, 15, 30))
        go_text = font_large.render("G A M E   O V E R", True, RED)
        sc_text = font_medium.render(f"Final Score: {player.score}", True, WHITE)
        ex_text = font_small.render("Cierra la ventana para salir.", True, CYAN)
        
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(sc_text, (WIDTH//2 - sc_text.get_width()//2, HEIGHT//2 + 10))
        screen.blit(ex_text, (WIDTH//2 - ex_text.get_width()//2, HEIGHT//2 + 80))
        
        pygame.display.flip()
        clock.tick(30)
        continue

    # --- JUEGO ACTIVO ---
    target_locked = False
    for enemy in enemies:
        if abs(enemy.rect.centerx - player.rect.centerx) < 35 and enemy.rect.centery < player.rect.centery:
            target_locked = True
            break
            
    keys = pygame.key.get_pressed()
    now = pygame.time.get_ticks()
    
    # DISPARO MANUAL
    if keys[pygame.K_SPACE] and now - last_shot > shoot_delay:
        last_shot = now
        snd_shoot.play()
        b1 = Bullet(player.rect.centerx - 15, player.rect.top + 10)
        b2 = Bullet(player.rect.centerx + 15, player.rect.top + 10)
        all_sprites.add(b1, b2)
        bullets.add(b1, b2)
        recoil_frames = 3

    player.update_position(px_falcon.value, pz_falcon.value)
    all_sprites.update()
    
    for p in particles[:]:
        p.update()
        if p.life <= 0:
            particles.remove(p)
            
    # Estrellas
    for i in range(len(stars)):
        x, y, s = stars[i]
        stars[i] = (x, y + s, s)
        if stars[i][1] >= HEIGHT:
            stars[i] = (random.randint(0, WIDTH), 0, s)

    # Colisiones Jugador acierta a Enemigo
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        snd_exp.play()
        player.score += 25
        for _ in range(15):
            particles.append(ExplosionParticle(hit.rect.centerx, hit.rect.centery))
        e = Enemy()
        all_sprites.add(e)
        enemies.add(e)

    # Colisiones Enemigo choca a Jugador
    crash1 = pygame.sprite.spritecollide(player, enemies, True)
    # Colisiones Balas enemigas a Jugador
    crash2 = pygame.sprite.spritecollide(player, enemy_bullets, True)
    
    crash = crash1 + crash2
    for hit in crash:
        snd_exp.play()
        player.health -= 25
        impact_frames = 15
        for _ in range(20):
            particles.append(ExplosionParticle(hit.rect.centerx, hit.rect.centery))
            
        if isinstance(hit, Enemy):
            e = Enemy()
            all_sprites.add(e)
            enemies.add(e)
        
        # Lógica de Vidas
        if player.health <= 0:
            player.lives -= 1
            if player.lives <= 0:
                game_over = True
            else:
                player.health = 100
                player.score = max(0, player.score - 50)

    # --- LÓGICA HÁPTICA ---
    k_resorte = 60.0
    f_x = -k_resorte * px_falcon.value
    f_y = -(k_resorte * 0.5) * py_falcon.value 
    f_z = -k_resorte * pz_falcon.value
    
    if recoil_frames > 0:
        f_z += 3.0 
        recoil_frames -= 1
        
    if impact_frames > 0:
        f_x += random.uniform(-8.0, 8.0)
        f_z += random.uniform(-8.0, 8.0)
        impact_frames -= 1

    falcon.set_force(f_x, f_y, f_z)

    # --- RENDERIZADO ---
    screen.fill((10, 15, 30))
    for x, y, s in stars:
        pygame.draw.circle(screen, WHITE, (x, y), s)
        
    player.draw_thruster(screen)
    all_sprites.draw(screen)
    for p in particles:
        p.draw(screen)
        
    draw_hud(screen, player, target_locked)
    
    pygame.display.flip()
    clock.tick(60)

print("Cerrando Falcon...")
falcon.close_falcon()
pygame.quit()
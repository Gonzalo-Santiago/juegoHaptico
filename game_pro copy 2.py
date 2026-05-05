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

# NUEVO: Intentar cargar la función de botones del Falcon
try:
    falcon.get_buttons.restype = ctypes.c_int
    soporte_botones_falcon = True
    print("Soporte de botones del Falcon: ACTIVADO")
except AttributeError:
    soporte_botones_falcon = False
    print("ADVERTENCIA: falcon_bridge.dll no tiene get_buttons(). Actualiza tu DLL en C++ para usar los botones físicos. Usando teclado temporalmente...")

# ==========================================
# 2. CONFIGURACIÓN DEL JUEGO Y AUDIO
# ==========================================
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Falcon Strike - Infinite Arcade Edition")
clock = pygame.time.Clock()

# Colores HUD
WHITE = (255, 255, 255)
RED = (255, 30, 30)
DARK_RED = (150, 0, 0)
CYAN = (0, 255, 255)
HUD_COLOR = (0, 200, 255)
BLACK = (0, 0, 0)
PURPLE = (150, 0, 255)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)

font_large = pygame.font.SysFont("Trebuchet MS", 36, bold=True)
font_medium = pygame.font.SysFont("Trebuchet MS", 24, bold=True)
font_small = pygame.font.SysFont("Consolas", 16)

img_bg = pygame.Surface((WIDTH, HEIGHT))
img_bg.fill((10, 15, 30))
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)) for _ in range(100)]

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
    class DummySound:
        def play(self): pass
        def set_volume(self, v): pass
    snd_shoot = DummySound()
    snd_exp = DummySound()

all_sprites = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
black_holes = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
particles = []

# Variable de Dificultad Global
ENEMY_SPEED_BOOST = 0

# ==========================================
# 3. CLASES DEL JUEGO AVANZADAS
# ==========================================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = img_player
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 40
        self.health = 100
        self.lives = 3
        self.score = 0
        self.tick = 0
        self.speed_factor = 0.15 
        self.last_target_x = self.rect.centerx
        self.last_target_y = self.rect.centery
        
        self.shield_active = False
        self.spread_timer = 0

    def update_position(self, px, pz):
        cx = WIDTH // 2
        cy = HEIGHT - 200
        
        target_x = cx - (px * 6000)
        target_y = cy - (pz * 6000)
        
        if target_x < 40: target_x = 40
        if target_x > WIDTH - 40: target_x = WIDTH - 40
        if target_y < 100: target_y = 100
        if target_y > HEIGHT - 50: target_y = HEIGHT - 50
        
        if abs(target_x - self.last_target_x) < 8 and abs(target_y - self.last_target_y) < 8:
            target_x = self.last_target_x
            target_y = self.last_target_y
            
        self.last_target_x = target_x
        self.last_target_y = target_y
        self.rect.centerx += int((target_x - self.rect.centerx) * self.speed_factor)
        self.rect.centery += int((target_y - self.rect.centery) * self.speed_factor)

        if self.spread_timer > 0:
            self.spread_timer -= 1

    def draw_thruster(self, surface):
        self.tick += 1
        glow = aircraft_art.draw_thruster_glow(self.tick, 0.7)
        surface.blit(glow, (self.rect.centerx - glow.get_width()//2, self.rect.bottom - 5))
        if self.shield_active:
            pygame.draw.circle(surface, GREEN, self.rect.center, 40, 2)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.type = random.choice(["SHIELD", "SPREAD"])
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN if self.type == "SHIELD" else YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed_y = 4
    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT: self.kill()

class BlackHole(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(100, WIDTH - 100)
        self.rect.y = -100
        self.speed_y = 2
        self.tick = 0
    def update(self):
        self.tick += 5
        self.rect.y += self.speed_y
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, PURPLE, (40, 40), 30 + math.sin(math.radians(self.tick))*5, 2)
        pygame.draw.circle(self.image, BLACK, (40, 40), 25)
        if self.rect.top > HEIGHT: self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        raw_img = img_enemies[1]
        self.image = pygame.transform.scale(raw_img, (raw_img.get_width()*3, raw_img.get_height()*3))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = -50
        self.hp = 1000
        self.max_hp = 1000
        self.state = "ENTER"
        self.speed_x = 3
    def update(self):
        if self.state == "ENTER":
            self.rect.y += 2
            if self.rect.top >= 20: self.state = "FIGHT"
        elif self.state == "FIGHT":
            self.rect.x += self.speed_x
            if self.rect.left < 20 or self.rect.right > WIDTH - 20: self.speed_x *= -1
            if random.random() < 0.08:
                eb = EnemyBullet(self.rect.centerx, self.rect.bottom)
                all_sprites.add(eb)
                enemy_bullets.add(eb)

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
        if self.rect.bottom < 0: self.kill()

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
        if self.rect.top > HEIGHT: self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        tipo = random.randint(0, 2)
        self.image = img_enemies[tipo]
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(20, WIDTH - 20 - self.rect.width)
        self.rect.y = random.randrange(-150, -40)
        
        if tipo == 2: self.speed_y = random.randrange(6, 10)
        elif tipo == 1: self.speed_y = random.randrange(2, 4)
        else: self.speed_y = random.randrange(3, 7)
        self.speed_y += ENEMY_SPEED_BOOST

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(20, WIDTH - 20 - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
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
# 4. HUD
# ==========================================
def draw_hud(surface, player, target_locked, current_distance, boss=None):
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
    
    lives_lbl = font_small.render("LIVES", True, HUD_COLOR)
    surface.blit(lives_lbl, (20, 70))
    for i in range(player.lives):
        pygame.draw.rect(surface, CYAN, (20 + (i*15), 90, 10, 10))

    dist_lbl = font_small.render("DISTANCE", True, HUD_COLOR)
    dist_val = font_medium.render(f"{int(current_distance)} M", True, WHITE)
    surface.blit(dist_lbl, (WIDTH - 140, 65))
    surface.blit(dist_val, (WIDTH - 140, 80))

    if boss and boss.state == "FIGHT":
        pygame.draw.rect(surface, DARK_RED, (100, HEIGHT - 30, WIDTH - 200, 15))
        boss_ratio = max(0, boss.hp / boss.max_hp)
        pygame.draw.rect(surface, RED, (100, HEIGHT - 30, int((WIDTH - 200) * boss_ratio), 15))
        b_lbl = font_small.render("BOSS SIGNAL", True, WHITE)
        surface.blit(b_lbl, (WIDTH//2 - b_lbl.get_width()//2, HEIGHT - 50))

    if target_locked:
        pygame.draw.line(surface, RED, (player.rect.centerx, player.rect.top - 10), (player.rect.centerx, 0), 1)
        lock_txt = font_small.render("TARGET LOCKED", True, RED)
        surface.blit(lock_txt, (player.rect.right + 10, player.rect.centery))

# ==========================================
# 5. INICIALIZACIÓN Y BUCLE PRINCIPAL
# ==========================================
print("Conectando con el Novint Falcon...")
if falcon.init_falcon() != 0:
    print("Error conectando al Falcon.")

player = Player()
all_sprites.add(player)

for i in range(5):
    e = Enemy()
    all_sprites.add(e)
    enemies.add(e)

px_falcon, py_falcon, pz_falcon = ctypes.c_double(), ctypes.c_double(), ctypes.c_double()

recoil_frames = 0
impact_frames = 0
running = True
game_over = False
is_paused = False
last_shot = pygame.time.get_ticks()
shoot_delay = 120

game_distance = 0.0
last_level_boosted = 0
boss_active = False
current_boss = None
level_msg_timer = 0
level_msg_text = ""

# NUEVO: Variables de anti-rebote para los botones del Falcon
last_btn_pausa = False
last_btn_reinicio = False

try:
 while running:
    falcon.get_position(ctypes.byref(px_falcon), ctypes.byref(py_falcon), ctypes.byref(pz_falcon))
    
    # NUEVO: Lectura de botones del Falcon
    btn_disparo = False
    btn_pausa = False
    btn_reinicio = False
    
    if soporte_botones_falcon:
        # La DLL debe retornar un int con la máscara de bits de los botones pulsados
        estado_botones = falcon.get_buttons()
        # Puedes ajustar los números (1, 2, 4) según cómo estén cableados tus botones físicos
        btn_disparo = (estado_botones & 1) != 0   # Botón Central/Principal
        btn_pausa = (estado_botones & 2) != 0     # Botón Izquierdo
        btn_reinicio = (estado_botones & 4) != 0  # Botón Derecho/Arriba
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Mantenemos el teclado SOLO como plan de respaldo si la DLL falla
        if event.type == pygame.KEYDOWN and not soporte_botones_falcon:
            if event.key == pygame.K_p: btn_pausa = True
            if event.key == pygame.K_r: btn_reinicio = True

    # Lógica de Pausa (Usa el botón del Falcon)
    if btn_pausa and not last_btn_pausa:
        if not game_over:
            is_paused = not is_paused
    last_btn_pausa = btn_pausa

    # Lógica de Reinicio (Usa el botón del Falcon)
    if btn_reinicio and not last_btn_reinicio:
        if game_over or is_paused:
            game_over = is_paused = boss_active = False
            game_distance = ENEMY_SPEED_BOOST = 0.0
            last_level_boosted = 0
            current_boss = None
            
            player.health, player.lives, player.score = 100, 3, 0
            player.shield_active = False
            player.spread_timer = 0
            player.speed_factor = 0.15
            player.rect.centerx, player.rect.bottom = WIDTH // 2, HEIGHT - 40
            
            for g in [enemies, bullets, enemy_bullets, powerups, black_holes, boss_group]:
                for sprite in g: sprite.kill()
            particles.clear()
            
            for i in range(5):
                e = Enemy()
                all_sprites.add(e)
                enemies.add(e)
    last_btn_reinicio = btn_reinicio

    if game_over:
        falcon.set_force(0.0, 0.0, 0.0)
        screen.fill((10, 15, 30))
        go_text = font_large.render("G A M E   O V E R", True, RED)
        sc_text = font_medium.render(f"Final Score: {player.score}", True, WHITE)
        # Texto actualizado para reflejar que usa botones del dispositivo
        ex_text = font_small.render("Usa el BOTÓN DERECHO del Falcon para Reiniciar.", True, CYAN)
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(sc_text, (WIDTH//2 - sc_text.get_width()//2, HEIGHT//2 + 10))
        screen.blit(ex_text, (WIDTH//2 - ex_text.get_width()//2, HEIGHT//2 + 80))
        pygame.display.flip()
        clock.tick(30)
        continue

    if is_paused:
        falcon.set_force(0.0, 0.0, 0.0) 
        screen.fill((10, 15, 30))
        for x, y, s in stars: pygame.draw.circle(screen, WHITE, (x, y), s)
        all_sprites.draw(screen)
        for p in particles: p.draw(screen)
        draw_hud(screen, player, False, game_distance, current_boss)
        
        overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(150); overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        pause_txt = font_large.render("P A U S A", True, HUD_COLOR)
        # Texto actualizado para reflejar que usa botones del dispositivo
        resume_txt = font_small.render("Pausa (Botón Izquierdo) | Reiniciar (Botón Derecho)", True, WHITE)
        screen.blit(pause_txt, (WIDTH//2 - pause_txt.get_width()//2, HEIGHT//2 - 20))
        screen.blit(resume_txt, (WIDTH//2 - resume_txt.get_width()//2, HEIGHT//2 + 30))
        pygame.display.flip()
        clock.tick(30)
        continue

    # --- JUEGO ACTIVO ---
    
    if not boss_active:
        game_distance += 0.05  
    
    current_level = int(game_distance // 100)
    
    if current_level > last_level_boosted:
        last_level_boosted = current_level
        
        if current_level % 2 == 0 and current_level > 0:
            boss_active = True
            current_boss = Boss()
            current_boss.hp = 1000 + (current_level * 250)
            current_boss.max_hp = current_boss.hp
            all_sprites.add(current_boss)
            boss_group.add(current_boss)
            
            for e in enemies: e.kill() 
            
            level_msg_timer = 180
            level_msg_text = f"¡ALERTA: NAVE NODRIZA MK-{current_level//2} DETECTADA!"
        else:
            if player.speed_factor < 0.6: 
                player.speed_factor += 0.05  
            ENEMY_SPEED_BOOST += 1.5       
            for e in enemies: e.speed_y += 1.5
            
            level_msg_timer = 180       
            level_msg_text = f"NIVEL {current_level}: ¡VELOCIDAD AUMENTADA!"

    if random.random() < 0.002 and not boss_active:
        bh = BlackHole()
        all_sprites.add(bh)
        black_holes.add(bh)

    target_locked = any(abs(e.rect.centerx - player.rect.centerx) < 35 and e.rect.centery < player.rect.centery for e in enemies)
    if current_boss and abs(current_boss.rect.centerx - player.rect.centerx) < 50: target_locked = True
            
    # Lógica de disparo actualizada (Ahora lee el botón central del Falcon o la tecla Espacio si la DLL falla)
    keys = pygame.key.get_pressed()
    now = pygame.time.get_ticks()
    
    condicion_disparo = btn_disparo if soporte_botones_falcon else keys[pygame.K_SPACE]
    
    if condicion_disparo and now - last_shot > shoot_delay:
        last_shot = now
        snd_shoot.play()
        if player.spread_timer > 0:
            b1 = Bullet(player.rect.centerx - 25, player.rect.top + 10)
            b2 = Bullet(player.rect.centerx, player.rect.top)
            b3 = Bullet(player.rect.centerx + 25, player.rect.top + 10)
            all_sprites.add(b1, b2, b3)
            bullets.add(b1, b2, b3)
        else:
            b1 = Bullet(player.rect.centerx - 15, player.rect.top + 10)
            b2 = Bullet(player.rect.centerx + 15, player.rect.top + 10)
            all_sprites.add(b1, b2)
            bullets.add(b1, b2)
        recoil_frames = 3

    player.update_position(px_falcon.value, pz_falcon.value)
    all_sprites.update()
    for p in particles[:]:
        p.update()
        if p.life <= 0: particles.remove(p)
    for i in range(len(stars)):
        x, y, s = stars[i]
        stars[i] = (x, y + s if not boss_active else y + (s * 0.2), s) 
        if stars[i][1] >= HEIGHT: stars[i] = (random.randint(0, WIDTH), 0, s)

    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        snd_exp.play()
        player.score += 25
        for _ in range(15): particles.append(ExplosionParticle(hit.rect.centerx, hit.rect.centery))
        
        if random.random() < 0.15:
            pu = PowerUp(hit.rect.centerx, hit.rect.centery)
            all_sprites.add(pu)
            powerups.add(pu)
            
        e = Enemy()
        all_sprites.add(e)
        enemies.add(e)

    boss_hits = pygame.sprite.groupcollide(boss_group, bullets, False, True)
    for boss, bullet_list in boss_hits.items():
        boss.hp -= 25 * len(bullet_list)
        snd_exp.play()
        for _ in range(5): particles.append(ExplosionParticle(boss.rect.centerx + random.randint(-50,50), boss.rect.centery))
        if boss.hp <= 0:
            player.score += 1500
            boss.kill()
            current_boss = None
            boss_active = False
            for _ in range(50): particles.append(ExplosionParticle(boss.rect.centerx, boss.rect.centery))
            
            for i in range(5):
                e = Enemy()
                all_sprites.add(e)
                enemies.add(e)

    pu_hits = pygame.sprite.spritecollide(player, powerups, True)
    for pu in pu_hits:
        if pu.type == "SHIELD": player.shield_active = True
        elif pu.type == "SPREAD": player.spread_timer = 600 

    crash = pygame.sprite.spritecollide(player, enemies, True) + pygame.sprite.spritecollide(player, enemy_bullets, True)
    if current_boss and pygame.sprite.collide_rect(player, current_boss):
        crash.append(current_boss)

    for hit in crash:
        impact_frames = 15
        if player.shield_active:
            player.shield_active = False 
            snd_exp.play()
        else:
            snd_exp.play()
            player.health -= 25
            for _ in range(20): particles.append(ExplosionParticle(hit.rect.centerx, hit.rect.centery))
            
            if player.health <= 0:
                player.lives -= 1
                if player.lives <= 0: game_over = True
                else:
                    player.health = 100
                    player.score = max(0, player.score - 50)
                    player.shield_active = True 

        if isinstance(hit, Enemy):
            e = Enemy()
            all_sprites.add(e)
            enemies.add(e)

    # --- LÓGICA HÁPTICA (FÍSICA DEL FALCON) ---
    f_x = 0.0  
    f_y = -30.0 * py_falcon.value 
    f_z = 0.0
    
    for bh in black_holes:
        dx = bh.rect.centerx - player.rect.centerx
        dy = bh.rect.centery - player.rect.centery
        dist = math.hypot(dx, dy)
        if 20 < dist < 300: 
            fuerza_gravedad = 150.0 / dist
            f_x += (dx / dist) * fuerza_gravedad
            f_z -= (dy / dist) * fuerza_gravedad 

    if current_boss and current_boss.state == "FIGHT":
        f_y += random.uniform(-0.5, 0.5) 
    
    if recoil_frames > 0:
        f_z += 3.0 
        recoil_frames -= 1
        
    if impact_frames > 0:
        f_x += random.uniform(-3.5, 3.5)
        f_z += random.uniform(-3.5, 3.5)
        impact_frames -= 1

    falcon.set_force(f_x, f_y, f_z)

    # --- RENDERIZADO ---
    screen.fill((10, 15, 30))
    for x, y, s in stars: pygame.draw.circle(screen, WHITE, (x, y), s)
    player.draw_thruster(screen)
    all_sprites.draw(screen)
    for p in particles: p.draw(screen)
        
    draw_hud(screen, player, target_locked, game_distance, current_boss)
    
    if level_msg_timer > 0:
        msg_bg = pygame.Surface((WIDTH, 60)); msg_bg.set_alpha(150); msg_bg.fill(BLACK)
        screen.blit(msg_bg, (0, HEIGHT//2 - 30))
        
        warn_txt = font_medium.render(level_msg_text, True, RED if boss_active else HUD_COLOR)
        screen.blit(warn_txt, (WIDTH//2 - warn_txt.get_width()//2, HEIGHT//2 - warn_txt.get_height()//2))
        level_msg_timer -= 1
    
    pygame.display.flip()
    clock.tick(60)

except KeyboardInterrupt:
    pass
finally:
    print("Cerrando Falcon...")
    falcon.close_falcon()
    pygame.quit()
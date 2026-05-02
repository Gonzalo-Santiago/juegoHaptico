"""
aircraft_art.py  —  Funciones de dibujo vectorial para aviones
Devuelve pygame.Surface con SRCALPHA con aviones de alta calidad.
"""
import pygame
import math


# ─── paleta compartida ───────────────────────────────────────────────
BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
CYAN    = (  0, 220, 255)
RED     = (255,  40,  40)
ORANGE  = (255, 140,   0)
YELLOW  = (255, 220,   0)
PURPLE  = (160,   0, 220)
GRAY    = (100, 110, 130)
LGRAY   = (160, 170, 190)
DGRAY   = ( 40,  50,  65)
STEEL   = ( 80,  95, 120)
COCKPIT = ( 30, 200, 255)
COCKPIT2= (  0, 100, 180)
EXHAUST = (255, 160,  50)
SHADOW  = (  0,   0,   0, 80)


def _poly(surf, color, pts, width=0):
    pygame.draw.polygon(surf, color, pts, width)

def _line(surf, color, p1, p2, w=1):
    pygame.draw.line(surf, color, p1, p2, w)

def _circle(surf, color, center, r, width=0):
    pygame.draw.circle(surf, color, center, r, width)

def _ellipse(surf, color, rect, width=0):
    pygame.draw.ellipse(surf, color, rect, width)


# ══════════════════════════════════════════════════════════════════════
#   AVIÓN DEL JUGADOR  —  F-22 Raptor estilizado  (90×110 px)
# ══════════════════════════════════════════════════════════════════════
def draw_player_aircraft(scale=1.0):
    W, H = int(90 * scale), int(110 * scale)
    s = scale
    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    cx = W // 2

    # ── sombra suave debajo ──
    shadow = pygame.Surface((W, H), pygame.SRCALPHA)
    _ellipse(shadow, (0, 200, 255, 35), (cx-28, H-22, 56, 14))
    surf.blit(shadow, (0, 0))

    # ── ALERONES TRASEROS (delta) ──
    _poly(surf, STEEL, [
        (cx,      int(H*0.72)),
        (cx-38,   int(H*0.98)),
        (cx-20,   int(H*0.80)),
    ])
    _poly(surf, STEEL, [
        (cx,      int(H*0.72)),
        (cx+38,   int(H*0.98)),
        (cx+20,   int(H*0.80)),
    ])
    # borde iluminado alerones
    _poly(surf, LGRAY, [
        (cx,    int(H*0.72)),
        (cx-38, int(H*0.98)),
        (cx-20, int(H*0.80)),
    ], 1)
    _poly(surf, LGRAY, [
        (cx,    int(H*0.72)),
        (cx+38, int(H*0.98)),
        (cx+20, int(H*0.80)),
    ], 1)

    # ── ALAS PRINCIPALES (delta sweep) ──
    _poly(surf, DGRAY, [
        (cx,      int(H*0.40)),
        (cx-44,   int(H*0.78)),
        (cx-36,   int(H*0.85)),
        (cx-10,   int(H*0.60)),
    ])
    _poly(surf, DGRAY, [
        (cx,      int(H*0.40)),
        (cx+44,   int(H*0.78)),
        (cx+36,   int(H*0.85)),
        (cx+10,   int(H*0.60)),
    ])
    # superficie superior de ala (iluminada)
    _poly(surf, STEEL, [
        (cx,      int(H*0.40)),
        (cx-38,   int(H*0.73)),
        (cx-14,   int(H*0.58)),
    ])
    _poly(surf, STEEL, [
        (cx,      int(H*0.40)),
        (cx+38,   int(H*0.73)),
        (cx+14,   int(H*0.58)),
    ])
    # nervios de ala
    _line(surf, LGRAY, (cx, int(H*0.42)), (cx-36, int(H*0.72)), 1)
    _line(surf, LGRAY, (cx, int(H*0.42)), (cx+36, int(H*0.72)), 1)
    _line(surf, CYAN,  (cx-20, int(H*0.50)), (cx-40, int(H*0.78)), 1)
    _line(surf, CYAN,  (cx+20, int(H*0.50)), (cx+40, int(H*0.78)), 1)

    # ── FUSELAJE central ──
    fuselage_pts = [
        (cx,       int(H*0.02)),   # punta de morro
        (cx+10,    int(H*0.22)),
        (cx+14,    int(H*0.45)),
        (cx+12,    int(H*0.70)),
        (cx+8,     int(H*0.88)),
        (cx,       int(H*0.95)),
        (cx-8,     int(H*0.88)),
        (cx-12,    int(H*0.70)),
        (cx-14,    int(H*0.45)),
        (cx-10,    int(H*0.22)),
    ]
    _poly(surf, GRAY, fuselage_pts)

    # cara iluminada (izquierda = luz)
    lit_pts = [
        (cx,    int(H*0.02)),
        (cx-10, int(H*0.22)),
        (cx-14, int(H*0.45)),
        (cx-10, int(H*0.60)),
        (cx,    int(H*0.55)),
        (cx+8,  int(H*0.35)),
        (cx+8,  int(H*0.18)),
    ]
    _poly(surf, STEEL, lit_pts)

    # línea central de paneles
    _line(surf, DGRAY, (cx, int(H*0.04)), (cx, int(H*0.90)), 1)
    # líneas de panel horizontal
    for frac in [0.28, 0.42, 0.58, 0.70]:
        _line(surf, DGRAY, (cx-12, int(H*frac)), (cx+12, int(H*frac)), 1)

    # ── TOMA DE AIRE (inlet) — laterales ──
    _poly(surf, BLACK, [(cx-12, int(H*0.44)), (cx-16, int(H*0.52)), (cx-8, int(H*0.56)), (cx-6, int(H*0.46))])
    _poly(surf, BLACK, [(cx+12, int(H*0.44)), (cx+16, int(H*0.52)), (cx+8,  int(H*0.56)), (cx+6, int(H*0.46))])
    _poly(surf, DGRAY, [(cx-11, int(H*0.45)), (cx-14, int(H*0.51)), (cx-8, int(H*0.54)), (cx-7, int(H*0.46))])
    _poly(surf, DGRAY, [(cx+11, int(H*0.45)), (cx+14, int(H*0.51)), (cx+8,  int(H*0.54)), (cx+7, int(H*0.46))])

    # ── TOBERAS de motor ──
    _ellipse(surf, DGRAY,  (cx-10, int(H*0.87), 20, 10))
    _ellipse(surf, BLACK,  (cx-8,  int(H*0.88), 16,  7))
    _ellipse(surf, EXHAUST,(cx-6,  int(H*0.89), 12,  5))
    # reflejo de tobera
    _ellipse(surf, (255,200,80,180), (cx-3, int(H*0.895), 6, 2))

    # ── CABINA (canopy) ──
    canopy_pts = [
        (cx,    int(H*0.08)),
        (cx+7,  int(H*0.16)),
        (cx+8,  int(H*0.26)),
        (cx,    int(H*0.30)),
        (cx-8,  int(H*0.26)),
        (cx-7,  int(H*0.16)),
    ]
    _poly(surf, COCKPIT2, canopy_pts)
    _poly(surf, COCKPIT,  [(cx,    int(H*0.09)),
                            (cx+5,  int(H*0.16)),
                            (cx,    int(H*0.20)),
                            (cx-5,  int(H*0.16))])
    # reflejo de canopy
    _poly(surf, (180, 240, 255, 160), [(cx-5, int(H*0.10)), (cx-7, int(H*0.18)), (cx-3, int(H*0.20)), (cx-1, int(H*0.12))])

    # ── CONTORNO general del fuselaje ──
    _poly(surf, CYAN, fuselage_pts, 1)

    # ── LUCES de posición ──
    _circle(surf, (255, 80, 80),  (cx-43, int(H*0.76)), 3)  # rojo — ala izq
    _circle(surf, (80, 255, 80),  (cx+43, int(H*0.76)), 3)  # verde — ala der
    _circle(surf, WHITE,          (cx,    int(H*0.02)), 2)   # blanco — morro

    # ── llama del motor (animable externamente, aquí estática base) ──
    _poly(surf, (255, 120, 0, 180), [
        (cx-5, int(H*0.94)),
        (cx+5, int(H*0.94)),
        (cx+3, int(H*1.00) if int(H*1.00) < H else H-1),
        (cx-3, int(H*1.00) if int(H*1.00) < H else H-1),
    ])

    return surf


# ══════════════════════════════════════════════════════════════════════
#   ENEMIGO TIPO 1  —  Interceptor alienígena angular  (70×75 px)
# ══════════════════════════════════════════════════════════════════════
def draw_enemy_standard(scale=1.0):
    W, H = int(70 * scale), int(75 * scale)
    s = scale
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    # ── alerones traseros angulares ──
    _poly(surf, (100,0,0), [(cx, int(H*0.15)), (cx-32, int(H*0.06)), (cx-28, int(H*0.25))])
    _poly(surf, (100,0,0), [(cx, int(H*0.15)), (cx+32, int(H*0.06)), (cx+28, int(H*0.25))])

    # ── alas sweep inverso (hacia adelante) ──
    _poly(surf, (120, 10, 10), [
        (cx,    int(H*0.50)),
        (cx-36, int(H*0.28)),
        (cx-30, int(H*0.40)),
        (cx-8,  int(H*0.55)),
    ])
    _poly(surf, (120, 10, 10), [
        (cx,    int(H*0.50)),
        (cx+36, int(H*0.28)),
        (cx+30, int(H*0.40)),
        (cx+8,  int(H*0.55)),
    ])
    # cara brillante de ala
    _poly(surf, (180, 20, 20), [(cx, int(H*0.50)), (cx-28, int(H*0.30)), (cx-10, int(H*0.50))])
    _poly(surf, (180, 20, 20), [(cx, int(H*0.50)), (cx+28, int(H*0.30)), (cx+10, int(H*0.50))])
    _line(surf, ORANGE, (cx, int(H*0.50)), (cx-32, int(H*0.28)), 1)
    _line(surf, ORANGE, (cx, int(H*0.50)), (cx+32, int(H*0.28)), 1)

    # ── fuselaje principal ──
    fpts = [
        (cx,    int(H*0.98)),  # punta (abajo = frente en enemigos)
        (cx+11, int(H*0.80)),
        (cx+13, int(H*0.55)),
        (cx+10, int(H*0.30)),
        (cx+6,  int(H*0.10)),
        (cx,    int(H*0.04)),
        (cx-6,  int(H*0.10)),
        (cx-10, int(H*0.30)),
        (cx-13, int(H*0.55)),
        (cx-11, int(H*0.80)),
    ]
    _poly(surf, (90, 10, 10), fpts)
    # cara iluminada
    _poly(surf, (160, 20, 20), [
        (cx,    int(H*0.98)),
        (cx+11, int(H*0.80)),
        (cx+13, int(H*0.55)),
        (cx+8,  int(H*0.35)),
        (cx,    int(H*0.40)),
        (cx-6,  int(H*0.68)),
    ])

    # paneles
    _line(surf, (60,0,0), (cx, int(H*0.10)), (cx, int(H*0.95)), 1)
    for frac in [0.30, 0.50, 0.68]:
        _line(surf, (60,0,0), (cx-10, int(H*frac)), (cx+10, int(H*frac)), 1)

    # ── cañones / tomas de energía ──
    _poly(surf, BLACK, [(cx-4, int(H*0.92)), (cx+4, int(H*0.92)), (cx+3, int(H*0.99)), (cx-3, int(H*0.99))])
    _ellipse(surf, (200, 0, 0), (cx-3, int(H*0.93), 6, 4))

    # ── sensor dome (cabina) ──
    _ellipse(surf, (40,0,0),  (cx-8, int(H*0.08), 16, 14))
    _ellipse(surf, (200,0,0), (cx-5, int(H*0.09), 10,  9))
    _poly(surf, (255, 60, 60, 180), [(cx-3, int(H*0.10)), (cx, int(H*0.12)), (cx-4, int(H*0.16))])

    # ── contorno ──
    _poly(surf, ORANGE, fpts, 1)

    # ── toberas (arriba = escape) ──
    _ellipse(surf, (60,0,0),   (cx-9, int(H*0.02), 18, 8))
    _ellipse(surf, BLACK,      (cx-7, int(H*0.03), 14, 5))
    _ellipse(surf, (255,80,0), (cx-5, int(H*0.04), 10, 3))

    # luces hostiles
    _circle(surf, (255, 50, 0), (cx-34, int(H*0.30)), 3)
    _circle(surf, (255, 50, 0), (cx+34, int(H*0.30)), 3)

    return surf


# ══════════════════════════════════════════════════════════════════════
#   ENEMIGO TIPO 2  —  Bombardero pesado "Titan"  (80×70 px)
# ══════════════════════════════════════════════════════════════════════
def draw_enemy_heavy(scale=1.0):
    W, H = int(80 * scale), int(70 * scale)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    # color base púrpura oscuro
    C1 = (60,  0, 100)
    C2 = (100, 0, 160)
    C3 = (140, 0, 200)

    # ── alas grandes rectangulares/trapezoidales ──
    _poly(surf, C1, [(cx-8, int(H*0.35)), (cx-40, int(H*0.20)), (cx-42, int(H*0.60)), (cx-8, int(H*0.65))])
    _poly(surf, C1, [(cx+8, int(H*0.35)), (cx+40, int(H*0.20)), (cx+42, int(H*0.60)), (cx+8, int(H*0.65))])
    _poly(surf, C2, [(cx-8, int(H*0.35)), (cx-35, int(H*0.22)), (cx-36, int(H*0.50)), (cx-8, int(H*0.52))])
    _poly(surf, C2, [(cx+8, int(H*0.35)), (cx+35, int(H*0.22)), (cx+36, int(H*0.50)), (cx+8, int(H*0.52))])
    # nervios
    for xi in [0.55, 0.72, 0.88]:
        _line(surf, C3, (cx - int(40*xi), int(H*0.22)), (cx - int(40*xi), int(H*0.58)), 1)
        _line(surf, C3, (cx + int(40*xi), int(H*0.22)), (cx + int(40*xi), int(H*0.58)), 1)

    # ── motores bajo las alas ──
    for xoff in [-28, -14, 14, 28]:
        mx = cx + xoff
        _ellipse(surf, C1,  (mx-5, int(H*0.55), 10, 18))
        _ellipse(surf, BLACK,(mx-4, int(H*0.56),  8, 15))
        _ellipse(surf, (200, 0, 255, 200), (mx-3, int(H*0.62), 6, 5))

    # ── fuselaje ancho (bombardero) ──
    fpts = [
        (cx,    int(H*0.98)),
        (cx+16, int(H*0.82)),
        (cx+18, int(H*0.50)),
        (cx+14, int(H*0.20)),
        (cx+8,  int(H*0.05)),
        (cx,    int(H*0.02)),
        (cx-8,  int(H*0.05)),
        (cx-14, int(H*0.20)),
        (cx-18, int(H*0.50)),
        (cx-16, int(H*0.82)),
    ]
    _poly(surf, C1, fpts)
    _poly(surf, C2, [
        (cx,    int(H*0.98)),
        (cx+16, int(H*0.82)),
        (cx+16, int(H*0.50)),
        (cx+10, int(H*0.25)),
        (cx,    int(H*0.30)),
    ])

    # paneles de blindaje
    for frac in [0.35, 0.52, 0.68, 0.80]:
        _line(surf, C3, (cx-16, int(H*frac)), (cx+16, int(H*frac)), 1)
    _line(surf, PURPLE, (cx, int(H*0.05)), (cx, int(H*0.95)), 1)

    # ── domo de arma frontal ──
    _ellipse(surf, C1, (cx-10, int(H*0.88), 20, 12))
    _ellipse(surf, (180,0,255), (cx-6, int(H*0.90), 12, 7))
    _circle(surf, (220, 0, 255), (cx, int(H*0.93)), 3)

    # ── cabina blindada ──
    _ellipse(surf, C1,  (cx-10, int(H*0.06), 20, 16))
    _ellipse(surf, (80,0,120), (cx-7, int(H*0.07), 14, 11))
    _poly(surf, (180, 0, 255, 150), [(cx-5, int(H*0.08)), (cx+3, int(H*0.10)), (cx, int(H*0.16)), (cx-5, int(H*0.14))])

    # contorno
    _poly(surf, (200, 0, 255), fpts, 1)

    # luces
    _circle(surf, PURPLE, (cx-40, int(H*0.40)), 3)
    _circle(surf, PURPLE, (cx+40, int(H*0.40)), 3)
    _circle(surf, (220,0,255), (cx, int(H*0.98)), 2)

    return surf


# ══════════════════════════════════════════════════════════════════════
#   ENEMIGO TIPO 3  —  Caza rápido "Phantom"  (55×60 px)
# ══════════════════════════════════════════════════════════════════════
def draw_enemy_fast(scale=1.0):
    W, H = int(55 * scale), int(60 * scale)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    C1 = (140, 80, 0)
    C2 = (200, 120, 0)
    C3 = (255, 180, 0)

    # ── aletas caudales en V ──
    _poly(surf, C1, [(cx, int(H*0.18)), (cx-25, int(H*0.05)), (cx-18, int(H*0.25))])
    _poly(surf, C1, [(cx, int(H*0.18)), (cx+25, int(H*0.05)), (cx+18, int(H*0.25))])

    # ── alas delta delgadas ──
    _poly(surf, C1, [(cx, int(H*0.55)), (cx-28, int(H*0.28)), (cx-20, int(H*0.42)), (cx-5, int(H*0.58))])
    _poly(surf, C1, [(cx, int(H*0.55)), (cx+28, int(H*0.28)), (cx+20, int(H*0.42)), (cx+5, int(H*0.58))])
    _poly(surf, C2, [(cx, int(H*0.55)), (cx-22, int(H*0.30)), (cx-8,  int(H*0.52))])
    _poly(surf, C2, [(cx, int(H*0.55)), (cx+22, int(H*0.30)), (cx+8,  int(H*0.52))])
    _line(surf, C3, (cx, int(H*0.55)), (cx-26, int(H*0.28)), 1)
    _line(surf, C3, (cx, int(H*0.55)), (cx+26, int(H*0.28)), 1)

    # ── fuselaje largo y delgado ──
    fpts = [
        (cx,    int(H*0.98)),
        (cx+7,  int(H*0.78)),
        (cx+9,  int(H*0.50)),
        (cx+7,  int(H*0.25)),
        (cx+4,  int(H*0.06)),
        (cx,    int(H*0.02)),
        (cx-4,  int(H*0.06)),
        (cx-7,  int(H*0.25)),
        (cx-9,  int(H*0.50)),
        (cx-7,  int(H*0.78)),
    ]
    _poly(surf, C1, fpts)
    _poly(surf, C2, [(cx, int(H*0.98)), (cx+7, int(H*0.78)), (cx+7, int(H*0.45)), (cx+4, int(H*0.20)), (cx, int(H*0.28))])

    # líneas de panel
    _line(surf, C3, (cx, int(H*0.06)), (cx, int(H*0.95)), 1)
    for frac in [0.35, 0.52, 0.70]:
        _line(surf, C1, (cx-7, int(H*frac)), (cx+7, int(H*frac)), 1)

    # ── sensor frontal ──
    _ellipse(surf, C1, (cx-5, int(H*0.90), 10, 8))
    _ellipse(surf, C3, (cx-3, int(H*0.91),  6, 5))

    # ── canopy pequeño ──
    _ellipse(surf, (20,10,0),    (cx-5, int(H*0.08), 10, 10))
    _ellipse(surf, (255,160,0),  (cx-3, int(H*0.09),  6,  7))
    _poly(surf, (255,220,100,160), [(cx-2, int(H*0.10)), (cx+2, int(H*0.11)), (cx, int(H*0.15))])

    # contorno
    _poly(surf, YELLOW, fpts, 1)

    # ── toberas dobles ──
    for xoff in [-4, 4]:
        _ellipse(surf, C1,  (cx+xoff-4, int(H*0.01), 8, 5))
        _ellipse(surf, BLACK,(cx+xoff-3, int(H*0.02), 6, 3))
        _ellipse(surf, (255,200,0,200),(cx+xoff-2, int(H*0.025), 4, 2))

    # luces
    _circle(surf, ORANGE, (cx-26, int(H*0.30)), 2)
    _circle(surf, ORANGE, (cx+26, int(H*0.30)), 2)

    return surf


# ══════════════════════════════════════════════════════════════════════
#   THRUSTER GLOW  —  llama animada para el jugador
# ══════════════════════════════════════════════════════════════════════
def draw_thruster_glow(tick, scale=1.0):
    """Devuelve una Surface con la llama del motor (animada por tick)."""
    W, H = int(30*scale), int(40*scale)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2
    flicker = math.sin(tick * 0.4) * 0.3 + 0.7
    length = int(H * flicker)

    for i, (col, frac) in enumerate([
        ((255, 200, 80, 200), 1.0),
        ((255, 120, 20, 160), 0.7),
        ((255,  60,  0, 100), 0.5),
    ]):
        pts = [
            (cx - int(5*frac), 0),
            (cx + int(5*frac), 0),
            (cx + int(2*frac), int(length*frac)),
            (cx,               int(length)),
            (cx - int(2*frac), int(length*frac)),
        ]
        _poly(surf, col, pts)

    return surf
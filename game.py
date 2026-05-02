import ctypes
import os
import time

# Intenta importar pygame. Si no está, avisa al usuario.
try:
    import pygame
except ImportError:
    print("Error: Pygame no está instalado. Ejecuta 'pip install pygame' en tu terminal.")
    exit(1)

# ==========================================
# 1. CARGAR LA LIBRERÍA (DLL DE C++)
# ==========================================
# Carga la DLL compilada. Asegúrate de compilarla primero (revisa el README.md).
# En Windows el archivo se llamará falcon_bridge.dll (o libfalcon_bridge.dll dependiendo del compilador)
dll_path = os.path.join(os.path.dirname(__file__), "falcon_bridge.dll")
if not os.path.exists(dll_path):
    dll_path = os.path.join(os.path.dirname(__file__), "libfalcon_bridge.dll")

if not os.path.exists(dll_path):
    print("Error: No se encontró la DLL. Debes compilar el código C++ primero.")
    exit(1)

# Cargar mediante ctypes
falcon = ctypes.CDLL(dll_path)

# Configurar tipos de retorno y argumentos para que Python y C++ se entiendan
falcon.init_falcon.restype = ctypes.c_int

# get_position recibe punteros a double
falcon.get_position.argtypes = [
    ctypes.POINTER(ctypes.c_double), 
    ctypes.POINTER(ctypes.c_double), 
    ctypes.POINTER(ctypes.c_double)
]

# set_force recibe tres doubles por valor
falcon.set_force.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]

# ==========================================
# 2. INICIALIZAR PYGAME Y EL JUEGO
# ==========================================
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Novint Falcon - Pygame Bridge")
clock = pygame.time.Clock()

# Inicializar Falcon
print("Iniciando Falcon...")
if falcon.init_falcon() != 0:
    print("Hubo un problema iniciando el Falcon.")

# Variables para guardar las lecturas
px = ctypes.c_double()
py = ctypes.c_double()
pz = ctypes.c_double()

running = True
print("Juego corriendo. Presiona la 'X' en la ventana para salir.")

# Círculo central interactivo (un "resorte")
centro_x, centro_y = WIDTH // 2, HEIGHT // 2

while running:
    # 1. Manejar eventos (cerrar ventana)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Leer la posición del Novint Falcon desde C++
    falcon.get_position(ctypes.byref(px), ctypes.byref(py), ctypes.byref(pz))
    # El Novint Falcon reporta la posición en Metros (usualmente un rango de -0.06m a 0.06m).
    # Multiplicamos por 4000 para mapearlo a píxeles en la pantalla:
    cursor_x = centro_x + int(px.value * 4000)
    # Invertimos el eje Y porque en gráficas Y crece hacia abajo, pero en el Falcon Y crece hacia arriba
    cursor_y = centro_y - int(py.value * 4000)

    # 3. Lógica del juego y cálculo de fuerzas (Haptic Feedback)
    # Por ejemplo, un resorte que tira del usuario hacia el centro si se aleja mucho
    distancia_x = px.value - 0.0
    distancia_y = py.value - 0.0
    
    # Ley de Hooke: F = -k * x
    # Tu posición estaba en 0.009m. Con k=80 apenas mandaba 0.7 Newtons (muy débil).
    # Con k=400, enviará casi 4 Newtons de fuerza, lo cual es muy fuerte.
    k_resorte = 400.0 
    fuerza_x = -k_resorte * distancia_x
    fuerza_y = -k_resorte * distancia_y
    fuerza_z = 0.0
    
    # 4. Enviar fuerzas calculadas al C++
    falcon.set_force(fuerza_x, fuerza_y, fuerza_z)

    # 5. Renderizado en Pygame
    screen.fill((30, 30, 30)) # Fondo oscuro
    
    # Dibujar el "centro" del resorte
    pygame.draw.circle(screen, (100, 100, 255), (centro_x, centro_y), 10)
    
    # Dibujar la posición del Falcon
    pygame.draw.circle(screen, (255, 100, 100), (cursor_x, cursor_y), 20)
    
    # Dibujar una línea conectando ambos (el resorte)
    pygame.draw.line(screen, (200, 200, 200), (centro_x, centro_y), (cursor_x, cursor_y), 3)

    pygame.display.flip()
    
    # Limitar a 60 FPS (El hilo de C++ debe correr a su propia velocidad internamente)
    clock.tick(60)

# ==========================================
# 3. CERRAR TODO LIMPIAMENTE
# ==========================================
print("Cerrando Falcon...")
falcon.close_falcon()
pygame.quit()
print("Terminado.")

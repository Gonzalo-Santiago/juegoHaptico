#include <iostream>
#include <atomic>
#include <windows.h>
#include "dhdc.h" // Cabecera del Force Dimension SDK
#include "drdc.h" // Cabecera de la librería robótica (necesaria para inicializar el Falcon)

// Definir macro de exportación para Windows
#ifdef _WIN32
    #define EXPORT extern "C" __declspec(dllexport)
#else
    #define EXPORT extern "C"
#endif

// Variables globales para el estado del control
std::atomic<double> g_posX(0.0);
std::atomic<double> g_posY(0.0);
std::atomic<double> g_posZ(0.0);

std::atomic<double> g_forceX(0.0);
std::atomic<double> g_forceY(0.0);
std::atomic<double> g_forceZ(0.0);

std::atomic<bool> g_isRunning(false);
HANDLE g_hapticThread = NULL;
int g_deviceId = -1;

// Función que mantiene el bucle de hardware a alta frecuencia
DWORD WINAPI hapticLoop(LPVOID lpParam) {
    std::cout << "[C++] Iniciando hilo háptico del Novint Falcon..." << std::endl;
    
    // Conectar al dispositivo
    g_deviceId = dhdOpen();
    if (g_deviceId < 0) {
        std::cout << "[C++] Error: No se pudo abrir el dispositivo. (" << dhdErrorGetLastStr() << ")" << std::endl;
        g_isRunning = false;
        return 1;
    }
    
    std::cout << "[C++] Falcon conectado: " << dhdGetSystemName() << std::endl;
    
    // Encender los motores manualmente por seguridad
    if (dhdEnableForce(DHD_ON, g_deviceId) < 0) {
        std::cout << "[C++] Error: No se pudo habilitar la fuerza en los motores." << std::endl;
    } else {
        std::cout << "[C++] Motores habilitados correctamente." << std::endl;
        std::cout << "[INFO] Si la luz está en ROJO, por favor empuja la bola hacia adentro y sácala por completo para calibrarlo manualmente." << std::endl;
    }
    
    int iteracion = 0;
    
    // Bucle principal de control
    while (g_isRunning) {
        double px, py, pz;
        // Leer la posición actual del hardware
        if (dhdGetPosition(&px, &py, &pz) >= 0) {
            g_posX = px;
            g_posY = py;
            g_posZ = pz;
        }

        // Leer fuerzas que Python configuró
        double fx = g_forceX.load();
        double fy = g_forceY.load();
        double fz = g_forceZ.load();

        // Imprimir depuración cada 1000 ciclos (~1 segundo)
        if (iteracion++ % 1000 == 0) {
            std::cout << "[C++] Debug - Posición: (" << px << ", " << py << ", " << pz << ") | Fuerza enviada: (" << fx << ", " << fy << ", " << fz << ") Newtons" << std::endl;
        }

        // Enviar fuerzas al hardware (Force Dimension espera Newtons)
        int ret = dhdSetForce(fx, fy, fz);
        if (ret < 0 && iteracion % 1000 == 1) { // Imprimir solo 1 vez por segundo si hay error
            std::cout << "[C++] Error enviando fuerza: " << dhdErrorGetLastStr() << std::endl;
        }
    }
    
    // Cerrar dispositivo
    dhdSetForce(0.0, 0.0, 0.0); // Asegurar que deje de aplicar fuerza
    dhdClose(g_deviceId);
    std::cout << "[C++] Hilo háptico cerrado y dispositivo desconectado." << std::endl;
    return 0;
}

// ---------------------------------------------------------
// FUNCIONES EXPORTADAS A PYTHON (C-API)
// ---------------------------------------------------------

EXPORT int init_falcon() {
    if (g_isRunning) return 1;
    
    g_isRunning = true;
    g_hapticThread = CreateThread(NULL, 0, hapticLoop, NULL, 0, NULL);
    
    // Esperar un poco para asegurar que se conectó (opcional)
    Sleep(500); 
    
    if (!g_isRunning || g_deviceId < 0) {
        return -1; // Error conectando
    }
    return 0; // 0 significa éxito
}

EXPORT void get_position(double* x, double* y, double* z) {
    if (x) *x = g_posX.load();
    if (y) *y = g_posY.load();
    if (z) *z = g_posZ.load();
}

EXPORT void set_force(double fx, double fy, double fz) {
    g_forceX.store(fx);
    g_forceY.store(fy);
    g_forceZ.store(fz);
}

EXPORT void close_falcon() {
    if (g_isRunning) {
        g_isRunning = false;
        if (g_hapticThread != NULL) {
            WaitForSingleObject(g_hapticThread, INFINITE);
            CloseHandle(g_hapticThread);
            g_hapticThread = NULL;
        }
    }
}

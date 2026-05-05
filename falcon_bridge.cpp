#include "dhdc.h"
#include "drdc.h"
#include <atomic>
#include <iostream>
#include <windows.h>

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

// Variable para el estado de los botones
std::atomic<int> g_buttons(0);

std::atomic<bool> g_isRunning(false);
HANDLE g_hapticThread = NULL;
int g_deviceId = -1;

DWORD WINAPI hapticLoop(LPVOID lpParam) {
  std::cout << "[C++] Iniciando hilo háptico del Novint Falcon..." << std::endl;

  g_deviceId = dhdOpen();
  if (g_deviceId < 0) {
    std::cout << "[C++] Error: No se pudo abrir el dispositivo. ("
              << dhdErrorGetLastStr() << ")" << std::endl;
    g_isRunning = false;
    return 1;
  }

  std::cout << "[C++] Falcon conectado: " << dhdGetSystemName() << std::endl;

  if (dhdEnableForce(DHD_ON, g_deviceId) < 0) {
    std::cout << "[C++] Error: No se pudo habilitar la fuerza." << std::endl;
  } else {
    std::cout << "[C++] Motores habilitados correctamente." << std::endl;
  }

  int iteracion = 0;

  while (g_isRunning) {
    double px, py, pz;
    if (dhdGetPosition(&px, &py, &pz) >= 0) {
      g_posX = px;
      g_posY = py;
      g_posZ = pz;
    }

    // LECTURA DE BOTONES
    int current_buttons = dhdGetButtonMask(g_deviceId);
    g_buttons = current_buttons;

    // IMPRESIÓN DE DIAGNÓSTICO (Para que veas el número en la consola negra)
    if (current_buttons > 0 && iteracion % 50 == 0) {
      std::cout << "[C++] ¡BOTÓN DETECTADO! Código: " << current_buttons
                << std::endl;
    }

    double fx = g_forceX.load();
    double fy = g_forceY.load();
    double fz = g_forceZ.load();

    int ret = dhdSetForce(fx, fy, fz);

    iteracion++;
  }

  dhdSetForce(0.0, 0.0, 0.0);
  dhdClose(g_deviceId);
  std::cout << "[C++] Hilo háptico cerrado." << std::endl;
  return 0;
}

EXPORT int init_falcon() {
  if (g_isRunning)
    return 1;

  g_isRunning = true;
  g_hapticThread = CreateThread(NULL, 0, hapticLoop, NULL, 0, NULL);

  Sleep(500);

  if (!g_isRunning || g_deviceId < 0)
    return -1;
  return 0;
}

EXPORT void get_position(double *x, double *y, double *z) {
  if (x)
    *x = g_posX.load();
  if (y)
    *y = g_posY.load();
  if (z)
    *z = g_posZ.load();
}

EXPORT void set_force(double fx, double fy, double fz) {
  g_forceX.store(fx);
  g_forceY.store(fy);
  g_forceZ.store(fz);
}

// EXPORTAMOS LOS BOTONES A PYTHON
EXPORT int get_buttons() { return g_buttons.load(); }

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
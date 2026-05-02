# Proyecto: Puente Novint Falcon -> Python

Este proyecto contiene la plantilla base (boilerplate) para conectar el **Novint Falcon** a un juego hecho en **Python**.

## Estructura
* `falcon_bridge.cpp`: Código en C++ que maneja el dispositivo (el SDK). Exoprta funciones a Python.
* `game.py`: Juego de Python con `pygame` y `ctypes` que se conecta a la DLL.
* `CMakeLists.txt`: Archivo para compilar el código C++ automáticamente.

## Requisitos Previos

1. **Compilador C++**: Necesitas tener instalado `MinGW` o `Visual Studio` (MSVC) en Windows. También necesitas `CMake`.
2. **Python**: Necesitas Python 3.x.
3. **Pygame**: Instálalo ejecutando:
   ```cmd
   pip install pygame
   ```
4. **SDK del Falcon**: Debes reemplazar los comentarios "TODO" en `falcon_bridge.cpp` con las verdaderas llamadas de tu SDK preferido (`libnifalcon` o `HDAL`).

## Cómo Compilar el C++ (La DLL)

Abre tu terminal (PowerShell o Símbolo del sistema) en esta misma carpeta y ejecuta:

```cmd
x86_64-w64-mingw32-g++ -shared -o falcon_bridge.dll falcon_bridge.cpp -std=c++11 "-Wl,--out-implib,libfalcon_bridge.a"
```

Esto generará el archivo `falcon_bridge.dll` (versión 64-bits). Ya lo he compilado por ti esta primera vez.

## Cómo Jugar

Una vez que tengas la `.dll` lista, solo ejecuta:

```cmd
python game.py
```

Verás una ventana negra con un círculo rojo que se mueve según los datos del puente en C++. (Actualmente el código base tiene una *simulación* de movimiento de péndulo en C++ para que veas cómo funciona antes de conectar el hardware real).

# juegoHaptico
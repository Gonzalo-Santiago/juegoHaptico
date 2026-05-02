cmake_minimum_required(VERSION 3.10)

# Nombre del proyecto
project(FalconBridge)

# Establecer estándar de C++
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Añadir la librería compartida (DLL en Windows, SO en Linux)
add_library(falcon_bridge SHARED falcon_bridge.cpp)

# Si utilizas libnifalcon, puedes incluirlo aquí:
# find_package(libnifalcon REQUIRED)
# target_link_libraries(falcon_bridge nifalcon)

# Mensaje de compilación
message(STATUS "Generando configuración para la DLL del puente de Falcon")

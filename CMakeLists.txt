cmake_minimum_required(VERSION 3.10)

# Nombre del proyecto
project(FalconBridge)

# Establecer estándar de C++
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Directorio del SDK de Force Dimension (mismo directorio del proyecto)
set(FD_SDK_DIR ${CMAKE_SOURCE_DIR})

# Añadir la librería compartida (DLL en Windows)
add_library(falcon_bridge SHARED falcon_bridge.cpp)

# Incluir headers del SDK
target_include_directories(falcon_bridge PRIVATE ${FD_SDK_DIR})

# Enlazar con la librería del SDK de Force Dimension
target_link_libraries(falcon_bridge PRIVATE ${FD_SDK_DIR}/dhdms64.lib)

# Mensaje de compilación
message(STATUS "Generando configuración para la DLL del puente de Falcon")

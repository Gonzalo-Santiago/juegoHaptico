# Documentación Técnica: Integración de Interfaz Háptica Activa en Entorno Interactivo 

**Nombre del Proyecto:** Falcon Strike - Vector Edition (Puente Novint Falcon - Python)  
**Dispositivo utilizado:** Novint Falcon (Controlador Háptico 3D de Fuerza Activa)  
**Propósito:** Integrar un dispositivo háptico de 3 grados de libertad (DOF) en un entorno de simulación bidimensional (Python/Pygame) utilizando una arquitectura de hilos asíncronos en C++ para proveer retroalimentación de fuerza (Force Feedback) en tiempo real, mejorando la inmersión y la manipulación directa del usuario.

---

## 1. Introducción y contexto

En el campo de la Interacción Humano-Computadora (IHC), la comunicación tradicional se ha centrado predominantemente en modalidades visuales y auditivas, dejando la vía somatosensorial subutilizada. La retroalimentación háptica introduce una bidireccionalidad física en la interfaz: el usuario no solo acciona el sistema, sino que el sistema ejerce fuerzas físicas sobre el usuario (MacLean, 2008). 

El presente proyecto nace de la necesidad de superar el paradigma del "vidrio plano" (flat glass), proporcionando al usuario una experiencia de manipulación directa donde las colisiones, el retroceso de armas y los límites espaciales del entorno digital (el juego arcade *Falcon Strike*) tienen una traducción física inmediata. Esta integración permite estudiar cómo la carga cognitiva y el tiempo de reacción se ven afectados cuando se introducen estímulos táctiles como redundancia a la información visual.

## 2. Descripción del dispositivo

El **Novint Falcon** es un dispositivo de interacción basado en cinemática paralela. Según las taxonomías de dispositivos de entrada en IHC (Buxton, 1983), se clasifica como un transductor de posición isométrica e isotónica (capaz de medir desplazamiento en el espacio) con capacidades de salida háptica activa.

**Especificaciones y su implicación en IHC:**
*   **Grados de Libertad (DOF):** 3 DOF para entrada de posición (ejes X, Y, Z) y 3 DOF para salida de fuerza. Esto permite un mapeo espacial directo uno a uno con entornos 3D, aunque en este proyecto se proyecta sobre un plano 2D con la profundidad (eje Z) utilizada para efectos de retroceso.
*   **Frecuencia de Actualización Háptica:** El dispositivo opera mediante el SDK de *Force Dimension* (`dhdc.h`), requiriendo un bucle de control estricto cercano a los 1000 Hz. En IHC, una latencia superior a los 2-3 milisegundos en la actualización de fuerza destruye la ilusión de solidez (sensación de vibración o *jitter*), por lo que el renderizado de fuerza debe estar aislado del renderizado gráfico (típicamente 60 Hz).
*   **Espacio de Trabajo (Workspace):** Aproximadamente 4x4x4 pulgadas. Esta limitación física define el "Control-Display (C/D) ratio"; un ratio muy alto incrementa la fatiga motriz, mientras que uno muy bajo reduce la precisión espacial (Ley de Fitts).

*[Insertar Tabla Comparativa de especificaciones técnicas frente a controladores estándar (ej. Gamepad, Mouse)]*

## 3. Objetivo de la implementación

El objetivo principal es implementar y evaluar una interfaz háptica asíncrona que traduzca eventos digitales en respuestas mecánicas, diseñada para usuarios jóvenes o investigadores de IHC familiarizados con simulaciones interactivas (Arcade gamers).

**Metas de Usabilidad:**
*   **Eficacia:** Permitir la navegación espacial y la puntería en pantalla con un margen de error posicional bajo, asegurando que las fuerzas externas (retroceso) no impidan al usuario recuperar el control en menos de 500 ms.
*   **Satisfacción:** Incrementar la inmersión subjetiva del usuario a través de vibraciones y resistencias físicas coherentes con la semántica gráfica (explosiones y disparos).
*   **Facilidad de Aprendizaje (Learnability):** El mapeo físico (mover la empuñadura equivale a mover la nave) aprovecha modelos mentales preexistentes del espacio físico, reduciendo la curva de aprendizaje en comparación con atajos de teclado.

## 4. Metodología de integración

Para garantizar la estabilidad del motor háptico, se ha adoptado una arquitectura de **Hilos Asíncronos Desacoplados**. 

1.  **Capa de Hardware (C++):** Se compila una librería dinámica (`falcon_bridge.dll`) que inicializa un `hapticThread`. Este hilo opera de forma independiente y se comunica directamente con los drivers USB del dispositivo mediante el Force Dimension SDK.
2.  **Capa de Interfaz y Gráficos (Python):** Utiliza `ctypes` para consumir la DLL. El bucle de juego (limitado a 60 FPS con `pygame`) lee las variables atómicas de posición y escribe las fuerzas resultantes de la física del juego.
3.  **Mapeo de Coordenadas:** Se aplica una transformación lineal bidimensional (X, Y) para escalar el espacio de trabajo físico (rango de metros) al sistema de coordenadas de la pantalla (píxeles), invirtiendo el eje Y por discrepancias entre estándares gráficos e ingenieriles.

*[Insertar Diagrama de Arquitectura de Software mostrando el Bucle Háptico a 1000Hz vs el Bucle Gráfico a 60Hz]*

## 5. Interacción usuario-sistema

Para analizar la interacción, aplicamos el **Modelo de los Siete Estadios de Acción** de Norman (2013), ilustrando el proceso cíclico durante el uso de la interfaz:

1.  **Formación del Objetivo:** El usuario desea destruir una nave enemiga sin recibir daño.
2.  **Formación de la Intención:** Decide mover la nave a la izquierda para alinear el disparo.
3.  **Especificación de la Acción:** Planifica el movimiento motor: empujar la empuñadura (grip) del Novint Falcon hacia la izquierda y presionar la tecla espacio.
4.  **Ejecución de la Acción:** El sistema muscular ejecuta el movimiento. El Falcon registra el cambio de coordenadas a través de sus codificadores ópticos y Python captura el evento del teclado.
5.  **Percepción del Estado del Mundo:** El usuario observa la nave desplazarse en pantalla (Feedback Visual a 60Hz), escucha el efecto de sonido (Feedback Auditivo), y **siente un impacto físico repentino de retroceso en el eje Z** proveniente del hardware (Feedback Háptico).
6.  **Interpretación del Estado:** El usuario procesa la resistencia física y la señal visual, decodificando que el arma fue disparada exitosamente y generó un retroceso.
7.  **Evaluación del Resultado:** El usuario comprueba si el enemigo fue destruido. Si el retroceso físico desvió su posición, formula un nuevo objetivo para compensar el error motriz, reiniciando el ciclo.

Este ciclo evidencia una ventaja crítica del sistema: el *feedback* háptico provee confirmación de la acción (Ejecución) de manera casi instantánea (<2 ms), mientras que la confirmación visual tiene una latencia inherente al refresco de la pantalla (~16 ms).

*[Insertar Diagrama de Flujo de Interacción basado en el Ciclo de Acción de Norman con tiempos de latencia anotados]*

## 6. Ventajas y desventajas

El análisis de usabilidad se enmarca en la norma **ISO 9241-11:2018** (Eficacia, Eficiencia, y Satisfacción):

**Ventajas:**
*   **Satisfacción Elevada:** La introducción de *Force Feedback* coherente aumenta la presencia espacial del usuario. La percepción de peso e inercia convierte una interfaz abstracta en una experiencia tangible.
*   **Redundancia de Señales (Eficacia):** Cuando el jugador sufre daño, la pantalla muestra una advertencia visual y el Falcon aplica una perturbación aleatoria (`f_x += random.uniform(-8.0, 8.0)`). Esta redundancia multisensorial reduce los tiempos de reacción ante eventos críticos del sistema.

**Desventajas:**
*   **Eficiencia Reducida por Fatiga Motriz:** A diferencia de un ratón estándar que descansa sobre una superficie (soporte pasivo), el usuario del Falcon debe sostener el grip en el aire contra la gravedad y contra la resistencia calculada (ej. Ley de Hooke `k=60.0`). Esto genera tensión isométrica continua, resultando en fatiga (Síndrome del Brazo de Gorila) en sesiones prolongadas.
*   **Exceso de Carga Cognitiva en Errores:** Si la ganancia de fuerza (K) es muy alta, el retroceso puede causar que el usuario pierda su objetivo (overshoot), obligándolo a realizar micro-correcciones constantes que penalizan la eficiencia de la tarea principal.

## 7. Limitaciones técnicas

*   **Saturación y Estabilidad Háptica (Hardware):** Los motores del Falcon tienen un límite físico de fuerza (aprox. 9 Newtons). Enviar fuerzas superiores por errores de cálculo en Python genera "clipping" y vibraciones inestables de alta frecuencia que degradan la experiencia de usuario y pueden ser inseguras.
    *   *Solución técnica propuesta:* Implementar una capa de "Saturación Segura" en el código C++ (Clamp) que trunque los vectores de fuerza antes de ser enviados al SDK (`dhdSetForce`).
*   **Desincronización de Hilos (Software):** Dado que Python corre en su propio bucle GIL (Global Interpreter Lock) y C++ maneja los motores, un cuello de botella en la renderización visual de Pygame genera desfases donde la fuerza háptica se siente antes o después del frame visual correspondiente.
    *   *Solución técnica propuesta:* Implementar interpolación de posición en Python y timestamps compartidos entre la DLL y Python para sincronizar los eventos hápticos exactamente con el frame de colisión.

## 8. Conclusiones y recomendaciones

La implementación de la arquitectura híbrida (C++ / Python) para el control del Novint Falcon demuestra ser un método robusto para integrar interfaces hápticas activas en entornos de programación de alto nivel. A nivel de IHC, el proyecto logra romper la barrera de la interacción plana, introduciendo el canal somatosensorial para reducir la dependencia exclusiva de la atención visual durante las alertas de sistema (colisiones y retroceso). Sin embargo, el diseño del modelo físico (fuerzas de resorte e impacto) debe ser calibrado cuidadosamente para evitar sobrepasar los umbrales de fatiga muscular del usuario.

**Líneas de desarrollo futuro:**
1.  **Mapeo Funcional de Hardware Integrado:** Actualmente la "Ejecución" de la acción de disparar recae en la barra espaciadora del teclado, fragmentando la interacción bimanual. Se recomienda leer los botones integrados en la empuñadura (Grip) del Falcon a través del SDK y mapearlos directamente en Python para concentrar el ciclo de acción en un solo dispositivo.
2.  **Renderizado de Texturas Hápticas (Haptic Textures):** Expandir el modelo físico para simular "fricción" y "viscosidad" dependiendo de las zonas de la pantalla, permitiendo al usuario identificar pasivamente el centro del área de juego o la proximidad de los enemigos mediante la resistencia del aire percibida en el dispositivo, aumentando la accesibilidad para usuarios con baja visión.

---

### Referencias

*   Buxton, W. (1983). Lexical and pragmatic considerations of input structures. *ACM SIGGRAPH Computer Graphics*, 17(3), 31-37.
*   ISO. (2018). *Ergonomics of human-system interaction — Part 11: Usability: Definitions and concepts* (ISO 9241-11:2018). International Organization for Standardization.
*   MacLean, K. E. (2008). Haptic interaction design for everyday interfaces. *Reviews of Human Factors and Ergonomics*, 4(1), 149-194.
*   Norman, D. A. (2013). *The design of everyday things*. Basic Books.
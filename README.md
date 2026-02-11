# Proyecto Sistemas Embebidos – Rover Autónomo

## Introducción
Este proyecto corresponde al trabajo práctico de la asignatura **Sistemas Embebidos**, cuyo objetivo es el desarrollo de un **rover móvil autónomo** basado en una Raspberry Pi, capaz de desplazarse de forma continua y **esquivar obstáculos**, integrando sensores, actuadores y programación concurrente.

El sistema fue diseñado siguiendo una arquitectura modular y concurrente, utilizando múltiples hilos de ejecución y mecanismos de sincronización, cumpliendo los requisitos establecidos en la rúbrica de la asignatura.

El código final y funcional del proyecto se encuentra en la carpeta **driverless/**. El resto del repositorio contiene **pruebas, prototipos y validaciones intermedias** realizadas durante el proceso de desarrollo.

---

## Objetivos cumplidos según la rúbrica

- Uso de programación concurrente mediante múltiples hilos.
- Separación clara de responsabilidades (sensores, control, señalización).
- Uso de mecanismos de sincronización (Lock, Event, Queue).
- Monitorización continua del entorno con sensor ultrasónico.
- Reacción automática ante obstáculos (buzzer + giro ~90°).
- Integración de sensores infrarrojos.
- Control de motores DC mediante PCA9685.
- Control de LEDs mediante SPI.
- Código modular, estructurado y comentado.

---

## Topología y estructura del proyecto

PROYECTO_ROVER/<br>
├── driverless/<br>
│   ├── lib/<br>
│   │   ├── buzzer.py<br>
│   │   ├── infrared.py<br>
│   │   ├── leds.py<br>
│   │   ├── motor.py<br>
│   │   ├── pca9685.py<br>
│   │   └── ultrasonido.py<br>
│   ├── main.py<br>
│   └── Setup.py<br>
├── tests/<br>
├── modules/<br>
└── README.md<br>

---

## Funcionamiento del sistema autónomo

El sistema implementa varios hilos concurrentes:

- **Ultrasonido**: mide distancia y actualiza estado compartido.
- **Control**: mueve el rover y ejecuta evasión ante obstáculos.
- **LEDs**: mantiene señalización visual continua.
- **Infrarrojos**: lectura periódica como apoyo sensorial.

---

## Cómo ejecutar el proyecto

### Requisitos
- Raspberry Pi con Raspberry Pi OS
- Python 3
- SPI habilitado
- Ejecución con sudo

### Pasos

    cd Proyecto_Sistemas_Embebidos_Rover
    sudo python3 driverless/main.py

Para detener el sistema:

    Ctrl + C

Nota: si los LEDs no funcionan, habilitar SPI desde raspi-config y reiniciar.

---

## Control de versiones (Git y GitHub)

El desarrollo se realizó usando Git y GitHub:
- Cada integrante trabajó en su propia rama.
- Integración progresiva al repositorio principal.
- Commits frecuentes para documentar avances y correcciones.

---

## Integrantes del grupo

- Oscar Eduardo Gómez Rivera
- Borja Graña Vidal
- Santiago de Prado Saborido
- Mateo Pérez Pastoriza
- Héctor Emilio Sierra Valdez

---

## Distribución de tareas

**Oscar Eduardo Gómez Rivera**
- Arquitectura general e integración final.
- Programación concurrente y evasión de obstáculos.

**Borja Graña Vidal**
- Control de motores y PCA9685.
- Ajuste de velocidades y giros.

**Santiago de Prado Saborido**
- Sensor ultrasónico y calibración.

**Mateo Pérez Pastoriza**
- Sensores infrarrojos y pruebas individuales.

**Héctor Emilio Sierra Valdez**
- LEDs, SPI y apoyo en documentación.

---

## Nota sobre el desarrollo

Se realizaron múltiples pruebas debido a fallos iniciales de sensores y periféricos.  
Las carpetas adicionales documentan este proceso de validación previo al sistema final.
Documentación de errores:
- [https://drive.google.com/file/d/1uqKrghAfRUxmyZ1OerxdNu-eD6vNPyen/view?usp=sharing](https://drive.google.com/file/d/1uqKrghAfRUxmyZ1OerxdNu-eD6vNPyen/view?usp=sharing)
- [https://drive.google.com/file/d/1vBQcYWe0UaNwVaal8ajDtcvk03P-tFiL/view?usp=sharing](https://drive.google.com/file/d/1vBQcYWe0UaNwVaal8ajDtcvk03P-tFiL/view?usp=sharing)
- [https://drive.google.com/file/d/1IGcqZqDGx-q0IXWn_8Yr6obN28EL-Lay/view?usp=sharing](https://drive.google.com/file/d/1IGcqZqDGx-q0IXWn_8Yr6obN28EL-Lay/view?usp=sharing)

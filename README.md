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
│   ├── lib/            ## Librerías usadas<br>
│   │   ├── buzzer.py<br>
│   │   ├── infrared.py<br>
│   │   ├── leds.py<br>
│   │   ├── motor.py<br>
│   │   ├── pca9685.py<br>
│   │   └── ultrasonido.py<br>
│   ├── main.py         ## Codigo principal para ejecutar<br>   
│   └── Setup.py        ## Instalación de recursos y librerías<br>
│
├── tests/              ## Pruebas y test previos<br> 
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

En los tres vídeos se muestran las pruebas hechas para comprobar, por un lado, el funcionamiento de los elementos del robotijo (como, por ejemplo, los sensores), y por otro, los diferentes movimientos que este tenía que llevar a cabo a partir del código escrito. Se tratan de las pruebas iniciales hechas al comienzo del trabajo, intentando familiarizarnos con el robotijo y la forma de trbajar con este.

En el primer vídeo observamos que el robotijo choca, sin saber el motivo, pudiendo ser o bien por culpa del código, o bien por algún problema de los periféricos o sensores.

En el segundo comprobamos que había un error en el sensor ultrasónico de forma que este siempre daba la misma lectura, impidiendo que el robotijo actuara correctamente, ya que trabaja de forma acorde a lo que el sensor detecta.

En el tercer vídeo comienza a hacer rectificaciones, pero estas no se corresponden a la detección de objetos, sino a la evolución en el código escrito, dando así respuesta a los cambios hechos y a lo que se pretendía conseguir.

LINK VIDEO FINAL: - [https://universidadevigo.sharepoint.com/:v:/s/Pruebasfinales-Robotijo/IQBOkNvOLkqYRJdcHqFpeJS1AbDQTLuyp-Syn9kBZ8cHjcs?e=I9gSOQ](https://universidadevigo.sharepoint.com/:v:/s/Pruebasfinales-Robotijo/IQBOkNvOLkqYRJdcHqFpeJS1AbDQTLuyp-Syn9kBZ8cHjcs?e=I9gSOQ)

Este video es el mismo que está subido en Moovi, en el se realizan las pruebas finales para escoger como esquivar mejor los objetos.

import RPi.GPIO as GPIO
import time
# Importamos tu clase para probar que el módulo funciona bien
from modules.ultrasonic import SensorUltrasonico

# Configuración básica
GPIO.setmode(GPIO.BOARD)
pin_trig = 16
pin_echo = 18

try:
    sensor = SensorUltrasonico(11, 13)
    print(f"--- Probando Sensor HC-SR04 en pines {pin_trig} y {pin_echo} ---")
    print("Presiona Ctrl+C para detener")
    
    while True:
        distancia = sensor.obtener_distancia()
        print(f"Distancia detectada: {distancia} cm")
        time.sleep(0.5) # Lectura cada medio segundo para facilitar la vista

except KeyboardInterrupt:
    print("\nPrueba finalizada por el usuario")
finally:
    GPIO.cleanup()
    print("Limpieza de GPIO completada")

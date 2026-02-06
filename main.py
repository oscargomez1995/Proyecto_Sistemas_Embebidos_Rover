import threading
import time
import RPi.GPIO as GPIO
from modules.ultrasonic import SensorUltrasonico
from modules.motor_ctrl import ControlMotores
from modules.brain import CerebroRover

# --- Configuración de Hardware ---
GPIO.setmode(GPIO.BOARD)

# Sincronización obligatoria para la rúbrica
DISTANCIA_COMPARTIDA = 100.0
LOCK = threading.Lock()
EJECUTANDO = True

def hilo_sensor():
    """Hilo dedicado exclusivamente a la lectura del sensor HC-SR04"""
    global DISTANCIA_COMPARTIDA, EJECUTANDO
    sensor = SensorUltrasonico(16, 18)
    
    while EJECUTANDO:
        try:
            d = sensor.obtener_distancia()
            with LOCK:
                DISTANCIA_COMPARTIDA = d
            time.sleep(0.05) # Muestreo a 20Hz
        except Exception as e:
            print(f"Error en sensor: {e}")

def hilo_control():
    """Hilo de decisión y actuación sobre motores PCA9685"""
    global EJECUTANDO
    motores = ControlMotores()
    cerebro = CerebroRover()
    
    while EJECUTANDO:
        try:
            # Lectura segura de la variable compartida
            with LOCK:
                dist = DISTANCIA_COMPARTIDA
            
            accion = cerebro.decidir_accion(dist)
            
            if accion == "AVANZAR_RAPIDO":
                # Potencia alta para tramos despejados
                motores.mover(3500, 3500, 3500, 3500)
            
            elif accion == "AVANZAR_LENTO":
                # Potencia reducida para aproximación
                motores.mover(1800, 1800, 1800, 1800)
            
            elif accion == "FRENAR":
                print(f"¡Obstáculo crítico detectado a {dist}cm!")
                motores.frenar_suave()
                # Maniobra de escape: retroceder un poco
                motores.mover(-2000, -2000, -2000, -2000)
                time.sleep(0.5)
                motores.mover(0, 0, 0, 0)
            
            time.sleep(0.1) # Ciclo de control
        except Exception as e:
            print(f"Error en control: {e}")

if __name__ == "__main__":
    # Inicio de la ejecución concurrente
    t_sensor = threading.Thread(target=hilo_sensor, daemon=True)
    t_control = threading.Thread(target=hilo_control, daemon=True)
    
    print("--- ROVER INICIADO: Modo Concurrente con PCA9685 ---")
    t_sensor.start()
    t_control.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo sistema de forma segura...")
        EJECUTANDO = False
        # Limpieza obligatoria para proteger el hardware
        GPIO.cleanup()
        print("GPIO liberado. Programa finalizado.")

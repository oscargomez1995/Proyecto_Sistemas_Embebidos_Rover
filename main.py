import threading
import time
import RPi.GPIO as GPIO
from modules.ultrasonic import SensorUltrasonico
from modules.motor_ctrl import ControlMotores
from modules.brain import CerebroRover

# Configuración de Hardware
GPIO.setmode(GPIO.BOARD)
DISTANCIA_COMPARTIDA = 100.0
LOCK = threading.Lock() # Sincronización obligatoria [cite: 25]

def hilo_sensor():
    """Hilo dedicado a la sensórica """
    global DISTANCIA_COMPARTIDA
    sensor = SensorUltrasonico(16, 18) # Pins de ejemplo
    while True:
        d = sensor.obtener_distancia()
        with LOCK:
            DISTANCIA_COMPARTIDA = d
        time.sleep(0.05)

def hilo_control():
    """Hilo dedicado a la lógica y actuadores """
    motores = ControlMotores({'DIR_IZQ':13, 'DIR_DER':15, 'PWM_IZQ':12, 'PWM_DER':11})
    cerebro = CerebroRover()
    while True:
        with LOCK:
            dist = DISTANCIA_COMPARTIDA
        
        accion = cerebro.decidir_accion(dist)
        if accion == "AVANZAR":
            motores.mover(50, 50)
        elif accion == "GIRAR":
            motores.mover(40, -40)
        else:
            motores.frenar_suave(40)
        time.sleep(0.1)

if __name__ == "__main__":
    # Inicio de la ejecución concurrente [cite: 22]
    t1 = threading.Thread(target=hilo_sensor, daemon=True)
    t2 = threading.Thread(target=hilo_control, daemon=True)
    t1.start()
    t2.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()

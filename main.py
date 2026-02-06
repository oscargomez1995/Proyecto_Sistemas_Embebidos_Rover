import threading
import time
import RPi.GPIO as GPIO
from modules.ultrasonic import SensorUltrasonico
from modules.motor_ctrl import ControlMotores
from modules.brain import CerebroRover

GPIO.setmode(GPIO.BOARD)
DISTANCIA_COMPARTIDA = 100.0
LOCK = threading.Lock()
EJECUTANDO = True

def hilo_sensor():
    global DISTANCIA_COMPARTIDA, EJECUTANDO
    sensor = SensorUltrasonico(16, 18)
    while EJECUTANDO:
        d = sensor.obtener_distancia()
        with LOCK:
            DISTANCIA_COMPARTIDA = d
        time.sleep(0.05)

def hilo_control():
    global EJECUTANDO
    motores = ControlMotores()
    cerebro = CerebroRover()
    while EJECUTANDO:
        with LOCK:
            dist = DISTANCIA_COMPARTIDA
        accion = cerebro.decidir_accion(dist)
        if accion == "AVANZAR_RAPIDO":
            motores.mover(3000, 3000, 3000, 3000)
        elif accion == "FRENAR":
            motores.frenar_suave()
        time.sleep(0.1)

if __name__ == "__main__":
    t1 = threading.Thread(target=hilo_sensor, daemon=True)
    t2 = threading.Thread(target=hilo_control, daemon=True)
    t1.start(); t2.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        EJECUTANDO = False
        GPIO.cleanup()

import threading
import time
from modules.ultrasonic import SensorUltrasonico

distancia_global = 100.0
lock = threading.Lock() # Sincronización obligatoria [cite: 25]

def hilo_lectura():
    global distancia_global
    sensor = SensorUltrasonico(16, 18)
    while True:
        d = sensor.obtener_distancia()
        with lock:
            distancia_global = d
        time.sleep(0.1)

if __name__ == "__main__":
    # Inicia hilos independientes para sensórica y control [cite: 24]
    t = threading.Thread(target=hilo_lectura, daemon=True)
    t.start()
    try:
        while True:
            with lock:
                print(f"Distancia actual: {distancia_global} cm")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Cerrando programa...")

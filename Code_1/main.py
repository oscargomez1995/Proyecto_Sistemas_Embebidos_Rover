import threading
import time
import RPi.GPIO as GPIO
from modules.ultrasonic import SensorUltrasonico
from modules.motor_ctrl import ControlMotores

# --- Configuración de Hardware ---
GPIO.setmode(GPIO.BOARD)

# Variables compartidas (Rúbrica de Sincronización)
DISTANCIA_COMPARTIDA = 100.0
LOCK = threading.Lock()
EJECUTANDO = True

def hilo_sensor():
    """Hilo 1: Monitoreo constante del sensor ultrasónico"""
    global DISTANCIA_COMPARTIDA, EJECUTANDO
    sensor = SensorUltrasonico(16, 18)
    
    while EJECUTANDO:
        try:
            d = sensor.obtener_distancia()
            with LOCK:
                DISTANCIA_COMPARTIDA = d
            time.sleep(0.05) 
        except Exception as e:
            print(f"Error en sensor: {e}")

def hilo_coreografia():
    """Hilo 2: Ejecución de la secuencia de movimientos (Test B)"""
    global EJECUTANDO
    motores = ControlMotores()
    
    VEL_RAPIDA = 3800
    VEL_LENTA = 1800

    def mover_seguro(v1, v2, v3, v4, duracion):
        """Función auxiliar para mover con chequeo de obstáculo"""
        inicio = time.time()
        while time.time() - inicio < duracion and EJECUTANDO:
            with LOCK:
                # Parada de emergencia si hay un obstáculo a menos de 15cm
                if DISTANCIA_COMPARTIDA < 15:
                    print(f"¡EMERGENCIA! Obstáculo a {DISTANCIA_COMPARTIDA}cm. Abortando.")
                    motores.mover(0,0,0,0)
                    return False 
            
            motores.mover(v1, v2, v3, v4)
            time.sleep(0.1)
        return True

    print("--- INICIANDO COREOGRAFÍA MULTIHILO ---")
    
    try:
        # 1. Avance rápido (1s real - ajustado a 2s según tu lógica de sleep)
        print(">> Avanzando rápido")
        if not mover_seguro(VEL_RAPIDA, VEL_RAPIDA, VEL_RAPIDA, VEL_RAPIDA, 2): return

        # 2. Avance lento (4s)
        print(">> Avance lento")
        if not mover_seguro(VEL_LENTA, VEL_LENTA, VEL_LENTA, VEL_LENTA, 4): return

        # 3. Retroceso lento (2s)
        print(">> Retroceso lento")
        if not mover_seguro(-VEL_LENTA, -VEL_LENTA, -VEL_LENTA, -VEL_LENTA, 2): return

        # 4. Retroceso rápido (1s)
        print(">> Retroceso rápido")
        if not mover_seguro(-VEL_RAPIDA, -VEL_RAPIDA, -VEL_RAPIDA, -VEL_RAPIDA, 1): return

        # 5. Giro Izquierda (2s)
        print(">> Giro izquierda")
        if not mover_seguro(-VEL_LENTA, -VEL_LENTA, VEL_LENTA, VEL_LENTA, 2): return

        # 6. Giro Derecha (2s)
        print(">> Giro derecha")
        if not mover_seguro(VEL_LENTA, VEL_LENTA, -VEL_LENTA, -VEL_LENTA, 2): return

        # 7. Rotación final (5s)
        print(">> Rotación final")
        if not mover_seguro(VEL_LENTA, VEL_LENTA, -VEL_LENTA, -VEL_LENTA, 5): return

        print("--- COREOGRAFÍA FINALIZADA EXITOSAMENTE ---")

    except Exception as e:
        print(f"Error en coreografía: {e}")
    finally:
        motores.mover(0, 0, 0, 0)
        EJECUTANDO = False

if __name__ == "__main__":
    # Creación de hilos
    t_sensor = threading.Thread(target=hilo_sensor, daemon=True)
    t_coreo = threading.Thread(target=hilo_coreografia, daemon=True)
    
    print("Sistema Rover Concurrente iniciado...")
    t_sensor.start()
    t_coreo.start()
    
    try:
        # Mantener el main vivo mientras la coreografía se ejecuta
        while EJECUTANDO:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[!] Interrupción detectada. Limpiando...")
    finally:
        EJECUTANDO = False
        GPIO.cleanup()
        print("Sistema apagado.")

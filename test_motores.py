import time
import RPi.GPIO as GPIO
from modules.motor_ctrl import ControlMotores

def secuencia_final():
    print("--- INICIANDO COREOGRAFÍA DEL ROVER ---")
    motores = ControlMotores()
    
    # Definición de potencias para mayor precisión
    VEL_RAPIDA = 3800
    VEL_LENTA = 1800

    try:
        # 1. Por 1 segundo avance rápido
        print(">> Avanzando rápido (1s)")
        motores.mover(VEL_RAPIDA, VEL_RAPIDA, VEL_RAPIDA, VEL_RAPIDA)
        time.sleep(1)

        # 2. Por 2 segundos baje su velocidad
        print(">> Avance lento (2s)")
        motores.mover(VEL_LENTA, VEL_LENTA, VEL_LENTA, VEL_LENTA)
        time.sleep(2)

        # 3. Por 2 segundos retroceda despacio
        print(">> Retroceso lento (2s)")
        motores.mover(-VEL_LENTA, -VEL_LENTA, -VEL_LENTA, -VEL_LENTA)
        time.sleep(2)

        # 4. Por 1 segundo retroceda rápido
        print(">> Retroceso rápido (1s)")
        motores.mover(-VEL_RAPIDA, -VEL_RAPIDA, -VEL_RAPIDA, -VEL_RAPIDA)
        time.sleep(1)

        # 5. Doblar a la izquierda y avance 2 segundos (Velocidad lenta)
        print(">> Giro izquierda y avance (2s)")
        # Para girar: Lado izquierdo atrás, lado derecho adelante
        motores.mover(-VEL_LENTA, -VEL_LENTA, VEL_LENTA, VEL_LENTA)
        time.sleep(2)

        # 6. Doblar a la derecha y avance 3 segundos (Velocidad lenta)
        print(">> Giro derecha y avance (3s)")
        # Para girar: Lado izquierdo adelante, lado derecho atrás
        motores.mover(VEL_LENTA, VEL_LENTA, -VEL_LENTA, -VEL_LENTA)
        time.sleep(3)

        # 7. Dar una vuelta por 3 segundos (Rotación sobre su eje)
        print(">> Rotación 360 grados (3s)")
        motores.mover(VEL_LENTA, VEL_LENTA, -VEL_LENTA, -VEL_LENTA)
        time.sleep(3)

        # 8. Detenerse
        print("--- SECUENCIA COMPLETADA ---")
        motores.mover(0, 0, 0, 0)

    except KeyboardInterrupt:
        print("\n[!] Prueba cancelada por el usuario.")
    finally:
        # Parada de seguridad obligatoria
        motores.mover(0, 0, 0, 0)
        GPIO.cleanup()
        print("GPIO Liberado y motores apagados.")

if __name__ == "__main__":
    # Configuración del modo de numeración de la placa
    GPIO.setmode(GPIO.BOARD)
    secuencia_final()

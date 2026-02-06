import time
import RPi.GPIO as GPIO
from modules.motor_ctrl import ControlMotores

def prueba_secuencial():
    print("--- INICIANDO SECUENCIA DE PRUEBA DE MOTORES ---")
    motores = ControlMotores()

    try:
        # 1. Por 1 segundo avance rápido
        print("1. Avanzando rápido (1 seg)...")
        motores.mover(3800, 3800, 3800, 3800)
        time.sleep(1)

        # 2. Por 2 segundos baje su velocidad (avance lento)
        print("2. Bajando velocidad (2 seg)...")
        motores.mover(1800, 1800, 1800, 1800)
        time.sleep(2)

        # 3. Por 2 segundos retroceda despacio
        print("3. Retrocediendo despacio (2 seg)...")
        motores.mover(-1800, -1800, -1800, -1800)
        time.sleep(2)

        # 4. Por 1 segundo retroceda rápido
        print("4. Retrocediendo rápido (1 seg)...")
        motores.mover(-3800, -3800, -3800, -3800)
        time.sleep(1)

        # 5. Detenerse
        print("5. Secuencia completada. Deteniendo motores.")
        motores.mover(0, 0, 0, 0)

    except KeyboardInterrupt:
        print("\nPrueba interrumpida.")
    finally:
        # Aseguramos que los motores se apaguen
        motores.mover(0, 0, 0, 0)
        GPIO.cleanup()
        print("GPIO Limpiado.")

if __name__ == "__main__":
    # Importante: configurar el modo de GPIO antes de empezar
    GPIO.setmode(GPIO.BOARD)
    prueba_secuencial()

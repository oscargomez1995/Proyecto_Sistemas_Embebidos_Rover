"""
Sistema autónomo simplificado para Rover usando threading.
Replica el comportamiento de driverless/main.py pero usando únicamente
las funciones y componentes de Test_functions.py

Hilos:
- Hilo 1: Sensor ultrasónico (actualiza distancia compartida)
- Hilo 2: Control del rover (avance + evasión de obstáculos)
- Hilo 3: Barrido del servo (opcional, para escaneo)

Funcionalidad:
- El rover avanza continuamente
- Detecta obstáculos con sensor ultrasónico
- Al detectar obstáculo (<10cm), se detiene, gira 90° izquierda y continúa
"""

import time
import threading
import queue
from ultrasonic import Ultrasonic
from motor import Ordinary_Car
from servo import Servo

# ------------------------------------------------
# Variables compartidas y sincronización
# ------------------------------------------------
DISTANCIA_CM = 999.0
LOCK_ESTADO = threading.Lock()
EVENTO_STOP = threading.Event()
COLA_OBSTACULO = queue.Queue(maxsize=10)

# ------------------------------------------------
# Parámetros de configuración
# ------------------------------------------------
UMBRAL_OBSTACULO_CM = 10

# Velocidades de los motores (ajustadas según Test_functions.py)
VEL_ADELANTE = 2000
VEL_GIRO = 2000

# Tiempo aproximado para girar 90 grados
TIEMPO_GIRO_90 = 0.55

# Periodos de ejecución
PERIODO_SENSOR = 0.05
PERIODO_CONTROL = 0.05
PERIODO_SERVO = 2.0  # Tiempo entre barridos del servo


# ------------------------------------------------
# Hilo 1: Sensor ultrasónico
# ------------------------------------------------
def hilo_ultrasonico():
    """Lee continuamente la distancia del sensor ultrasónico"""
    global DISTANCIA_CM
    sonic = Ultrasonic()

    try:
        while not EVENTO_STOP.is_set():
            distancia = sonic.get_distance()

            if distancia is not None:
                with LOCK_ESTADO:
                    DISTANCIA_CM = float(distancia)

                # Notificar obstáculo si está muy cerca
                if distancia < UMBRAL_OBSTACULO_CM:
                    try:
                        COLA_OBSTACULO.put_nowait(("OBSTACULO", time.time(), distancia))
                    except queue.Full:
                        pass

            time.sleep(PERIODO_SENSOR)
    finally:
        sonic.close()


# ------------------------------------------------
# Hilo 2: Control del rover + evasión de obstáculos
# ------------------------------------------------
def hilo_control():
    """Controla el movimiento del rover y evita obstáculos"""
    motor = Ordinary_Car()

    def detener():
        motor.set_motor_model(0, 0, 0, 0)

    def avanzar():
        # Motores hacia adelante (según Test_functions.py)
        motor.set_motor_model(
            VEL_ADELANTE, VEL_ADELANTE,
            VEL_ADELANTE, VEL_ADELANTE
        )

    def girar_izquierda_90():
        """Gira 90 grados a la izquierda (ruedas izq atrás, der adelante)"""
        motor.set_motor_model(
            -VEL_GIRO, -VEL_GIRO,  # Ruedas izquierdas atrás
            VEL_GIRO, VEL_GIRO      # Ruedas derechas adelante
        )
        time.sleep(TIEMPO_GIRO_90)
        detener()

    try:
        print("[CONTROL] Rover avanzando...")
        avanzar()

        while not EVENTO_STOP.is_set():
            try:
                evento, t, d = COLA_OBSTACULO.get_nowait()
            except queue.Empty:
                time.sleep(PERIODO_CONTROL)
                continue

            if evento == "OBSTACULO":
                with LOCK_ESTADO:
                    distancia_actual = DISTANCIA_CM

                print(f"[EMERGENCIA] Obstáculo detectado a {distancia_actual:.1f} cm")

                # Secuencia de evasión
                detener()
                time.sleep(0.2)

                print("[CONTROL] Girando 90° a la izquierda...")
                girar_izquierda_90()

                time.sleep(0.2)
                print("[CONTROL] Reanudando avance...")
                avanzar()

    finally:
        try:
            detener()
            motor.close()
        except Exception as e:
            print(f"[ERROR] Cerrando motor: {e}")


# ------------------------------------------------
# Hilo 3: Barrido del servo (opcional)
# ------------------------------------------------
def hilo_servo_barrido():
    """Realiza barridos periódicos con el servo del ultrasónico"""
    servo = Servo()

    try:
        # Inicializar servo en posición central
        servo.set_servo_pwm('0', 90)
        time.sleep(0.5)

        while not EVENTO_STOP.is_set():
            # Barrido de 30° a 150°
            for angulo in range(30, 151, 10):
                if EVENTO_STOP.is_set():
                    break
                servo.set_servo_pwm('0', angulo)
                time.sleep(0.05)

            # Barrido de 150° a 30°
            for angulo in range(150, 29, -10):
                if EVENTO_STOP.is_set():
                    break
                servo.set_servo_pwm('0', angulo)
                time.sleep(0.05)

            # Volver al centro
            servo.set_servo_pwm('0', 90)
            time.sleep(PERIODO_SERVO)

    finally:
        try:
            servo.set_servo_pwm('0', 90)  # Dejar en posición central
        except Exception as e:
            print(f"[ERROR] Cerrando servo: {e}")


# ------------------------------------------------
# Programa principal
# ------------------------------------------------
def main():
    print("=" * 50)
    print("Sistema Rover Autónomo Simplificado")
    print("Basado en driverless/main.py")
    print("Usando componentes de Test_functions.py")
    print("=" * 50)
    print()

    # Crear hilos
    h_ultrasonico = threading.Thread(target=hilo_ultrasonico, daemon=True)
    h_control = threading.Thread(target=hilo_control, daemon=True)
    h_servo = threading.Thread(target=hilo_servo_barrido, daemon=True)

    # Iniciar hilos
    print("[MAIN] Iniciando hilos...")
    h_ultrasonico.start()
    h_servo.start()
    time.sleep(0.5)  # Esperar a que se inicialice el sensor
    h_control.start()

    try:
        print("[MAIN] Sistema en funcionamiento. Presiona Ctrl+C para detener.")
        print()

        while True:
            with LOCK_ESTADO:
                distancia = DISTANCIA_CM

            print(f"[ESTADO] Distancia: {distancia:.1f} cm", end="\r")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n")
        print("[MAIN] Interrupción detectada. Deteniendo sistema...")

    finally:
        EVENTO_STOP.set()
        time.sleep(0.5)
        print("[MAIN] Sistema apagado correctamente.")
        print()


if __name__ == "__main__":
    main()

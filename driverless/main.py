"""
Sistema concurrente para Rover usando threading y sincronización.

Hilos:
- Hilo 1: Sensor ultrasónico (actualiza distancia compartida)
- Hilo 2: Control del rover (avance + evasión de obstáculos)
- Hilo 3: LEDs siempre encendidos (animación tipo wheel)
- Hilo 4: Sensores infrarrojos (opcional, solo lectura)

Correcciones incluidas:
- El control usa la distancia DEL EVENTO (d) en vez de DISTANCIA_CM (evita "OBSTACULO a 300cm")
- Filtro de lecturas inválidas del ultrasonido (None, <=0, o demasiado altas tipo 300)
- Cooldown anti-rebote para no encadenar evasiones
- Limpieza de cola tras manejar un evento (descarta eventos viejos acumulados)
"""

import time
import threading
import queue

import RPi.GPIO as GPIO
from lib.buzzer import Buzzer
from lib.infrared import Infrared
from lib.leds import Freenove_SPI_LedPixel
from lib.motor import Ordinary_Car
from lib.ultrasonido import Ultrasonic

# ------------------------------------------------
# Variables compartidas y mecanismos de sincronización
# ------------------------------------------------
DISTANCIA_CM = 999.0
VALOR_IR = 0

LOCK_ESTADO = threading.Lock()
EVENTO_STOP = threading.Event()

# Cola para notificar detección de obstáculo (thread-safe)
COLA_OBSTACULO = queue.Queue(maxsize=1)

# ------------------------------------------------
# Parámetros de configuración
# ------------------------------------------------
UMBRAL_OBSTACULO_CM = 60

# Rango válido de medición (ajusta según tu sensor/lib; 300 suele ser "sin eco")
DISTANCIA_MIN_VALIDA = 2.0
DISTANCIA_MAX_VALIDA = 250.0

# Velocidades de los motores
VEL_ADELANTE = 1000
VEL_GIRO = 1000

# Tiempo aproximado para retroceder (ajustable)
TIEMPO_RETROCEDER = 0.2

# Tiempo aproximado para girar 90 grados (ajustable)
TIEMPO_GIRO_90 = 1.0

# Periodos de ejecución
PERIODO_SENSOR = 0.05
PERIODO_CONTROL = 0.05
PERIODO_LED = 0.01
PERIODO_IR = 0.10

# Anti-rebote: tiempo mínimo entre evasiones
COOLDOWN_OBSTACULO_S = 1.0


# ------------------------------------------------
# Hilo 1: Sensor ultrasónico
# ------------------------------------------------
def hilo_ultrasonico():
    global DISTANCIA_CM
    sensor = Ultrasonic()

    try:
        while not EVENTO_STOP.is_set():
            distancia = sensor.get_distance()

            # Filtrar lecturas inválidas / fuera de rango (típico 300 = sin eco)
            if (
                distancia is None
                or not isinstance(distancia, (int, float))
                or distancia < DISTANCIA_MIN_VALIDA
                or distancia > DISTANCIA_MAX_VALIDA
            ):
                time.sleep(PERIODO_SENSOR)
                continue

            # Actualizar variable compartida SOLO con datos válidos
            with LOCK_ESTADO:
                DISTANCIA_CM = float(distancia)

            # Notificar obstáculo si está muy cerca
            if distancia < UMBRAL_OBSTACULO_CM:
                try:
                    # Guardamos la distancia del evento en la cola
                    COLA_OBSTACULO.put_nowait(("OBSTACULO", time.time(), float(distancia)))
                except queue.Full:
                    pass

            time.sleep(PERIODO_SENSOR)

    finally:
        try:
            sensor.close()
        except Exception:
            pass


# ------------------------------------------------
# Hilo 2: Sensor infrarrojo (opcional)
# ------------------------------------------------
def hilo_infrarrojo():
    global VALOR_IR
    ir = Infrared()

    try:
        while not EVENTO_STOP.is_set():
            valor = ir.read_all_infrared()
            with LOCK_ESTADO:
                VALOR_IR = int(valor)
            time.sleep(PERIODO_IR)
    finally:
        try:
            ir.close()
        except Exception:
            pass


# ------------------------------------------------
# Hilo 3: LEDs (siempre activos)
# ------------------------------------------------
def hilo_leds():
    leds = Freenove_SPI_LedPixel(count=8, bright=80, sequence="GRB", bus=0, device=0)

    try:
        # Verificar que SPI esté habilitado
        if leds.check_spi_state() == 0:
            print("[LEDS] SPI no disponible. Habilita SPI y reinicia.")
            return

        j = 0
        while not EVENTO_STOP.is_set():
            for i in range(leds.led_count):
                leds.set_led_rgb_data(
                    i,
                    leds.wheel((round(i * 255 / leds.led_count) + j) % 256)
                )
            leds.show()
            j = (j + 1) % 256
            time.sleep(PERIODO_LED)

    finally:
        try:
            leds.led_close()
        except Exception:
            pass


# ------------------------------------------------
# Hilo 4: Control del rover + seguridad
# ------------------------------------------------
def hilo_control():
    motores = Ordinary_Car()
    buzzer = Buzzer()

    def detener():
        motores.set_motor_model(0, 0, 0, 0)

    def avanzar():
        motores.set_motor_model(
            -VEL_ADELANTE, -VEL_ADELANTE,
            -VEL_ADELANTE, -VEL_ADELANTE
        )

    def retroceder():
        motores.set_motor_model(
            VEL_ADELANTE, VEL_ADELANTE,
            VEL_ADELANTE, VEL_ADELANTE
        )
        time.sleep(TIEMPO_RETROCEDER)
        detener()

    def girar_izquierda_90():
        motores.set_motor_model(
            -VEL_GIRO, -VEL_GIRO,
            VEL_GIRO, VEL_GIRO
        )
        time.sleep(TIEMPO_GIRO_90)
        detener()

    def alerta_buzzer():
        for _ in range(3):
            buzzer.set_state(True)
            time.sleep(0.08)
            buzzer.set_state(False)
            time.sleep(0.08)

    def limpiar_cola_obstaculo():
        # Descarta eventos viejos acumulados
        while True:
            try:
                COLA_OBSTACULO.get_nowait()
            except queue.Empty:
                break

    ultimo_evento = 0.0

    try:
        print("[CONTROL] Rover avanzando...")
        avanzar()

        while not EVENTO_STOP.is_set():
            try:
                evento, t, d = COLA_OBSTACULO.get_nowait()
            except queue.Empty:
                time.sleep(PERIODO_CONTROL)
                continue

            if evento != "OBSTACULO":
                continue

            # Anti-rebote / cooldown para evitar bucle de evasión
            ahora = time.time()
            if (ahora - ultimo_evento) < COOLDOWN_OBSTACULO_S:
                continue
            ultimo_evento = ahora

            # Usar la distancia del EVENTO (d), no la distancia global (que puede ser 300)
            print(f"[EMERGENCIA] Obstáculo detectado a {d:.1f} cm")

            detener()
            retroceder()

            # beep rápido + alerta
            buzzer.set_state(True)
            time.sleep(0.15)
            buzzer.set_state(False)

            alerta_buzzer()
            girar_izquierda_90()

            # Limpia cola para no re-ejecutar maniobras por eventos viejos
            limpiar_cola_obstaculo()

            time.sleep(0.1)
            avanzar()

    finally:
        try:
            detener()
            motores.close()
        except Exception:
            pass

        try:
            buzzer.set_state(False)
            buzzer.close()
        except Exception:
            pass


# ------------------------------------------------
# Programa principal
# ------------------------------------------------
def main():
    print("Sistema Rover concurrente iniciado")

    h1 = threading.Thread(target=hilo_ultrasonico, daemon=True)
    h2 = threading.Thread(target=hilo_leds, daemon=True)
    h3 = threading.Thread(target=hilo_control, daemon=True)
    h4 = threading.Thread(target=hilo_infrarrojo, daemon=True)

    h1.start()
    h2.start()
    h4.start()
    h3.start()

    try:
        while True:
            with LOCK_ESTADO:
                print(f"[ESTADO] Distancia={DISTANCIA_CM:.1f} cm | IR={VALOR_IR}")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[MAIN] Interrupción detectada")

    finally:
        EVENTO_STOP.set()
        time.sleep(0.3)
        print("[MAIN] Sistema apagado")


if __name__ == "__main__":
    main()

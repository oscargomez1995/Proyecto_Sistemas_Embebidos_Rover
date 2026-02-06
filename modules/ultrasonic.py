import RPi.GPIO as GPIO
import time

class SensorUltrasonico:
    def __init__(self, trig=16, echo=18):
        self.trig = trig
        self.echo = echo
        # Criterio: Sensórica - Configuración obligatoria
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

    def obtener_distancia(self):
        # Limpieza del pin trigger
        GPIO.output(self.trig, False)
        time.sleep(0.01)

        # Disparo de pulso (10 microsegundos)
        GPIO.output(self.trig, True)
        time.sleep(0.00001)
        GPIO.output(self.trig, False)

        # Tiempos de seguridad para evitar bloqueos
        timeout = time.time() + 0.1
        start_time = time.time()
        stop_time = time.time()

        # Captura el inicio del eco con protección contra bloqueo
        while GPIO.input(self.echo) == 0:
            start_time = time.time()
            if start_time > timeout:
                return 100.0  # Si falla, devolvemos una distancia segura

        # Captura el fin del eco con protección contra bloqueo
        timeout = time.time() + 0.1
        while GPIO.input(self.echo) == 1:
            stop_time = time.time()
            if stop_time > timeout:
                return 100.0

        duracion = stop_time - start_time
        distancia = (duracion * 34300) / 2
        
        return round(distancia, 2)

import RPi.GPIO as GPIO
import time

class SensorUltrasonico:
    def __init__(self, trig=16, echo=18):
        self.trig = trig
        self.echo = echo
        # Configuración de pines (Criterio: Sensórica)
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

    def obtener_distancia(self):
        """Mide la distancia enviando un pulso sónico"""
        # Limpieza del pin trigger
        GPIO.output(self.trig, False)
        time.sleep(0.01)

        # Disparo de pulso (10 microsegundos)
        GPIO.output(self.trig, True)
        time.sleep(0.00001)
        GPIO.output(self.trig, False)

        start_time = time.time()
        stop_time = time.time()

        # Captura el inicio del eco
        while GPIO.input(self.echo) == 0:
            start_time = time.time()

        # Captura el fin del eco
        while GPIO.input(self.echo) == 1:
            stop_time = time.time()

        # Cálculo basado en la velocidad del sonido (34300 cm/s)
        duracion = stop_time - start_time
        distancia = (duracion * 34300) / 2
        
        return round(distancia, 2)

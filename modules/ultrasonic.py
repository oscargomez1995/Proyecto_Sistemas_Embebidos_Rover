import RPi.GPIO as GPIO
import time

class SensorUltrasonico:
    def __init__(self, trig, echo):
        self.trig = trig
        self.echo = echo
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

    def obtener_distancia(self):
        GPIO.output(self.trig, True)
        time.sleep(0.00001)
        GPIO.output(self.trig, False)
        while GPIO.input(self.echo) == 0: start = time.time()
        while GPIO.input(self.echo) == 1: stop = time.time()
        return round(((stop - start) * 34300) / 2, 2)

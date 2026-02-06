import RPi.GPIO as GPIO
import time

class ControlMotores:
    def __init__(self, pins):
        self.pins = pins
        for pin in self.pins.values():
            GPIO.setup(pin, GPIO.OUT)
        self.pwm_izq = GPIO.PWM(self.pins['PWM_IZQ'], 1000)
        self.pwm_der = GPIO.PWM(self.pins['PWM_DER'], 1000)
        self.pwm_izq.start(0)
        self.pwm_der.start(0)

    def mover(self, vel_izq, vel_der):
        """Control básico de movimiento"""
        GPIO.output(self.pins['DIR_IZQ'], vel_izq > 0)
        GPIO.output(self.pins['DIR_DER'], vel_der > 0)
        self.pwm_izq.ChangeDutyCycle(abs(vel_izq))
        self.pwm_der.ChangeDutyCycle(abs(vel_der))

    def frenar_suave(self, vel_actual):
        """Reduce la velocidad gradualmente (Seguridad)"""
        for v in range(vel_actual, -1, -5):
            self.pwm_izq.ChangeDutyCycle(v)
            self.pwm_der.ChangeDutyCycle(v)
            time.sleep(0.02)
        self.mover(0, 0)

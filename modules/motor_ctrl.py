import time
from pca9685 import PCA9685

class ControlMotores:
    def __init__(self):
        self.pwm = PCA9685(0x40)
        self.pwm.set_pwm_freq(50)
        self.vel_ref = 0

    def mover(self, d1, d2, d3, d4):
        # Mapeo: 0,1 izq_sup | 3,2 izq_inf | 6,7 der_sup | 4,5 der_inf
        self._set_wheel(0, 1, d1)
        self._set_wheel(3, 2, d2)
        self._set_wheel(6, 7, d3)
        self._set_wheel(4, 5, d4)
        self.vel_ref = d1

    def _set_wheel(self, p1, p2, duty):
        if duty > 0:
            self.pwm.set_motor_pwm(p1, 0); self.pwm.set_motor_pwm(p2, abs(duty))
        elif duty < 0:
            self.pwm.set_motor_pwm(p2, 0); self.pwm.set_motor_pwm(p1, abs(duty))
        else:
            self.pwm.set_motor_pwm(p1, 4095); self.pwm.set_motor_pwm(p2, 4095)

    def frenar_suave(self):
        for v in range(abs(self.vel_ref), -1, -500):
            p = v if self.vel_ref > 0 else -v
            self.mover(p, p, p, p)
            time.sleep(0.05)
        self.mover(0, 0, 0, 0)

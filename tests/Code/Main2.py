from ultrasonic import Ultrasonic
from motor import Ordinary_Car
from servo import Servo
import time
import threading

# Inicializar componentes
motor = Ordinary_Car()
sonic = Ultrasonic()
servo = Servo()

# Flag para controlar el thread de distancia
lectura_activa = True

# Función para leer distancia en paralelo
def leer_distancia_continua():
    while lectura_activa:
        distance = sonic.get_distance()
        print(f"Distancia: {distance} cm")
        time.sleep(0.5)  # Lee cada 0.5 segundos

# Iniciar thread de lectura de distancia
thread_distancia = threading.Thread(target=leer_distancia_continua)
thread_distancia.start()

try:
    # CASO 1: Mover motores hacia adelante
    print("Moviendo motores adelante...")
    motor.set_motor_model(2000, 2000, 2000, 2000)
    time.sleep(2)

    # CASO 2: Barrido del servo del ultrasonido
    servo.set_servo_pwm('1', 90)  # Coloca Servo de camara con vista al frente
    print("Barrido del servo de 30° a 150°...")
    for ciclo in range(3):  # 3 ciclos de barrido Seervo horizontal
        # Barrido de 30° a 150°
        for angulo in range(30, 151, 5):
            servo.set_servo_pwm('0', angulo)
            time.sleep(0.02)  # ~0.5s por barrido

        # Barrido de 150° a 30°
        for angulo in range(150, 29, -5):
            servo.set_servo_pwm('0', angulo)
            time.sleep(0.02)  # ~0.5s por barrido

    # Detener motores
    print("Deteniendo...")
    motor.set_motor_model(0, 0, 0, 0)

except KeyboardInterrupt:
    print("\nPrograma interrumpido")

finally:
    # Detener thread de distancia
    lectura_activa = False
    thread_distancia.join(timeout=1)

    # Limpieza
    motor.close()
    sonic.close()
    print("Fin del programa")

#!/usr/bin/env python3
"""
Script de prueba para leer todos los sensores del Rover
Lee y muestra en el terminal los valores de:
- Sensor ultrasónico (distancia)
- Sensores infrarrojos (3 sensores de línea)
- Fotorresistores (izquierdo y derecho)
- ADC (voltajes analógicos)
"""

import sys
import os
import time
import RPi.GPIO as GPIO


# Importar las clases de los sensores
from ultrasonic import SensorUltrasonico
from infrared import Infrared
from photoresistor import Photoresistor
from adc import ADC

def main():
    """Función principal que lee todos los sensores."""
    print("=" * 60)
    print("SISTEMA DE LECTURA DE SENSORES DEL ROVER")
    print("=" * 60)
    print("Inicializando sensores...")

    # Configurar GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Inicializar sensores
    try:
        ultrasonic = SensorUltrasonico(trig=16, echo=18)
        print("✓ Sensor ultrasónico inicializado")
    except Exception as e:
        print(f"✗ Error al inicializar sensor ultrasónico: {e}")
        ultrasonic = None

    try:
        infrared = Infrared()
        print("✓ Sensores infrarrojos inicializados")
    except Exception as e:
        print(f"✗ Error al inicializar sensores infrarrojos: {e}")
        infrared = None

    try:
        photoresistor = Photoresistor()
        print("✓ Fotorresistores inicializados")
    except Exception as e:
        print(f"✗ Error al inicializar fotorresistores: {e}")
        photoresistor = None

    try:
        adc = ADC()
        print("✓ ADC inicializado")
    except Exception as e:
        print(f"✗ Error al inicializar ADC: {e}")
        adc = None

    print("\nPresiona Ctrl+C para detener el programa\n")
    print("=" * 60)

    try:
        while True:
            print("\n" + "─" * 60)
            print(f"Lectura de sensores - {time.strftime('%H:%M:%S')}")
            print("─" * 60)

            # Leer sensor ultrasónico
            if ultrasonic:
                try:
                    distancia = ultrasonic.obtener_distancia()
                    print(f"📏 ULTRASÓNICO:")
                    print(f"   └─ Distancia: {distancia} cm")
                except Exception as e:
                    print(f"📏 ULTRASÓNICO: Error - {e}")

            # Leer sensores infrarrojos
            if infrared:
                try:
                    ir_combined = infrared.read_all_infrared()
                    ir1 = infrared.read_one_infrared(1)
                    ir2 = infrared.read_one_infrared(2)
                    ir3 = infrared.read_one_infrared(3)
                    print(f"\n🔴 INFRARROJOS:")
                    print(f"   ├─ Sensor 1 (Izq):    {ir1}")
                    print(f"   ├─ Sensor 2 (Centro): {ir2}")
                    print(f"   ├─ Sensor 3 (Der):    {ir3}")
                    print(f"   └─ Valor combinado:   {ir_combined:03b} (binario) = {ir_combined} (decimal)")
                except Exception as e:
                    print(f"\n🔴 INFRARROJOS: Error - {e}")

            # Leer fotorresistores
            if photoresistor:
                try:
                    left_value = photoresistor.read_left_photoresistor()
                    right_value = photoresistor.read_right_photoresistor()
                    print(f"\n💡 FOTORRESISTORES:")
                    print(f"   ├─ Izquierdo: {left_value} V")
                    print(f"   └─ Derecho:   {right_value} V")
                except Exception as e:
                    print(f"\n💡 FOTORRESISTORES: Error - {e}")

            # Leer ADC
            if adc:
                try:
                    adc_ch0 = adc.read_adc(0)
                    adc_ch1 = adc.read_adc(1)
                    adc_ch2 = adc.read_adc(2)
                    power = adc_ch2 * (3 if adc.pcb_version == 1 else 2)
                    print(f"\n⚡ ADC:")
                    print(f"   ├─ Canal 0: {adc_ch0} V")
                    print(f"   ├─ Canal 1: {adc_ch1} V")
                    print(f"   ├─ Canal 2: {adc_ch2} V")
                    print(f"   └─ Potencia estimada: {power:.2f} V")
                except Exception as e:
                    print(f"\n⚡ ADC: Error - {e}")

            print("─" * 60)
            time.sleep(1)  # Esperar 1 segundo antes de la próxima lectura

    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("FINALIZANDO PROGRAMA...")
        print("=" * 60)

        # Limpiar recursos
        if infrared:
            try:
                infrared.close()
                print("✓ Sensores infrarrojos cerrados")
            except Exception as e:
                print(f"✗ Error al cerrar infrarrojos: {e}")

        if photoresistor:
            try:
                photoresistor.stop()
                print("✓ Fotorresistores cerrados")
            except Exception as e:
                print(f"✗ Error al cerrar fotorresistores: {e}")

        if adc:
            try:
                adc.close_i2c()
                print("✓ ADC cerrado")
            except Exception as e:
                print(f"✗ Error al cerrar ADC: {e}")

        GPIO.cleanup()
        print("✓ GPIO limpiado")
        print("\n¡Programa terminado correctamente!\n")

if __name__ == "__main__":
    main()

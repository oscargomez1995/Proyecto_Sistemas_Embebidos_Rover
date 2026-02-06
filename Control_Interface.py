import tkinter as tk
from tkinter import messagebox
import threading
import time
import RPi.GPIO as GPIO
from modules.ultrasonic import SensorUltrasonico
from modules.motor_ctrl import ControlMotores

class RoverControlInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Rover Control Interface")
        self.root.geometry("600x700")
        self.root.configure(bg='#2c3e50')

        # Inicialización de GPIO
        GPIO.setmode(GPIO.BOARD)

        # Variables de control
        self.DISTANCIA_COMPARTIDA = 100.0
        self.LOCK = threading.Lock()
        self.EJECUTANDO = False
        self.modo_manual = False
        self.tecla_presionada = None

        # Inicializar componentes
        self.motores = ControlMotores()
        self.sensor = SensorUltrasonico(16, 18)

        # Velocidades configurables
        self.VEL_MANUAL = 2500
        self.VEL_RAPIDA = 3800
        self.VEL_LENTA = 1800

        self._crear_interfaz()
        self._iniciar_hilo_sensor()

    def _crear_interfaz(self):
        # Título
        titulo = tk.Label(self.root, text="🚗 ROVER CONTROL PANEL",
                         font=('Arial', 24, 'bold'),
                         bg='#2c3e50', fg='white')
        titulo.pack(pady=20)

        # Frame de información del sensor
        self.frame_sensor = tk.Frame(self.root, bg='#34495e', relief=tk.RAISED, bd=3)
        self.frame_sensor.pack(pady=10, padx=20, fill='x')

        tk.Label(self.frame_sensor, text="📏 Distancia del Sensor",
                font=('Arial', 14, 'bold'), bg='#34495e', fg='white').pack(pady=5)

        self.distancia_label = tk.Label(self.frame_sensor, text="-- cm",
                                       font=('Arial', 32, 'bold'),
                                       bg='#34495e', fg='#2ecc71')
        self.distancia_label.pack(pady=10)

        # Frame de controles de coreografía
        frame_coreo = tk.LabelFrame(self.root, text="Coreografía Automática",
                                    font=('Arial', 12, 'bold'),
                                    bg='#34495e', fg='white', bd=3)
        frame_coreo.pack(pady=10, padx=20, fill='x')

        self.btn_iniciar_coreo = tk.Button(frame_coreo, text="▶ Iniciar Coreografía",
                                          command=self._iniciar_coreografia,
                                          font=('Arial', 12, 'bold'),
                                          bg='#27ae60', fg='white',
                                          activebackground='#2ecc71',
                                          width=20, height=2)
        self.btn_iniciar_coreo.pack(pady=10, padx=10, side='left')

        self.btn_detener = tk.Button(frame_coreo, text="⏹ Detener",
                                     command=self._detener_todo,
                                     font=('Arial', 12, 'bold'),
                                     bg='#e74c3c', fg='white',
                                     activebackground='#c0392b',
                                     width=15, height=2)
        self.btn_detener.pack(pady=10, padx=10, side='left')

        # Estado de la coreografía
        self.estado_label = tk.Label(frame_coreo, text="Estado: Detenido",
                                     font=('Arial', 10),
                                     bg='#34495e', fg='#ecf0f1')
        self.estado_label.pack(pady=5)

        # Frame de control manual
        frame_manual = tk.LabelFrame(self.root, text="Control Manual",
                                     font=('Arial', 12, 'bold'),
                                     bg='#34495e', fg='white', bd=3)
        frame_manual.pack(pady=10, padx=20, fill='both', expand=True)

        # Botón para activar modo manual
        self.btn_modo_manual = tk.Button(frame_manual, text="🎮 Activar Modo Manual",
                                        command=self._toggle_modo_manual,
                                        font=('Arial', 11, 'bold'),
                                        bg='#3498db', fg='white',
                                        activebackground='#2980b9',
                                        width=25, height=1)
        self.btn_modo_manual.pack(pady=10)

        # Instrucciones
        instrucciones = tk.Label(frame_manual,
                                text="Usa las flechas del teclado para controlar el rover\n↑ Adelante | ↓ Atrás | ← Izquierda | → Derecha",
                                font=('Arial', 9), bg='#34495e', fg='#95a5a6')
        instrucciones.pack(pady=5)

        # Controles direccionales visuales
        frame_flechas = tk.Frame(frame_manual, bg='#34495e')
        frame_flechas.pack(pady=20)

        # Fila superior (Arriba)
        frame_arriba = tk.Frame(frame_flechas, bg='#34495e')
        frame_arriba.grid(row=0, column=1, pady=5)

        self.btn_arriba = tk.Button(frame_arriba, text="▲",
                                    font=('Arial', 20, 'bold'),
                                    bg='#95a5a6', fg='white',
                                    width=4, height=2,
                                    state='disabled')
        self.btn_arriba.pack()

        # Fila media (Izquierda, Detener, Derecha)
        frame_medio = tk.Frame(frame_flechas, bg='#34495e')
        frame_medio.grid(row=1, column=0, columnspan=3, pady=5)

        self.btn_izquierda = tk.Button(frame_medio, text="◄",
                                       font=('Arial', 20, 'bold'),
                                       bg='#95a5a6', fg='white',
                                       width=4, height=2,
                                       state='disabled')
        self.btn_izquierda.grid(row=0, column=0, padx=5)

        self.btn_stop = tk.Button(frame_medio, text="■",
                                 font=('Arial', 20, 'bold'),
                                 bg='#e74c3c', fg='white',
                                 width=4, height=2,
                                 state='disabled')
        self.btn_stop.grid(row=0, column=1, padx=5)

        self.btn_derecha = tk.Button(frame_medio, text="►",
                                     font=('Arial', 20, 'bold'),
                                     bg='#95a5a6', fg='white',
                                     width=4, height=2,
                                     state='disabled')
        self.btn_derecha.grid(row=0, column=2, padx=5)

        # Fila inferior (Abajo)
        frame_abajo = tk.Frame(frame_flechas, bg='#34495e')
        frame_abajo.grid(row=2, column=1, pady=5)

        self.btn_abajo = tk.Button(frame_abajo, text="▼",
                                   font=('Arial', 20, 'bold'),
                                   bg='#95a5a6', fg='white',
                                   width=4, height=2,
                                   state='disabled')
        self.btn_abajo.pack()

        # Control de velocidad
        frame_velocidad = tk.Frame(frame_manual, bg='#34495e')
        frame_velocidad.pack(pady=10)

        tk.Label(frame_velocidad, text="Velocidad Manual:",
                font=('Arial', 10), bg='#34495e', fg='white').pack(side='left', padx=5)

        self.velocidad_scale = tk.Scale(frame_velocidad, from_=1000, to=4000,
                                       orient='horizontal', length=200,
                                       bg='#34495e', fg='white',
                                       command=self._actualizar_velocidad)
        self.velocidad_scale.set(self.VEL_MANUAL)
        self.velocidad_scale.pack(side='left', padx=5)

        self.vel_valor_label = tk.Label(frame_velocidad, text=f"{self.VEL_MANUAL}",
                                        font=('Arial', 10, 'bold'),
                                        bg='#34495e', fg='#f39c12')
        self.vel_valor_label.pack(side='left', padx=5)

    def _actualizar_velocidad(self, valor):
        """Actualiza el valor de velocidad manual"""
        self.VEL_MANUAL = int(valor)
        self.vel_valor_label.config(text=f"{self.VEL_MANUAL}")

    def _toggle_modo_manual(self):
        """Activa/desactiva el modo de control manual"""
        if not self.modo_manual:
            if self.EJECUTANDO:
                messagebox.showwarning("Advertencia",
                                      "Detén la coreografía antes de activar el modo manual")
                return

            self.modo_manual = True
            self.btn_modo_manual.config(text="🎮 Desactivar Modo Manual", bg='#e67e22')
            self._habilitar_controles_manuales()
            self._iniciar_control_teclado()
            self.estado_label.config(text="Estado: Modo Manual Activo")
        else:
            self.modo_manual = False
            self.btn_modo_manual.config(text="🎮 Activar Modo Manual", bg='#3498db')
            self._deshabilitar_controles_manuales()
            self.motores.mover(0, 0, 0, 0)
            self.estado_label.config(text="Estado: Detenido")

    def _habilitar_controles_manuales(self):
        """Habilita los botones de control manual"""
        self.btn_arriba.config(state='normal')
        self.btn_abajo.config(state='normal')
        self.btn_izquierda.config(state='normal')
        self.btn_derecha.config(state='normal')
        self.btn_stop.config(state='normal')

    def _deshabilitar_controles_manuales(self):
        """Deshabilita los botones de control manual"""
        self.btn_arriba.config(state='disabled', bg='#95a5a6')
        self.btn_abajo.config(state='disabled', bg='#95a5a6')
        self.btn_izquierda.config(state='disabled', bg='#95a5a6')
        self.btn_derecha.config(state='disabled', bg='#95a5a6')
        self.btn_stop.config(state='disabled', bg='#e74c3c')

    def _iniciar_control_teclado(self):
        """Configura los eventos de teclado para el control manual"""
        self.root.bind('<KeyPress-Up>', lambda _: self._manejar_tecla('arriba', True))
        self.root.bind('<KeyRelease-Up>', lambda _: self._manejar_tecla('arriba', False))

        self.root.bind('<KeyPress-Down>', lambda _: self._manejar_tecla('abajo', True))
        self.root.bind('<KeyRelease-Down>', lambda _: self._manejar_tecla('abajo', False))

        self.root.bind('<KeyPress-Left>', lambda _: self._manejar_tecla('izquierda', True))
        self.root.bind('<KeyRelease-Left>', lambda _: self._manejar_tecla('izquierda', False))

        self.root.bind('<KeyPress-Right>', lambda _: self._manejar_tecla('derecha', True))
        self.root.bind('<KeyRelease-Right>', lambda _: self._manejar_tecla('derecha', False))

    def _manejar_tecla(self, direccion, presionada):
        """Maneja los eventos de presión y liberación de teclas"""
        if not self.modo_manual:
            return

        if presionada:
            self.tecla_presionada = direccion
            self._ejecutar_movimiento(direccion)
        else:
            if self.tecla_presionada == direccion:
                self.tecla_presionada = None
                self.motores.mover(0, 0, 0, 0)
                self._resetear_botones_visuales()

    def _ejecutar_movimiento(self, direccion):
        """Ejecuta el movimiento según la dirección"""
        v = self.VEL_MANUAL

        if direccion == 'arriba':
            self.motores.mover(v, v, v, v)
            self.btn_arriba.config(bg='#2ecc71')
        elif direccion == 'abajo':
            self.motores.mover(-v, -v, -v, -v)
            self.btn_abajo.config(bg='#2ecc71')
        elif direccion == 'izquierda':
            self.motores.mover(-v, -v, v, v)
            self.btn_izquierda.config(bg='#2ecc71')
        elif direccion == 'derecha':
            self.motores.mover(v, v, -v, -v)
            self.btn_derecha.config(bg='#2ecc71')

    def _resetear_botones_visuales(self):
        """Resetea el color de los botones visuales"""
        self.btn_arriba.config(bg='#95a5a6')
        self.btn_abajo.config(bg='#95a5a6')
        self.btn_izquierda.config(bg='#95a5a6')
        self.btn_derecha.config(bg='#95a5a6')

    def _iniciar_hilo_sensor(self):
        """Inicia el hilo que monitorea constantemente el sensor ultrasónico"""
        def actualizar_sensor():
            while True:
                try:
                    d = self.sensor.obtener_distancia()
                    with self.LOCK:
                        self.DISTANCIA_COMPARTIDA = d

                    # Actualizar la interfaz
                    self.root.after(0, self._actualizar_display_distancia, d)
                    time.sleep(0.1)
                except Exception as e:
                    print(f"Error en sensor: {e}")
                    time.sleep(0.5)

        hilo = threading.Thread(target=actualizar_sensor, daemon=True)
        hilo.start()

    def _actualizar_display_distancia(self, distancia):
        """Actualiza el display de distancia en la interfaz"""
        self.distancia_label.config(text=f"{distancia:.1f} cm")

        # Cambiar color según la distancia
        if distancia < 15:
            self.distancia_label.config(fg='#e74c3c')  # Rojo
        elif distancia < 30:
            self.distancia_label.config(fg='#f39c12')  # Naranja
        else:
            self.distancia_label.config(fg='#2ecc71')  # Verde

    def _iniciar_coreografia(self):
        """Inicia la coreografía automática del main.py"""
        if self.EJECUTANDO:
            messagebox.showwarning("Advertencia", "La coreografía ya está en ejecución")
            return

        if self.modo_manual:
            messagebox.showwarning("Advertencia",
                                  "Desactiva el modo manual antes de iniciar la coreografía")
            return

        self.EJECUTANDO = True
        self.btn_iniciar_coreo.config(state='disabled')
        self.estado_label.config(text="Estado: Ejecutando Coreografía...")

        hilo = threading.Thread(target=self._ejecutar_coreografia, daemon=True)
        hilo.start()

    def _ejecutar_coreografia(self):
        """Ejecuta la secuencia de movimientos (coreografía del main.py)"""
        def mover_seguro(v1, v2, v3, v4, duracion, nombre):
            """Función auxiliar para mover con chequeo de obstáculo"""
            self.root.after(0, lambda: self.estado_label.config(text=f"Estado: {nombre}"))

            inicio = time.time()
            while time.time() - inicio < duracion and self.EJECUTANDO:
                with self.LOCK:
                    if self.DISTANCIA_COMPARTIDA < 15:
                        print(f"¡EMERGENCIA! Obstáculo a {self.DISTANCIA_COMPARTIDA}cm. Abortando.")
                        self.motores.mover(0, 0, 0, 0)
                        self.root.after(0, lambda: messagebox.showerror(
                            "Emergencia",
                            f"Obstáculo detectado a {self.DISTANCIA_COMPARTIDA:.1f}cm. Coreografía abortada."))
                        return False

                self.motores.mover(v1, v2, v3, v4)
                time.sleep(0.1)
            return True

        try:
            print("--- INICIANDO COREOGRAFÍA MULTIHILO ---")

            # 1. Avance rápido
            if not mover_seguro(self.VEL_RAPIDA, self.VEL_RAPIDA, self.VEL_RAPIDA, self.VEL_RAPIDA,
                               2, "Avance Rápido"): return

            # 2. Avance lento
            if not mover_seguro(self.VEL_LENTA, self.VEL_LENTA, self.VEL_LENTA, self.VEL_LENTA,
                               4, "Avance Lento"): return

            # 3. Retroceso lento
            if not mover_seguro(-self.VEL_LENTA, -self.VEL_LENTA, -self.VEL_LENTA, -self.VEL_LENTA,
                               2, "Retroceso Lento"): return

            # 4. Retroceso rápido
            if not mover_seguro(-self.VEL_RAPIDA, -self.VEL_RAPIDA, -self.VEL_RAPIDA, -self.VEL_RAPIDA,
                               1, "Retroceso Rápido"): return

            # 5. Giro Izquierda
            if not mover_seguro(-self.VEL_LENTA, -self.VEL_LENTA, self.VEL_LENTA, self.VEL_LENTA,
                               2, "Giro Izquierda"): return

            # 6. Giro Derecha
            if not mover_seguro(self.VEL_LENTA, self.VEL_LENTA, -self.VEL_LENTA, -self.VEL_LENTA,
                               2, "Giro Derecha"): return

            # 7. Rotación final
            if not mover_seguro(self.VEL_LENTA, self.VEL_LENTA, -self.VEL_LENTA, -self.VEL_LENTA,
                               5, "Rotación Final"): return

            print("--- COREOGRAFÍA FINALIZADA EXITOSAMENTE ---")
            self.root.after(0, lambda: messagebox.showinfo("Éxito",
                                                          "Coreografía completada exitosamente"))

        except Exception as e:
            print(f"Error en coreografía: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error",
                                                            f"Error en coreografía: {e}"))
        finally:
            self.motores.mover(0, 0, 0, 0)
            self.EJECUTANDO = False
            self.root.after(0, self._finalizar_coreografia)

    def _finalizar_coreografia(self):
        """Limpia el estado después de finalizar la coreografía"""
        self.btn_iniciar_coreo.config(state='normal')
        self.estado_label.config(text="Estado: Detenido")

    def _detener_todo(self):
        """Detiene todos los movimientos y procesos"""
        self.EJECUTANDO = False
        self.modo_manual = False
        self.motores.mover(0, 0, 0, 0)
        self.btn_modo_manual.config(text="🎮 Activar Modo Manual", bg='#3498db')
        self._deshabilitar_controles_manuales()
        self.btn_iniciar_coreo.config(state='normal')
        self.estado_label.config(text="Estado: Detenido")

    def cerrar_aplicacion(self):
        """Limpia recursos al cerrar la aplicación"""
        self.EJECUTANDO = False
        self.modo_manual = False
        self.motores.mover(0, 0, 0, 0)
        GPIO.cleanup()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = RoverControlInterface(root)
    root.protocol("WM_DELETE_WINDOW", app.cerrar_aplicacion)
    root.mainloop()

if __name__ == "__main__":
    main()

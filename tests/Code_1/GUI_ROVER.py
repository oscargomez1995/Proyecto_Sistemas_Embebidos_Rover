import sys
import threading
import time
import webbrowser # Para abrir el stream de la cámara
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QGridLayout, QHBoxLayout)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

# --- SIMULADOR DE HARDWARE (Para PC/Windows) ---
class MockHardware:
    def mover(self, v1, v2, v3, v4): 
        print(f"HARDWARE -> Motores: L[{v1},{v2}] R[{v3},{v4}]")
    def obtener_distancia(self): return 25.0

try:
    import RPi.GPIO as GPIO
    from modules.motor_ctrl import ControlMotores
    MODO_REAL = True
except ImportError:
    MODO_REAL = False

class VentanaRover(QWidget):
    def __init__(self):
        super().__init__()
        self.motores = ControlMotores() if MODO_REAL else MockHardware()
        self.vel = 2500 
        self.ip_raspberry = "192.168.1.100" # <-- CAMBIA ESTO por la IP de tu Rover
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Freenove Smart Car - Control Maestro')
        self.setStyleSheet("background-color: #1e272e; color: white; font-family: 'Segoe UI', Arial;")
        
        layout_principal = QVBoxLayout()

        # 1. Indicador de Estado
        self.lbl_status = QLabel('SISTEMA ' + ('CONECTADO' if MODO_REAL else 'SIMULADO'))
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("font-size: 14px; color: #05c46b; font-weight: bold; margin-bottom: 5px;")
        layout_principal.addWidget(self.lbl_status)

        # 2. BOTÓN DE CÁMARA (Nuevo)
        self.btn_camara = QPushButton('📷 ABRIR CÁMARA (STREAM)')
        self.btn_camara.setStyleSheet("""
            QPushButton { 
                background-color: #0fbcf9; color: white; font-size: 15px; 
                font-weight: bold; padding: 12px; border-radius: 8px; 
            }
            QPushButton:hover { background-color: #4bcffa; }
        """)
        self.btn_camara.clicked.connect(self.abrir_camara)
        layout_principal.addWidget(self.btn_camara)

        layout_principal.addSpacing(15)

        # 3. Control Direccional (Cruceta)
        grid = QGridLayout()
        btn_style = """
            QPushButton { 
                background-color: #485460; font-size: 20px; border-radius: 15px; padding: 20px; 
            } 
            QPushButton:pressed { background-color: #05c46b; }
        """
        
        self.btn_up = QPushButton('▲'); self.btn_up.setStyleSheet(btn_style)
        self.btn_down = QPushButton('▼'); self.btn_down.setStyleSheet(btn_style)
        self.btn_left = QPushButton('◀'); self.btn_left.setStyleSheet(btn_style)
        self.btn_right = QPushButton('▶'); self.btn_right.setStyleSheet(btn_style)
        self.btn_stop = QPushButton('STOP')
        self.btn_stop.setStyleSheet(btn_style + "QPushButton { color: #ff5e57; font-weight: bold; }")

        grid.addWidget(self.btn_up, 0, 1)
        grid.addWidget(self.btn_left, 1, 0)
        grid.addWidget(self.btn_stop, 1, 1)
        grid.addWidget(self.btn_right, 1, 2)
        grid.addWidget(self.btn_down, 2, 1)
        layout_principal.addLayout(grid)

        layout_principal.addSpacing(20)

        # 4. Botón de Coreografía
        self.btn_coreo = QPushButton('EJECUTAR MOVIMIENTOS')
        self.btn_coreo.setStyleSheet("""
            QPushButton { 
                background-color: #575fcf; color: white; font-size: 14px; 
                font-weight: bold; padding: 12px; border-radius: 8px; 
            }
            QPushButton:hover { background-color: #3c40c6; }
        """)
        self.btn_coreo.clicked.connect(self.iniciar_hilo_coreografia)
        layout_principal.addWidget(self.btn_coreo)

        # Conectar eventos
        self.btn_up.clicked.connect(lambda: self.mover("adelante"))
        self.btn_down.clicked.connect(lambda: self.mover("atras"))
        self.btn_left.clicked.connect(lambda: self.mover("izquierda"))
        self.btn_right.clicked.connect(lambda: self.mover("derecha"))
        self.btn_stop.clicked.connect(lambda: self.mover("parar"))

        self.setLayout(layout_principal)

    def abrir_camara(self):
        # El Chapter 7 de Freenove suele usar el puerto 8080 o 5000 para el stream
        url = f"http://{self.ip_raspberry}:8080" 
        print(f"Abriendo stream de cámara en: {url}")
        webbrowser.open(url)

    def mover(self, accion):
        v = self.vel
        if accion == "adelante": self.motores.mover(v, v, v, v)
        elif accion == "atras": self.motores.mover(-v, -v, -v, -v)
        elif accion == "izquierda": self.motores.mover(-v, -v, v, v)
        elif accion == "derecha": self.motores.mover(v, v, -v, -v)
        elif accion == "parar": self.motores.mover(0, 0, 0, 0)

    def iniciar_hilo_coreografia(self):
        threading.Thread(target=self.secuencia_coreografia, daemon=True).start()

    def secuencia_coreografia(self):
        print("Iniciando secuencia...")
        self.mover("adelante"); time.sleep(1)
        self.mover("parar")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VentanaRover()
    ex.show()
    sys.exit(app.exec_())

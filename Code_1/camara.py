import cv2
import time

def probar_camara():
    print("--- Probando Cámara Freenove (Smart Car) ---")
    
    # Inicializar la cámara (0 suele ser la cámara de la Raspberry)
    # Si usas la cámara oficial o USB, el índice suele ser 0 o -1
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara.")
        return

    print("Cámara detectada. Presiona 'q' para salir.")
    
    # Configurar resolución (opcional, para mejorar velocidad)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    try:
        while True:
            # Capturar frame por frame
            ret, frame = cap.read()

            if not ret:
                print("Error al recibir el frame.")
                break

            # Mostrar el video en una ventana
            cv2.imshow('Prueba de Camara Rover', frame)

            # Salir si se presiona la tecla 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nPrueba detenida por el usuario.")
    
    finally:
        # Liberar recursos
        cap.release()
        cv2.destroyAllWindows()
        print("Recursos liberados correctamente.")

if __name__ == "__main__":
    probar_camara()

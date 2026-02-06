class CerebroRover:
    def __init__(self):
        self.distancia_segura = 25.0 # cm

    def decidir_accion(self, distancia_actual):
        """Lógica de navegación básica"""
        if distancia_actual > self.distancia_segura:
            return "AVANZAR"
        elif distancia_actual > 10:
            return "GIRAR"
        else:
            return "RETROCEDER"

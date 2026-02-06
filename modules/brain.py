class CerebroRover:
    def __init__(self):
        # Umbrales de distancia en centímetros
        self.distancia_critica = 25.0  # Menos de esto: FRENAR
        self.distancia_segura = 50.0   # Entre 25 y 50: AVANZAR_LENTO
                                       # Más de 50: AVANZAR_RAPIDO

    def decidir_accion(self, distancia):
        """Asocia la distancia leída con un estado de movimiento"""
        if distancia <= self.distancia_critica:
            return "FRENAR"
        elif distancia <= self.distancia_segura:
            return "AVANZAR_LENTO"
        else:
            return "AVANZAR_RAPIDO"

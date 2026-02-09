class CerebroRover:
    def __init__(self):
        self.distancia_critica = 25.0
        self.distancia_segura = 50.0

    def decidir_accion(self, distancia):
        # Si la distancia es negativa o un error (0), tratamos como peligro
        if distancia <= 0:
            return "FRENAR"
            
        if distancia <= self.distancia_critica:
            return "FRENAR"
        elif distancia <= self.distancia_segura:
            return "AVANZAR_LENTO"
        else:
            return "AVANZAR_RAPIDO"

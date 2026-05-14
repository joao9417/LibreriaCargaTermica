import math

class CalculadoraCargaPersonas:
    """
    Modulo 4a: Calculo de carga termica aportada por personas.
    Basado en los estandares del Manual de refrigeracion ASHRAE.
    """

    # Tabla estandar ASHRAE (Temperatura en °C, Calor en BTU/hr)
    TABLA_ASHRAE = [
        (10.0, 720.0),
        (4.4, 840.0),
        (-1.1, 950.0),
        (-6.7, 1050.0),
        (-12.2, 1200.0),
        (-17.8, 1300.0),
        (-23.3, 1400.0),
        (-28.9, 1500.0)
    ]

    def __init__(self, temp_camara_c: float, cantidad_personas: int, tiempo_horas: float):
        self.temp_camara_c = temp_camara_c
        self.cantidad_personas = cantidad_personas
        self.tiempo_horas = tiempo_horas

    def _obtener_calor_por_persona(self) -> float:
        """
        Calcula los BTU/hr emitidos por una persona segun la temperatura de la camara.
        utiliza una logica segura que asigna el valor normativo mas cercano hacia el lado seguro.
        """
        # Si la temperatura es mas caliente que 10°C, usamos el minimo de ASHRAE
        if self.temp_camara_c >= self.TABLA_ASHRAE[0][0]:
            return self.TABLA_ASHRAE[0][1]
        
        # Si la temperatura es mas fria que -28.9°C, usamos el maximo de ASHRAE
        if self.temp_camara_c <= self.TABLA_ASHRAE[-1][0]:
            return self.TABLA_ASHRAE[-1][1]
        
        # Busca el valor correcto en la tabla (Interpolacion Logica)
        for i in range(len(self.TABLA_ASHRAE) - 1):
            temp_superior = self.TABLA_ASHRAE[i][0]
            temp_inferior = self.TABLA_ASHRAE[i+1][0]
            calor_superior = self.TABLA_ASHRAE[i][1]
            calor_inferior = self.TABLA_ASHRAE[i+1][1]

            if temp_inferior <= self.temp_camara_c <= temp_superior:
                # Interpolacion lineal
                # Asi evitamos saltos bruscos entre temperaturas cercanas.
                proporcion = (self.temp_camara_c - temp_inferior) / (temp_superior - temp_inferior)
                calor_interpolado = calor_inferior + proporcion * (calor_superior - calor_inferior)
                return round(calor_interpolado, 2)
        
        return 0.0
    
    def calcular_carga(self) -> dict:
        """
        Calcula la carga total de BTU/Dia aportada por las personas.
        """
        # Si no hay personas o tiempo, la carga es 0.
        if self.cantidad_personas <= 0 or self.tiempo_horas <= 0:
            return {
                'tipo': 'Personas',
                'cantidad': 0,
                'calor_unitario_btuh': 0,
                'TOTAL_SUPLEMENTARIA': 0
            }

        calor_unitario = self._obtener_calor_por_persona()

        total_btu_dia = self.cantidad_personas * calor_unitario * self.tiempo_horas

        return {
            'tipo': 'Personas',
            'cantidad': self.cantidad_personas,
            'horas_operacion': self.tiempo_horas,
            'calor_unitario_btuh': calor_unitario,
            'TOTAL_SUPLEMENTARIA': round(total_btu_dia)
        }

class CalculadoraIluminacion:
    """
    Modulo 4b: Calculo de carga termica aportada por iluminacion.
    """
    def __init__(self, largo_m: float, ancho_m: float, alto_m: float, luxes_deseados: float, horas_uso: float, potencia_lampara_w: float):
        self.largo_m = largo_m
        self.ancho_m = ancho_m
        self.alto_m = alto_m
        self.luxes_deseados = luxes_deseados
        self.horas_uso = horas_uso
        self.potencia_lampara_w = potencia_lampara_w

        # Estandares industriales para cuartos frios
        self.FACTOR_PERDIDA_LUZ = 0.80 # Depreciacion por frio/polvo
        self.EFICACIA_LED = 140.0 # lm/W (Lumens por Watt)
        self.W_TO_BTUHR = 3.412 # BTU/hr por Watt

    def _calcular_coeficiente_utilizacion(self) -> float:
        """
        Calcula el CU dinamico basado en la geometria del cuarto (RCR).
        """
        altura_cavidad = self.alto_m - 0.85 # Distancia de la lampara al area de trabajo

        # Formula del indice de cavidad del local (RCR)
        # Entre mas alto y estrecho el cuarto, mayor es el RCR y mas luz se pierde.
        rcr = (5 * altura_cavidad * (self.largo_m + self.ancho_m)) / (self.largo_m * self.ancho_m)

        # Interpolacion lineal simple para CU en cuartos blancos (0.80 max, castigado por RCR)
        # Por cada punto de RCR, perdemos aprox 4% de aprovechamiento de luz
        cu_dinamico = 0.80 - (rcr * 0.04)

        # Limite de seguridad: el CU nunca debe ser menor a 0.30 en paneles blancos
        return max(cu_dinamico, 0.30)


    
    def calcular_watts_necesarios(self) -> float:
        """
        Simulacion diseño luminico para encontrar los watts totales requeridos.
        """
        area = self.largo_m * self.ancho_m
        cu = self._calcular_coeficiente_utilizacion()

        # Fórmula: Lumens = (Lux * Area) / (CU * LLF)
        lumens_totales = (self.luxes_deseados * area) / (cu * self.FACTOR_PERDIDA_LUZ)

        # Watts = Lumens / Eficacia
        watts_totales = lumens_totales / self.EFICACIA_LED
        return round(watts_totales, 2)

    def calcular_carga(self) -> dict:
        """
        Calcula la carga termica diaria en BTU.
        """
        watts_teoricos = self.calcular_watts_necesarios()

        # Calculo cantidad fisica de lamparas (redondeando hacia arriba)
        if self.potencia_lampara_w > 0:
            cantidad_lamparas = math.ceil(watts_teoricos / self.potencia_lampara_w)
        else:
            cantidad_lamparas = 0

        # El 100% de la potencia electrica en luces dentro del cuarto se vuelve calor
        watts_reales_instalados = cantidad_lamparas * self.potencia_lampara_w
        btu_dia = watts_reales_instalados * self.W_TO_BTUHR * self.horas_uso

        # Calculo de luxes reales para el diseño
        cu = self._calcular_coeficiente_utilizacion()
        area = self.largo_m * self.ancho_m
        lumens_reales = watts_reales_instalados * self.EFICACIA_LED
        luxes_reales = (lumens_reales * cu * self.FACTOR_PERDIDA_LUZ) / area

        return {
            'tipo': 'Iluminacion',
            'area_m2': round(area, 2),
            'watts_teoricos': round(watts_teoricos, 2),
            'lamparas_sugeridas': cantidad_lamparas,
            'watts_reales': watts_reales_instalados,
            'luxes_calculados': round(luxes_reales),
            'horas_uso': self.horas_uso,
            'TOTAL_SUPLEMENTARIA': round(btu_dia)
        }







# Prueba y Depuracion
if __name__ == "__main__":
    # Test
    calc_personas = CalculadoraCargaPersonas(
        temp_camara_c=-20.0,
        cantidad_personas=2,
        tiempo_horas=16.0
    )

    res = calc_personas.calcular_carga()

    print("\n--- 4a. CARGA SUPLEMENTARIA (PERSONAS) ---")
    print(f"Temperatura Cámara:      -20.0 °C")
    print(f"Personal trabajando:     {res['cantidad']} personas")
    print(f"Tiempo de permanencia:   {res['horas_operacion']} horas")
    print(f"Calor emitido (c/u):     {res['calor_unitario_btuh']} BTU/h (Calculado por ASHRAE)")
    print("-" * 50)
    print(f"TOTAL PERSONAS =         {res['TOTAL_SUPLEMENTARIA']:,} BTU/DIA".replace(',', '.'))
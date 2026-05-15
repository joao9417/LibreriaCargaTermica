import math

class CalculadoraCargaPersonas:
    """
    Modulo 4a: Calculo de carga termica aportada por personas.
    Basado en los estandares del Manual de refrigeracion ASHRAE.
    """
    TABLA_ASHRAE = [
        (10.0, 720.0), (4.4, 840.0), (-1.1, 950.0), (-6.7, 1050.0),
        (-12.2, 1200.0), (-17.8, 1300.0), (-23.3, 1400.0), (-28.9, 1500.0)
    ]

    def __init__(self, temp_camara_c: float, cantidad_personas: int, tiempo_horas: float):
        self.temp_camara_c = temp_camara_c
        self.cantidad_personas = cantidad_personas
        self.tiempo_horas = tiempo_horas

    def _obtener_calor_por_persona(self) -> float:
        if self.temp_camara_c >= self.TABLA_ASHRAE[0][0]: return self.TABLA_ASHRAE[0][1]
        if self.temp_camara_c <= self.TABLA_ASHRAE[-1][0]: return self.TABLA_ASHRAE[-1][1]
        for i in range(len(self.TABLA_ASHRAE) - 1):
            temp_superior = self.TABLA_ASHRAE[i][0]
            temp_inferior = self.TABLA_ASHRAE[i+1][0]
            calor_superior = self.TABLA_ASHRAE[i][1]
            calor_inferior = self.TABLA_ASHRAE[i+1][1]
            if temp_inferior <= self.temp_camara_c <= temp_superior:
                proporcion = (self.temp_camara_c - temp_inferior) / (temp_superior - temp_inferior)
                return round(calor_inferior + proporcion * (calor_superior - calor_inferior), 2)
        return 0.0
    
    def calcular_carga(self) -> dict:
        if self.cantidad_personas <= 0 or self.tiempo_horas <= 0:
            return {'tipo': 'Personas', 'cantidad': 0, 'calor_unitario_btuh': 0, 'TOTAL_SUPLEMENTARIA': 0}
        calor_unitario = self._obtener_calor_por_persona()
        total_btu_dia = self.cantidad_personas * calor_unitario * self.tiempo_horas
        return {
            'tipo': 'Personas', 'cantidad': self.cantidad_personas, 
            'horas_operacion': self.tiempo_horas, 'calor_unitario_btuh': calor_unitario,
            'TOTAL_SUPLEMENTARIA': round(total_btu_dia)
        }

class CalculadoraIluminacion:
    """
    Modulo 4b: Calculo de carga termica aportada por iluminacion.
    """
    def __init__(self, largo_m: float, ancho_m: float, alto_m: float, luxes_deseados: float, 
                 horas_uso: float, potencia_lampara_w: float, eficiencia_lampara_lm_w: float):
        self.largo_m = largo_m
        self.ancho_m = ancho_m
        self.alto_m = alto_m
        self.luxes_deseados = luxes_deseados
        self.horas_uso = horas_uso
        self.potencia_lampara_w = potencia_lampara_w

        self.FACTOR_PERDIDA_LUZ = 0.80 
        self.EFICACIA_LED = eficiencia_lampara_lm_w # Nombre de variable original conservado
        self.W_TO_BTUHR = 3.412 

    def _calcular_coeficiente_utilizacion(self) -> float:
        altura_cavidad = self.alto_m - 0.85 
        rcr = (5 * altura_cavidad * (self.largo_m + self.ancho_m)) / (self.largo_m * self.ancho_m)
        cu_dinamico = 0.80 - (rcr * 0.04)
        return max(cu_dinamico, 0.30)

    def calcular_watts_necesarios(self) -> float:
        area = self.largo_m * self.ancho_m
        cu = self._calcular_coeficiente_utilizacion()
        lumens_totales = (self.luxes_deseados * area) / (cu * self.FACTOR_PERDIDA_LUZ)
        watts_totales = lumens_totales / self.EFICACIA_LED
        return round(watts_totales, 2)

    def calcular_carga(self) -> dict:
        watts_teoricos = self.calcular_watts_necesarios()
        if self.potencia_lampara_w > 0:
            cantidad_lamparas = math.ceil(watts_teoricos / self.potencia_lampara_w)
        else:
            cantidad_lamparas = 0

        watts_reales_instalados = cantidad_lamparas * self.potencia_lampara_w
        btu_dia = watts_reales_instalados * self.W_TO_BTUHR * self.horas_uso

        cu = self._calcular_coeficiente_utilizacion()
        area = self.largo_m * self.ancho_m
        lumens_reales = watts_reales_instalados * self.EFICACIA_LED
        luxes_reales = (lumens_reales * cu * self.FACTOR_PERDIDA_LUZ) / area

        return {
            'tipo': 'Iluminacion', 'area_m2': round(area, 2), 'watts_teoricos': round(watts_teoricos, 2),
            'lamparas_sugeridas': cantidad_lamparas, 'watts_reales': watts_reales_instalados,
            'luxes_calculados': round(luxes_reales), 'horas_uso': self.horas_uso,
            'TOTAL_SUPLEMENTARIA': round(btu_dia)
        }

class CalculadoraEnvases:
    """
    Modulo 4c: Calculo de carga termica por enfriamiento de los envases/canastas.
    """
    def __init__(self, rotacion_kg: float, temp_entrada_c: float, temp_salida_c: float, tamano_canasta_cm: int = 25):
        self.rotacion_kg = rotacion_kg
        self.temp_entrada_c = temp_entrada_c
        self.temp_salida_c = temp_salida_c
        self.tamano_canasta_cm = tamano_canasta_cm
        
        self.CALOR_ESPECIFICO_PLASTICO = 0.12 
        self.PESO_CANASTA_KG = 2.0 
        self.KG_A_LBS = 2.20462

    def calcular_unidades(self) -> float:
        if self.tamano_canasta_cm == 13:
            capacidad_kg_por_canasta = 15.0
        elif self.tamano_canasta_cm == 25:
            capacidad_kg_por_canasta = 25.0
        else:
            return 0.0 
        return self.rotacion_kg / capacidad_kg_por_canasta

    def calcular_carga(self) -> dict:
        unidades = self.calcular_unidades()
        peso_total_lbs = unidades * (self.PESO_CANASTA_KG * self.KG_A_LBS)
        delta_t_c = max(0, self.temp_entrada_c - self.temp_salida_c)
        delta_t_f = delta_t_c * 1.8
        btu_dia = peso_total_lbs * self.CALOR_ESPECIFICO_PLASTICO * delta_t_f
        
        return {
            'tipo': 'Envases y Canastas', 'unidades_estimadas': round(unidades),
            'peso_total_lbs': round(peso_total_lbs, 2), 'delta_t_f': round(delta_t_f, 2),
            'TOTAL_SUPLEMENTARIA': round(btu_dia)
        }

class CalculadoraCargasInternas:
    """
    Modulo 4d: Calculo de carga termica aportada por motores de evaporadores y deshielo.
    Utilizando Diseño parametrico (Relaciones Fisicas) con Ajuste Industrial.
    """
    def __init__(self, temp_camara_c: float, volumen_m3: float, cambios_aire_hora: float, 
                 horas_operacion_equipo: float, hp_adicionales: float = 0.0, watts_adicionales: float = 0.0,
                 cantidad_cargas_hp: int = 1, horas_operacion_hp: float = 8.0,
                 cantidad_cargas_watts: int = 1, horas_operacion_watts: float = 8.0,
                 tipo_evaporador: str = 'industrial_pesado', tipo_deshielo: str = 'gas_caliente'): # Nuevos parámetros opcionales al final para no romper tu código
        
        self.temp_camara_c = temp_camara_c
        self.volumen_m3 = volumen_m3
        self.cambios_aire_hora = cambios_aire_hora
        self.horas_operacion_equipo = horas_operacion_equipo
        
        self.hp_adicionales = hp_adicionales
        self.watts_adicionales = watts_adicionales
        self.cantidad_cargas_hp = cantidad_cargas_hp
        self.horas_operacion_hp = horas_operacion_hp
        self.cantidad_cargas_watts = cantidad_cargas_watts
        self.horas_operacion_watts = horas_operacion_watts
        
        self.tipo_deshielo = tipo_deshielo
        
        # --- CONSTANTES PARAMÉTRICAS INDUSTRIALES CALIBRADAS ---
        # Si es industrial pesado usa 0.118, de lo contrario el 0.025 estandar
        self.WATTS_POR_M3H = 0.118 if tipo_evaporador == 'industrial_pesado' else 0.025
        
        self.WATTS_DESHIELO_POR_BTUH = 0.12 
        # Si es gas caliente solo transfiere el 15%, si es eléctrico el 30%
        self.EFICIENCIA_DESHIELO = 0.15 if tipo_deshielo == 'gas_caliente' else 0.30
        self.HORAS_DESHIELO_DIA = 2.0 
        
        self.W_TO_BTUHR = 3.412
        self.HP_TO_BTUHR = 2544.4

    def calcular_calor_ventiladores(self) -> float:
        caudal_m3h = self.volumen_m3 * self.cambios_aire_hora
        watts_ventiladores = caudal_m3h * self.WATTS_POR_M3H
        
        horas_ventilacion = self.horas_operacion_equipo
        if self.temp_camara_c <= 2.0:
            horas_ventilacion -= self.HORAS_DESHIELO_DIA
            
        btu_dia_ventiladores = watts_ventiladores * self.W_TO_BTUHR * horas_ventilacion
        return btu_dia_ventiladores, watts_ventiladores

    def calcular_calor_deshielo(self, subtotal_carga_btuh: float) -> float:
        if self.temp_camara_c > 2.0:
            return 0.0, 0.0
            
        watts_resistencias_equiv = subtotal_carga_btuh * self.WATTS_DESHIELO_POR_BTUH
        
        # Consumo eléctrico real instalado: 0 si es gas caliente, de lo contrario usa las resistencias
        watts_resistencias_inst = 0 if self.tipo_deshielo == 'gas_caliente' else watts_resistencias_equiv
        
        calor_perdido_cuarto_w = watts_resistencias_equiv * self.EFICIENCIA_DESHIELO
        btu_dia_deshielo = calor_perdido_cuarto_w * self.W_TO_BTUHR * self.HORAS_DESHIELO_DIA
        
        return btu_dia_deshielo, watts_resistencias_inst

    def calcular_carga_equipos_adicionales(self) -> tuple:
        btu_dia_hp = (self.hp_adicionales * self.cantidad_cargas_hp * self.HP_TO_BTUHR) * self.horas_operacion_hp
        btu_dia_watts = (self.watts_adicionales * self.cantidad_cargas_watts * self.W_TO_BTUHR) * self.horas_operacion_watts
        return btu_dia_hp, btu_dia_watts

    def calcular_carga(self, subtotal_carga_previa_dia: float) -> dict:
        subtotal_btuh = subtotal_carga_previa_dia / self.horas_operacion_equipo
        
        btu_dia_vent, watts_vent = self.calcular_calor_ventiladores()
        btu_dia_deshielo, watts_deshielo = self.calcular_calor_deshielo(subtotal_btuh)
        btu_dia_hp, btu_dia_watts = self.calcular_carga_equipos_adicionales()
        
        btu_dia_extra = btu_dia_hp + btu_dia_watts
        total_dia = btu_dia_vent + btu_dia_deshielo + btu_dia_extra
        
        # Retorno con los mismos nombres exactos que tu simulador lee en los 'print'
        return {
            'tipo': 'Cargas Internas Paramétricas',
            'potencia_estimada_ventiladores_W': round(watts_vent),
            'btu_dia_ventiladores': round(btu_dia_vent),
            'potencia_estimada_resistencias_W': round(watts_deshielo),
            'btu_dia_deshielo': round(btu_dia_deshielo),
            'btu_dia_equipos_extra': round(btu_dia_extra),
            'btu_dia_hp_extra': round(btu_dia_hp),
            'btu_dia_watts_extra': round(btu_dia_watts),
            'TOTAL_SUPLEMENTARIA': round(total_dia)
        }
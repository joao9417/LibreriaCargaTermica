class CalculadoraTransmisionTermica:
    """
    Modulo de calculo de carga termica por transmision a traves de la envolvente del camara frigorifica, considerando paredes, techo y piso.
    Basado en estandares industriales y coeficientes empiricos.
    """
    
    FACTORES_K_PARED_TECHO = {0: 5.04, 50: 1.92, 80: 1.28, 100: 0.96, 125: 0.77, 150: 0.64}
    FACTORES_K_PISO = {0: 5.04, 50: 1.32, 80: 0.98, 100: 0.78, 125: 0.65, 150: 0.55}
    M2_A_FT2 = 10.7639
    
    
    def __init__(self, largo_m: float, ancho_m: float, alto_m: float, temp_camara_c: float, temp_exterior_c: float):
        # Dimensiones de entrada en metros
        self.largo_m = largo_m
        self.ancho_m = ancho_m
        self.alto_m = alto_m
        
        # Temperaturas en grados Celsius
        self.temp_camara_c = temp_camara_c
        self.temp_exterior_c = temp_exterior_c
        
        
    
    def obtener_areas(self, unidad: str = "ft2") -> dict:
        """
        Calcula las areas de los paneles considerando el factor de seguridad estructural del 20% (0.2 m) para cada dimensión.
        Parametro unidad: 'm2' para metros cuadrados, 'ft2' para pies cuadrados.
        """
        
        areas_m2 = {
            'techo': (self.largo_m + 0.2) * (self.ancho_m + 0.2),
            'piso': (self.largo_m + 0.2) * (self.ancho_m + 0.2),
            'pared_norte': (self.largo_m + 0.2) * (self.alto_m + 0.2),
            'pared_sur': (self.largo_m + 0.2) * (self.alto_m + 0.2),
            'pared_este': (self.ancho_m + 0.2) * (self.alto_m + 0.2),
            'pared_oeste': (self.ancho_m + 0.2) * (self.alto_m + 0.2)
        } 
        
        if unidad.lower() == 'm2':
            return {panel: round(area, 2) for panel, area in areas_m2.items()}
        elif unidad.lower() == 'ft2':
            return {panel: round(area * self.M2_A_FT2, 2) for panel, area in areas_m2.items()}
        else:
            raise ValueError("Unidad no soportada. Use 'm2' para metros cuadrados o 'ft2' para pies cuadrados.")
        
    
    
    def obtener_deltas_temperatura(self, unidad: str = 'F') -> dict:
        """
        Calcular el diferencial de temperatura considerando asoleamiento y temperatura del suelo según la temperatura exterior.
        Parametro unidad: 'C' para Celsius, 'F' para Fahrenheit, 'K' para Kelvin.
        """
        
        # Regla empirica para determinar la temperatura del suelo según la temperatura exterior
        if self.temp_exterior_c > 30:
            temp_suelo = 18
        elif self.temp_exterior_c > 23:
            temp_suelo = 16
        elif self.temp_exterior_c > 16:
            temp_suelo = 14
        else:
            temp_suelo = 12
            
        # Temperaturas exteriores ajustadas para cada superficie considerando asoleamiento y contacto con el suelo
        temp_ext_superficies = {
            'piso': temp_suelo,
            'techo': self.temp_exterior_c + 5,
            'pared_norte': self.temp_exterior_c,
            'pared_este': self.temp_exterior_c + 3,
            'pared_sur': self.temp_exterior_c + 2,
            'pared_oeste': self.temp_exterior_c + 3
        }
        
        # Calculamos ΔT base en Celsius: (T_ext - T_camara)
        deltas_c = {panel: (t_ext - self.temp_camara_c) for panel, t_ext in temp_ext_superficies.items()}
        
        if unidad.upper() == 'C':
            return {panel: round(delta, 2) for panel, delta in deltas_c.items()}
        elif unidad.upper() == 'F':
            return {panel: round(delta * 1.8, 2) for panel, delta in deltas_c.items()}
        elif unidad.upper() == 'K':
            return {panel: round(delta, 2) for panel, delta in deltas_c.items()}
        else:
            raise ValueError("Unidad no soportada. Use 'C' para Celsius, 'F' para Fahrenheit o 'K' para Kelvin.")
        

    def obtener_k_factores(self, espesor_pared_mm: int, espesor_techo_mm: int, espesor_piso_mm: int, tiempo_control: float = 24.0) -> dict:
        """
        Retorna los Factores K de diseño ajustados por el tiempo de operacion del equipo.
        """
        
        for espesor in [espesor_pared_mm, espesor_techo_mm]:
            if espesor not in self.FACTORES_K_PARED_TECHO:
                raise ValueError(f"El espesor {espesor} mm no tiene un factor K definido en la tabla.")
            
        if espesor_piso_mm not in self.FACTORES_K_PISO:
            raise ValueError(f"El espesor {espesor_piso_mm} mm no tiene un factor K definido en la tabla.")
        
        # Calculamos el factor de ajuste
        ajuste_tiempo = tiempo_control / 24.0
                
        return{
            'techo': self.FACTORES_K_PARED_TECHO[espesor_techo_mm] * ajuste_tiempo,
            'piso': self.FACTORES_K_PISO[espesor_piso_mm] * ajuste_tiempo,
            'pared_norte': self.FACTORES_K_PARED_TECHO[espesor_pared_mm] * ajuste_tiempo,
            'pared_este': self.FACTORES_K_PARED_TECHO[espesor_pared_mm] * ajuste_tiempo,
            'pared_sur': self.FACTORES_K_PARED_TECHO[espesor_pared_mm] * ajuste_tiempo,
            'pared_oeste': self.FACTORES_K_PARED_TECHO[espesor_pared_mm] * ajuste_tiempo
        }
        
    
    def calcular_carga_total(self, espesor_pared_mm: int, espesor_techo_mm: int, espesor_piso_mm: int, tiempo_control: float = 24.0) -> dict:
        """
        Ejecuta el calculo maestro de la carga termica por transmision en BTU/dia
        """
        # Para la formula final exigimos ft2 y fahrenheit
        areas_ft2 = self.obtener_areas(unidad='ft2')
        deltas_f = self.obtener_deltas_temperatura(unidad='F')
        factores_k = self.obtener_k_factores(espesor_pared_mm, espesor_techo_mm, espesor_piso_mm, tiempo_control)
        
        cargas = {}
        total = 0.0
        
        for panel in areas_ft2.keys():
            carga_panel = areas_ft2[panel] * deltas_f[panel] * factores_k[panel]
            cargas[panel] = round(carga_panel)
            total += carga_panel
        
        cargas['TOTAL'] = round(total)        
        return cargas
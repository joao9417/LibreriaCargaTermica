class CalculadoraInfiltracion:
    """
    Módulo de cálculo de carga térmica por infiltración de aire.
    Calcula el calor sensible y latente aportado por el aire exterior considerando
    las renovaciones de aire por apertura de puertas.
    """
    
    # ---------------- CONSTANTES DE CLASE ---------------- #
    
    # Temperaturas Exteriores (Columnas en °C)
    TEMP_EXTERIOR_COLS = [37.78, 35.00, 32.22, 29.44]

    # Temperaturas de Cámara (Filas en °C)
    TEMP_CAMARA_ROWS = [
        18.33, 15.56, 12.78, 10.00, 7.22, 4.44, 1.67, -1.11, 
        -3.89, -6.67, -9.44, -12.22, -15.00, -17.78, -20.56, -23.33
    ]

    # Matriz de Factores de Infiltración (BTU/ft3)
    MATRIZ_FACTOR_AIRE = [
        [1.95, 1.54, 1.17, 0.85], [2.15, 1.74, 1.37, 1.03], [2.44, 2.01, 1.66, 1.34],
        [2.65, 2.22, 1.87, 1.54], [2.85, 2.42, 2.06, 1.73], [3.06, 2.62, 2.26, 1.92],
        [3.24, 2.79, 2.43, 2.09], [3.35, 2.94, 2.53, 2.24], [3.54, 3.16, 2.71, 2.42],
        [3.73, 3.35, 2.90, 2.61], [3.92, 3.54, 3.07, 2.74], [4.04, 3.66, 3.20, 2.87],
        [4.27, 3.87, 3.40, 3.07], [4.43, 4.03, 3.56, 3.23], [4.57, 4.18, 3.69, 3.36],
        [4.74, 4.33, 3.85, 3.49]
    ]

    # Tabla de Volúmenes (ft3) y sus correspondientes Cambios de Aire por día
    TABLA_VOLUMEN_FT3 = [
        200, 250, 300, 400, 500, 600, 700, 800, 900, 1000,
        1500, 2000, 3000, 4000, 5000, 6000, 15000, 20000,
        25000, 30000, 40000, 50000, 75000, 100000, 350000, 700000
    ]
    TABLA_CAMBIOS_AIRE = [
        44, 38, 34.5, 29.5, 26, 23, 21.5, 20, 18.75, 17.5,
        14, 12, 9.5, 8.2, 7.2, 6.5, 3.9, 3.5,
        3, 2.7, 2.3, 2, 1.6, 1.4, 1.13, 0.97
    ]

    # Factores de uso empíricos (Multiplicadores de velocidad de aire)
    OPCIONES_FACTOR_USO = {
        'normal': 1.0,
        'trabajo_pesado': 2.0,
        'almacenaje_prolongado': 0.6,
        'dos_puertas': 2.5
    }

    def __init__(self, largo_m: float, ancho_m: float, alto_m: float, temp_camara_c: float, temp_exterior_c: float):
        self.largo_m = largo_m
        self.ancho_m = ancho_m
        self.alto_m = alto_m
        self.temp_camara_c = temp_camara_c
        self.temp_exterior_c = temp_exterior_c
        self.M3_A_FT3 = 35.3147

    # ---------------- MÉTODOS PRIVADOS ---------------- #

    def _buscar_indice_temperatura(self, valor_buscado: float, array_descendente: list) -> int:
        """Emula COINCIDIR(valor, matriz, -1) para tablas descendentes."""
        for i, valor_tabla in enumerate(array_descendente):
            if valor_buscado > valor_tabla:
                return max(0, i - 1)
        return len(array_descendente) - 1

    def _buscar_indice_volumen(self, valor_buscado: float, array_ascendente: list) -> int:
        """
        Emula COINCIDIR(valor, matriz, 1) para la tabla ascendente de volúmenes.
        Retorna el índice del mayor valor que sea menor o igual al buscado.
        """
        for i, valor_tabla in enumerate(array_ascendente):
            if valor_buscado < valor_tabla:
                # Si nos pasamos, el correcto era el anterior
                return max(0, i - 1)
        # Si es mayor que todos, retorna el último
        return len(array_ascendente) - 1

    # ---------------- MÉTODOS PÚBLICOS ---------------- #

    def obtener_volumen_cuarto(self, unidad: str = 'ft3') -> float:
        volumen_m3 = self.largo_m * self.ancho_m * self.alto_m
        if unidad.lower() == 'm3':
            return round(volumen_m3, 2)
        elif unidad.lower() == 'ft3':
            return round(volumen_m3 * self.M3_A_FT3, 2)
        else:
            raise ValueError("Unidad no soportada. Use 'm3' o 'ft3'")

    def obtener_factor_infiltracion_base(self) -> float:
        idx_col = self._buscar_indice_temperatura(self.temp_exterior_c, self.TEMP_EXTERIOR_COLS)
        idx_fila_base = self._buscar_indice_temperatura(self.temp_camara_c, self.TEMP_CAMARA_ROWS)
        idx_fila = min(idx_fila_base + 1, len(self.TEMP_CAMARA_ROWS) - 1)
        return self.MATRIZ_FACTOR_AIRE[idx_fila][idx_col]

    def obtener_renovaciones_diarias(self, tipo_uso: str = 'normal') -> float:
        """
        Calcula las renovaciones de aire cruzando el volumen en la tabla y
        aplicando el factor de uso (velocidad de aire).
        """
        if tipo_uso not in self.OPCIONES_FACTOR_USO:
            raise ValueError(f"Tipo de uso inválido. Opciones: {list(self.OPCIONES_FACTOR_USO.keys())}")
            
        volumen_ft3 = self.obtener_volumen_cuarto(unidad='ft3')
        
        # Buscar en la tabla ascendente
        idx_vol = self._buscar_indice_volumen(volumen_ft3, self.TABLA_VOLUMEN_FT3)
        renovaciones_base = self.TABLA_CAMBIOS_AIRE[idx_vol]
        
        # Aplicar el factor de uso de las puertas
        multiplicador = self.OPCIONES_FACTOR_USO[tipo_uso]
        
        return renovaciones_base * multiplicador

    def calcular_carga_infiltracion(self, tiempo_control: float = 24.0, tipo_uso: str = 'normal') -> dict:
        """
        Calcula la carga térmica total por infiltración en BTU/día.
        """
        volumen_ft3 = self.obtener_volumen_cuarto(unidad='ft3')
        factor_base = self.obtener_factor_infiltracion_base()
        renovaciones = self.obtener_renovaciones_diarias(tipo_uso)
        
        # Ajuste por tiempo de operación
        factor_ajustado = factor_base * (tiempo_control / 24.0)
        
        # Fórmula final
        carga_total_btu = volumen_ft3 * factor_ajustado * renovaciones
        
        return {
            'volumen_ft3': volumen_ft3,
            'factor_base_btu_ft3': factor_base,
            'factor_ajustado': factor_ajustado,
            'renovaciones_ajustadas': renovaciones,
            'TOTAL_INFILTRACION': round(carga_total_btu)
        }
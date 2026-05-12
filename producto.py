class CalculadoraProducto:
    """
    Modulo 3: Calculo de carga termica del producto.
    Calcula el calor sensible (enfriamiento y subenfriamiento), calor latente 
    (congelacion) y calor de respiración.
    """
    
    def __init__(self, nombre: str, rotacion_kg: float, temp_entrada_c: float, 
                 temp_salida_c: float, temp_congelacion_c: float = None, 
                 cp_arriba_cong: float = 0.0, cp_debajo_cong: float = 0.0, 
                 calor_latente: float = 0.0, almacenamiento: float = 0.0, 
                 calor_respiracion: float = 0.0, factor_carga: float = 1.0):
        
        # 1. Identificación y Operación
        self.nombre = nombre
        self.rotacion_kg = rotacion_kg
        self.almacenamiento = almacenamiento
        self.factor_carga = factor_carga
        
        # 2. Temperaturas (°C)
        self.temp_entrada_c = temp_entrada_c
        self.temp_salida_c = temp_salida_c
        self.temp_congelacion_c = temp_congelacion_c
        
        # 3. Propiedades Térmicas
        self.cp_arriba_cong = cp_arriba_cong
        self.cp_debajo_cong = cp_debajo_cong
        self.calor_latente = calor_latente
        self.calor_respiracion = calor_respiracion
        
        # Factores de conversión
        self.KG_A_LBS = 2.20462

    # ---------------- MÉTODOS PRIVADOS ---------------- #

    def _c_to_f(self, temp_c: float) -> float:
        """Convierte grados Celsius a Fahrenheit."""
        return (9/5 * temp_c) + 32

    # ---------------- MÉTODOS PÚBLICOS ---------------- #

    def obtener_masa_diaria_lbs(self) -> float:
        """Calcula la masa total del producto que ingresa al día en libras."""
        return self.rotacion_kg * self.KG_A_LBS * self.factor_carga

    def obtener_deltas_temperatura(self) -> dict:
        """
        Calcula los diferenciales de temperatura (ΔT en °F) para las tres fases 
        termodinámicas del producto.
        """
        t_in_f = self._c_to_f(self.temp_entrada_c)
        t_out_f = self._c_to_f(self.temp_salida_c)
        
        # Manejo del caso sin punto de congelación definido (asume 32°F / 0°C)
        if self.temp_congelacion_c is None:
            t_cong_f = 32.0
        else:
            t_cong_f = self._c_to_f(self.temp_congelacion_c)
            
        delta_refrig = 0.0
        flag_congelacion = 0.0
        delta_subenfriamiento = 0.0
        
        # Solo hay enfriamiento si la temperatura de entrada es mayor a la de salida
        if t_in_f > t_out_f:
            
            # 1. ETAPA DE REFRIGERACIÓN (Sensible arriba del punto de congelación)
            if t_in_f > t_cong_f and t_out_f > t_cong_f:
                delta_refrig = t_in_f - t_out_f
            elif t_in_f > t_cong_f:
                delta_refrig = t_in_f - t_cong_f
                
            # 2. ETAPA DE CONGELACIÓN (Latente: cambio de fase)
            # El flag indica que el producto cruzó la barrera de congelación
            if t_in_f > t_cong_f and t_out_f < t_cong_f:
                flag_congelacion = 1.0
                
            # 3. ETAPA DE SUBENFRIAMIENTO (Sensible debajo del punto de congelación)
            if t_in_f < t_cong_f and t_out_f < t_cong_f:
                delta_subenfriamiento = abs(t_in_f - t_out_f)
            elif t_out_f < t_cong_f:
                delta_subenfriamiento = abs(t_out_f - t_cong_f)
                
        return {
            'refrigeracion_f': round(delta_refrig, 2),
            'congelacion_flag': round(flag_congelacion, 2),
            'subenfriamiento_f': round(delta_subenfriamiento, 2)
        }

    def calcular_carga_producto(self) -> dict:
        """
        Calcula la carga térmica total del producto en BTU/día aplicando 
        las fórmulas termodinámicas para cada etapa.
        """
        masa_lbs = self.obtener_masa_diaria_lbs()
        deltas = self.obtener_deltas_temperatura()
        
        # Q = m * Cp * ΔT
        btu_refrigeracion = masa_lbs * self.cp_arriba_cong * deltas['refrigeracion_f']
        
        # Q = m * Calor_Latente * Flag
        btu_congelacion = masa_lbs * self.calor_latente * deltas['congelacion_flag']
        
        # Q = m * Cp * ΔT
        btu_subenfriamiento = masa_lbs * self.cp_debajo_cong * deltas['subenfriamiento_f']
        
        # Calor de respiración/evolución (Si aplica)
        # Generalmente es: Almacenamiento * Factor de Respiración
        btu_respiracion = self.almacenamiento * self.calor_respiracion
        
        total_btu_dia = btu_refrigeracion + btu_congelacion + btu_subenfriamiento + btu_respiracion
        
        return {
            'producto': self.nombre,
            'masa_lbs': round(masa_lbs, 2),
            'btu_refrigeracion': round(btu_refrigeracion, 2),
            'btu_congelacion': round(btu_congelacion, 2),
            'btu_subenfriamiento': round(btu_subenfriamiento, 2),
            'btu_respiracion': round(btu_respiracion, 2),
            'TOTAL_PRODUCTO': round(total_btu_dia)
        }

# --- PRUEBA Y DEPURACIÓN DEL CÓDIGO ---
if __name__ == "__main__":
    # Instanciamos la "Papa" con los datos exactos de tu Excel
    papa = CalculadoraProducto(
        nombre="Papa", 
        rotacion_kg=18144, 
        temp_entrada_c=-13.0, 
        temp_salida_c=-18.0, 
        temp_congelacion_c=-0.6,
        cp_arriba_cong=0.88,
        cp_debajo_cong=0.5,
        calor_latente=113.0,
        factor_carga=1.0
    )
    
    resultados = papa.calcular_carga_producto()
    
    print(f"--- 3. CARGA TÉRMICA DEBIDA AL PRODUCTO ({resultados['producto'].upper()}) ---")
    print(f"Masa procesada:          {resultados['masa_lbs']:,.2f} lbs")
    print(f"Calor Refrigeración:     {resultados['btu_refrigeracion']:,.2f} BTU/Día")
    print(f"Calor Congelación:       {resultados['btu_congelacion']:,.2f} BTU/Día")
    print(f"Calor Subenfriamiento:   {resultados['btu_subenfriamiento']:,.2f} BTU/Día")
    print("-" * 55)
    print(f"TOTAL ITEM III =         {resultados['TOTAL_PRODUCTO']:,} BTU/DIA".replace(',', '.'))
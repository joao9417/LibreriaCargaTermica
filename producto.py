from catalogo import CatalogoProductosDB

class CalculadoraProducto:
    """
    Modulo 3: Calculo de carga termica del producto.
    """
    
    def __init__(self, 
                # Datos operativos de entrada:
                nombre: str,
                rotacion_kg: float,
                temp_entrada_c: float,
                temp_salida_c: float,
                almacenamiento_ton: float = 0.0,
                factor_carga: float = 1.0,
                aplica_respiracion: bool = False,

                # Datos de catalogo Base de datos SQLite:
                temp_congelacion_f: float = None,
                cp_arriba_cong: float = 0.0,
                cp_debajo_cong: float = 0.0,
                calor_latente: float = 0.0,
                # Calor de respiracion 
                resp_0: float = None,
                resp_5: float = None,
                resp_10: float = None,
                resp_15: float = None,
                resp_20: float = None):
        
        # Guardamos en memoria del objeto los datos
        self.nombre = nombre
        self.rotacion_kg = rotacion_kg
        self.almacenamiento_ton = almacenamiento_ton
        self.factor_carga = factor_carga
        self.aplica_respiracion = aplica_respiracion
        
        self.temp_entrada_c = temp_entrada_c
        self.temp_salida_c = temp_salida_c

        self.temp_congelacion_f = temp_congelacion_f
        self.cp_arriba_cong = cp_arriba_cong
        self.cp_debajo_cong = cp_debajo_cong
        self.calor_latente = calor_latente

        self.respiracion = {
            0: resp_0 or 0.0,
            5: resp_5 or 0.0,
            10: resp_10 or 0.0,
            15: resp_15 or 0.0,
            20: resp_20 or 0.0
        }
        
        # Factores de conversión
        self.KG_A_LBS = 2.20462

    # ---------------- MÉTODOS PRIVADOS ---------------- #

    def _c_to_f(self, temp_c: float) -> float:
        """Convierte grados Celsius a Fahrenheit."""
        return (9/5 * temp_c) + 32
    
    def _obtener_tasa_respiracion(self) -> float:
        """
        Busca la tasa de respiracion basada en la temperatura de la camara.
        """
        if not self.temp_salida_c:
            return 0.0
        
        t_camara = self.temp_salida_c

        # Logica interpolacion
        if t_camara <=0:
            return self.respiracion[0]
        elif t_camara <=5:
            return self.respiracion[5]
        elif t_camara <=10:
            return self.respiracion[10]
        elif t_camara <=15:
            return self.respiracion[15]
        else:
            return self.respiracion[20]

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

        t_cong_f = 32.0 if self.temp_congelacion_f is None else self.temp_congelacion_f        
            
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
        tasa_resp = self._obtener_tasa_respiracion()
        btu_respiracion = self.almacenamiento_ton * tasa_resp
        
        total_btu_dia = btu_refrigeracion + btu_congelacion + btu_subenfriamiento + btu_respiracion
        
        return {
            'producto': self.nombre,
            'masa_lbs': round(masa_lbs, 2),
            'btu_refrigeracion': round(btu_refrigeracion, 2),
            'btu_congelacion': round(btu_congelacion, 2),
            'btu_subenfriamiento': round(btu_subenfriamiento, 2),
            'tasa_respiracion_usada': tasa_resp,
            'btu_respiracion': round(btu_respiracion, 2),
            'TOTAL_PRODUCTO': round(total_btu_dia)
        }

# --- PRUEBA Y DEPURACIÓN DEL CÓDIGO ---
if __name__ == "__main__":
    db = CatalogoProductosDB()
    nombre_producto = "Pepino"
    
    try:
        datos_bd = db.buscar_producto(nombre_producto)

        papa_calc = CalculadoraProducto(
            nombre=datos_bd['nombre'],
            rotacion_kg=18144, 
            temp_entrada_c=-13.0, 
            temp_salida_c=-18.0,
            almacenamiento_ton=2.4,
            factor_carga=1.0,
            aplica_respiracion=True,

            # Inyeccion desde SQLite
            temp_congelacion_f=datos_bd['temp_congelacion_f'],
            cp_arriba_cong=datos_bd['cp_arriba'],
            cp_debajo_cong=datos_bd['cp_debajo'],
            calor_latente=datos_bd['calor_latente'],
            resp_0=datos_bd['resp_0'],
            resp_5=datos_bd['resp_5'],
            resp_10=datos_bd['resp_10'],
            resp_15=datos_bd['resp_15'],
            resp_20=datos_bd['resp_20'], 
          
        )

        resultados = papa_calc.calcular_carga_producto()

        print(f"\n--- 3. CARGA TÉRMICA DEBIDA AL PRODUCTO ({resultados['producto'].upper()}) ---")
        print(f"Masa procesada:          {resultados['masa_lbs']:,.2f} lbs")
        print(f"Calor Refrigeración:     {resultados['btu_refrigeracion']:,.2f} BTU/Día")
        print(f"Calor Congelación:       {resultados['btu_congelacion']:,.2f} BTU/Día")
        print(f"Calor Subenfriamiento:   {resultados['btu_subenfriamiento']:,.2f} BTU/Día")
        print(f"Calor Evolución (Resp):  {resultados['btu_respiracion']:,.2f} BTU/Día (Tasa: {resultados['tasa_respiracion_usada']})")
        print("-" * 55)
        print(f"TOTAL ITEM III =         {resultados['TOTAL_PRODUCTO']:,} BTU/DIA".replace(',', '.'))
        
    except ValueError as e:
        print(f"Error: {e}")
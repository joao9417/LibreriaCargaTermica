import infiltracion
from transmision import CalculadoraTransmisionTermica
from infiltracion import CalculadoraInfiltracionTermica
from producto import CalculadoraProducto
from catalogo import CatalogoProductosDB
from suplementarias import (
    CalculadoraCargaPersonas, 
    CalculadoraIluminacion, 
    CalculadoraEnvases, 
    CalculadoraCargasInternas
)

# ==================================================
# 1. PARÁMETROS MAESTROS (INPUTS DEL USUARIO)
# ==================================================
# Dimensiones y Temperaturas
L, A, H = 10.0, 5.0, 5.0
T_camara = 1
T_exterior = 30
Tiempo_OP = 18.0  # Tiempo de operación del equipo

# Datos para Puertas (Infiltración)
alto_puerta, ancho_puerta = 2.5, 2.5
tiempo_abierta_min = 30.0  # Tiempo total de apertura al día en minutos
n_puertas = 0

# Datos para Transmisión
esp_pared, esp_techo, esp_piso = 80, 80, 0

# Datos para Infiltración
tipo_uso_infil = 'dos_puertas'

# Datos para Producto (Desde BD)
nombre_producto = "Res, higado"
rotacion_kg = 35000
T_entrada_prod = 39
T_salida_prod = 5
factor_carga_prod = 1.0
almacen_ton = 2.0
respiracion_activa = False

# Datos para Envases / Canastas
tamano_canasta = 25  # Puede ser 13, 25 o 0 si no aplica

# Datos para Suplementarias (Personas y Luces)
n_personas = 1
horas_personas = 12.0
luxes_requeridos = 570
horas_luces = 15.0
w_por_lampara = 50.0
eficiencia_lampara_lm_w = 140.0

# Datos para Cargas Internas (Motores y Equipos Adicionales)
tipo_evaporador = 'industrial_pesado'
tipo_deshielo = 'gas_caliente'
cambios_aire_hora = 216.0  # Renovaciones requeridas para el producto
hp_adicionales_cuarto = 10.0 # Ej: montacargas operando dentro
cantidad_cargas_hp = 0
horas_operacion_hp = 12.0
watts_adicionales_cuarto = 5000.0
cantidad_cargas_watts = 0
horas_operacion_watts = 0

print("="*70)
print(f"SIMULACIÓN INTEGRAL DE CARGA TÉRMICA: CUARTO DE {nombre_producto.upper()}")
print("="*70)

# ==================================================
# 2. EJECUCIÓN DE MÓDULOS (CASCADA)
# ==================================================

# --- MODULO 1: TRANSMISIÓN ---
calc_trans = CalculadoraTransmisionTermica(L, A, H, T_camara, T_exterior)
res_trans = calc_trans.calcular_carga_total(esp_pared, esp_techo, esp_piso, Tiempo_OP)
total_trans = res_trans['TOTAL']

# --- MODULO 2: INFILTRACIÓN ---
calc_infil = CalculadoraInfiltracionTermica(L, A, H, T_camara, T_exterior)
# Usaremos el método por Volumen para el balance térmico principal en este ejemplo
res_infil_vol = calc_infil.calcular_carga_por_volumen(Tiempo_OP, tipo_uso_infil)
total_infil = res_infil_vol['TOTAL_INFILTRACION']

# Calculo por Puertas (Solo como información para reporte)
res_infil_puertas = calc_infil.calcular_carga_por_puertas(
    alto_puerta_m=alto_puerta, 
    ancho_puerta_m=ancho_puerta, 
    tiempo_abierta_min=tiempo_abierta_min, 
    cant_puertas=n_puertas, 
    tiempo_control=Tiempo_OP
)
total_infil_puertas = res_infil_puertas['TOTAL_INFILTRACION']

# --- MODULO 3: PRODUCTO (Conexión SQLite) ---
db = CatalogoProductosDB()
datos_p = db.buscar_producto(nombre_producto)
calc_prod = CalculadoraProducto(
    nombre=datos_p['nombre'], rotacion_kg=rotacion_kg, 
    temp_entrada_c=T_entrada_prod, temp_salida_c=T_salida_prod,
    almacenamiento_ton=almacen_ton, factor_carga=factor_carga_prod,
    aplica_respiracion=respiracion_activa,
    temp_congelacion_f=datos_p['temp_congelacion_f'],
    cp_arriba_cong=datos_p['cp_arriba'],
    cp_debajo_cong=datos_p['cp_debajo'],
    calor_latente=datos_p['calor_latente'],
    resp_0=datos_p['resp_0'], resp_5=datos_p['resp_5'],
    resp_10=datos_p['resp_10'], resp_15=datos_p['resp_15'], resp_20=datos_p['resp_20']
)
res_prod = calc_prod.calcular_carga_producto()
total_prod = res_prod['TOTAL_PRODUCTO']

# --- MODULO 4: SUPLEMENTARIAS Y CARGAS INTERNAS ---
# 4a. Personas
calc_pers = CalculadoraCargaPersonas(T_camara, n_personas, horas_personas)
res_pers = calc_pers.calcular_carga()

# 4b. Iluminación 
calc_luces = CalculadoraIluminacion(L, A, H, luxes_requeridos, horas_luces, w_por_lampara, eficiencia_lampara_lm_w)
res_luces = calc_luces.calcular_carga()

# 4c. Envases
calc_envases = CalculadoraEnvases(rotacion_kg, T_entrada_prod, T_salida_prod, tamano_canasta)
res_envases = calc_envases.calcular_carga()

# Sumatoria Suplementarias Base
total_suple_base = res_pers['TOTAL_SUPLEMENTARIA'] + res_luces['TOTAL_SUPLEMENTARIA'] + res_envases['TOTAL_SUPLEMENTARIA']

# --- EL MOMENTO DE LA VERDAD: SUBTOTAL PREVIO ---
# Sumamos todo lo que genera calor ANTES de calcular los motores
subtotal_parcial_dia = total_trans + total_infil + total_prod + total_suple_base

# 4d. Cargas Internas (Motores Evaporador y Deshielo)
volumen_cuarto = L * A * H
calc_internas = CalculadoraCargasInternas(
    temp_camara_c=T_camara, 
    volumen_m3=volumen_cuarto, 
    cambios_aire_hora=cambios_aire_hora, 
    horas_operacion_equipo=Tiempo_OP,
    hp_adicionales=hp_adicionales_cuarto,
    watts_adicionales=watts_adicionales_cuarto,
    cantidad_cargas_hp=cantidad_cargas_hp,
    horas_operacion_hp=horas_operacion_hp,
    cantidad_cargas_watts=cantidad_cargas_watts,
    horas_operacion_watts=horas_operacion_watts,
    tipo_evaporador=tipo_evaporador,
    tipo_deshielo=tipo_deshielo
)
res_internas = calc_internas.calcular_carga(subtotal_carga_previa_dia=subtotal_parcial_dia)

# ==================================================
# 3. REPORTE FINAL Y BALANCE TÉRMICO
# ==================================================
# El Gran Total es el subtotal de las cargas + el calor de los equipos
total_general_dia = subtotal_parcial_dia + res_internas['TOTAL_SUPLEMENTARIA']
total_btu_h = total_general_dia / Tiempo_OP

print(f"\n1. TRANSMISIÓN:        {total_trans:15,.0f} BTU/Día")
print(f"2. INFILTRACIÓN:       {total_infil:15,.0f} BTU/Día (Método: Volumen)")
print(f"                       {total_infil_puertas:15,.0f} BTU/Día (Método: Puertas)")
print(f"3. PRODUCTO:           {total_prod:15,.0f} BTU/Día")
print(f"4. SUPLEMENTARIAS:     ")
print(f"   - Personas:         {res_pers['TOTAL_SUPLEMENTARIA']:15,.0f} BTU/Día")
print(f"   - Iluminación:      {res_luces['TOTAL_SUPLEMENTARIA']:15,.0f} BTU/Día")
print(f"     * Lámparas a inst.: {res_luces['lamparas_sugeridas']} ud(s) de {w_por_lampara}W")
print(f"   - Envases Plásticos:{res_envases['TOTAL_SUPLEMENTARIA']:15,.0f} BTU/Día")
print(f"     * Cant. ingresada:  {res_envases['unidades_estimadas']} canastas de {tamano_canasta}cm")
print(f"5. CARGAS INTERNAS:    ")
print(f"   - Motores Evap.:    {res_internas['btu_dia_ventiladores']:15,.0f} BTU/Día ({res_internas['potencia_estimada_ventiladores_W']} W eléctricos inst.)")
print(f"   - Deshielo:         {res_internas['btu_dia_deshielo']:15,.0f} BTU/Día ({res_internas['potencia_estimada_resistencias_W']} W eléctricos inst.)")
print(f"   - Eq. Adic. (HP):   {res_internas['btu_dia_hp_extra']:15,.0f} BTU/Día ({cantidad_cargas_hp} equipo(s) de {hp_adicionales_cuarto} HP, {horas_operacion_hp} h/día)")
print(f"   - Eq. Adic. (W):    {res_internas['btu_dia_watts_extra']:15,.0f} BTU/Día ({cantidad_cargas_watts} equipo(s) de {watts_adicionales_cuarto} W, {horas_operacion_watts} h/día)")
print("-" * 70)
print(f"CARGA TOTAL DIARIA:    {total_general_dia:15,.0f} BTU/Día")
print(f"CARGA TÉRMICA (Q):     {total_btu_h:15,.0f} BTU/h")
print(f"CAPACIDAD CON FACTOR 10%:  {((total_btu_h)*1.10):15,.0f} BTU/h")
print(f"CAPACIDAD SUGERIDA:    {total_btu_h / 12000:15.2f} Ton. Ref.")
print("="*70)
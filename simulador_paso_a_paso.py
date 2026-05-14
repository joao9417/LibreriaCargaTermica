from transmision import CalculadoraTransmisionTermica
from infiltracion import CalculadoraInfiltracionTermica
from producto import CalculadoraProducto
from catalogo import CatalogoProductosDB
from suplementarias import CalculadoraCargaPersonas, CalculadoraIluminacion

# ==================================================
# 1. PARÁMETROS MAESTROS (INPUTS DEL USUARIO)
# ==================================================
# Dimensiones y Temperaturas
L, A, H = 17.87, 19.57, 3.5
T_camara = -20.0
T_exterior = 30.0
Tiempo_OP = 16.0  # Tiempo de operación del equipo

# Datos para Puertas (Infiltración)
alto_puerta, ancho_puerta = 5.0, 5.0
tiempo_abierta_min = 20.0  # Tiempo total de apertura al día en minutos
n_puertas = 2

# Datos para Transmisión
esp_pared, esp_techo, esp_piso = 100, 100, 80

# Datos para Infiltración
tipo_uso_infil = 'trabajo_pesado'

# Datos para Producto (Desde BD)
nombre_producto = "Papa"
rotacion_kg = 18144
T_entrada_prod = -13.0
T_salida_prod = -18.0
factor_carga_prod = 1.1
almacen_ton = 2.4
respiracion_activa = True

# Datos para Suplementarias
n_personas = 2
horas_personas = 16.0
luxes_requeridos = 250
horas_luces = 24.0
w_por_lampara = 50.0

print("="*60)
print(f"SIMULACIÓN INTEGRAL DE CARGA TÉRMICA: CUARTO DE {nombre_producto.upper()}")
print("="*60)

# ==================================================
# 2. EJECUCIÓN DE MÓDULOS (CASCADA)
# ==================================================

# --- MODULO 1: TRANSMISIÓN ---
calc_trans = CalculadoraTransmisionTermica(L, A, H, T_camara, T_exterior)
res_trans = calc_trans.calcular_carga_total(esp_pared, esp_techo, esp_piso, Tiempo_OP)
total_trans = res_trans['TOTAL']

# --- MODULO 2: INFILTRACIÓN ---
calc_infil = CalculadoraInfiltracionTermica(L, A, H, T_camara, T_exterior)
# Cálculo 1: Por Volumen
res_infil_vol = calc_infil.calcular_carga_por_volumen(Tiempo_OP, tipo_uso_infil)
# Cálculo 2: Por Puertas
res_infil_puertas = calc_infil.calcular_carga_por_puertas(alto_puerta, ancho_puerta, tiempo_abierta_min, n_puertas, Tiempo_OP)

print("DICCIONARIO INFILTRACION (VOL):", res_infil_vol)
print("DICCIONARIO INFILTRACION (PUERTAS):", res_infil_puertas)

# Elegimos el mayor o el que el usuario prefiera (usaremos volumen para el total general por ahora)
total_infil = res_infil_vol['TOTAL_INFILTRACION']
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

# --- MODULO 4: SUPLEMENTARIAS ---
# Personas
calc_pers = CalculadoraCargaPersonas(T_camara, n_personas, horas_personas)
res_pers = calc_pers.calcular_carga()
# Iluminación (Usa L, A y H de los parámetros maestros)
calc_luces = CalculadoraIluminacion(L, A, H, luxes_requeridos, horas_luces, w_por_lampara)
res_luces = calc_luces.calcular_carga()

total_suple = res_pers['TOTAL_SUPLEMENTARIA'] + res_luces['TOTAL_SUPLEMENTARIA']

# ==================================================
# 3. REPORTE FINAL Y BALANCE TÉRMICO
# ==================================================
total_general_vol = total_trans + total_infil + total_prod + total_suple
total_general_pue = total_trans + total_infil_puertas + total_prod + total_suple

total_btu_h_vol = total_general_vol / Tiempo_OP
total_btu_h_pue = total_general_pue / Tiempo_OP

total_suple_pers = res_pers['TOTAL_SUPLEMENTARIA']
total_suple_luces = res_luces['TOTAL_SUPLEMENTARIA']

print(f"\n1. TRANSMISIÓN:        {total_trans:15,.0f} BTU/Día")
print(f"2. INFILTRACIÓN (VOL): {total_infil:15,.0f} BTU/Día")
print(f"   INFILTRACIÓN (PUE): {total_infil_puertas:15,.0f} BTU/Día")
print(f"3. PRODUCTO:           {total_prod:15,.0f} BTU/Día")
print(f"4. SUPLEMENTARIAS:     {total_suple:15,.0f} BTU/Día")
print(f"   - Personas:         {total_suple_pers:15,.0f} BTU/Día")
print(f"   - Iluminación:      {total_suple_luces:15,.0f} BTU/Día")
print(f"     * Lámparas a instalar: {res_luces['lamparas_sugeridas']} ud(s) de {w_por_lampara}W")
print(f"     * Watts totales int.:  {res_luces['watts_reales']} W")
print("-" * 50)
print(f"RESUMEN USANDO INFILTRACIÓN POR VOLUMEN:")
print(f"CARGA TOTAL DIARIA:    {total_general_vol:15,.0f} BTU/Día")
print(f"CARGA TÉRMICA (Q):     {total_btu_h_vol:15,.0f} BTU/h")
print(f"CAPACIDAD SUGERIDA:    {total_btu_h_vol / 12000:15.2f} Ton. Ref.")
print("-" * 50)
print(f"RESUMEN USANDO INFILTRACIÓN POR PUERTAS:")
print(f"CARGA TOTAL DIARIA:    {total_general_pue:15,.0f} BTU/Día")
print(f"CARGA TÉRMICA (Q):     {total_btu_h_pue:15,.0f} BTU/h")
print(f"CAPACIDAD SUGERIDA:    {total_btu_h_pue / 12000:15.2f} Ton. Ref.")
print("="*60)
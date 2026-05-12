from transmision import CalculadoraTransmisionTermica
from infiltracion import CalculadoraInfiltracionTermica

# Parametros Modulo 1: Transmision Termica
L, A, H = 4.0, 3.0, 2.5
T_camara = -20.0
T_exterior = 30.0
Tiempo_OP = 16.0
esp_pared_mm= 100
esp_techo_mm= 100
esp_piso_mm= 80


# Parametros Modulo 2: Infiltracion Termica
tipo_uso_infiltracion = 'trabajo_pesado'
tipo_metodo_infiltracion = 'volumen'

tiempo_abierto_min = 20
alto_puerta_m = 5
ancho_puerta_m = 5
cant_puertas = 2


# Prueba Modulo 1: Calculo de carga termica por transmision

calc_trans = CalculadoraTransmisionTermica(
    largo_m=L,
    ancho_m=A,
    alto_m=H,
    temp_camara_c=T_camara,
    temp_exterior_c=T_exterior
)

resultados_trans = calc_trans.calcular_carga_total(
    espesor_pared_mm=esp_pared_mm,
    espesor_techo_mm=esp_techo_mm,
    espesor_piso_mm=esp_piso_mm,
    tiempo_control=Tiempo_OP
)

for superficie, carga in resultados_trans.items():
    print(f"{superficie.capitalize()}: {carga} BTU/dia")


# Prueba Modulo 2: Calculo de carga termica por infiltracion
print("\n" + "="*50)
print("PRUEBA MODULO 2: CARGA TERMICA POR INFILTRACION")
print("="*50)

calc_infil = CalculadoraInfiltracionTermica(
    largo_m=L,
    ancho_m=A,
    alto_m=H,
    temp_camara_c=T_camara,
    temp_exterior_c=T_exterior
)

# 1. Extraccion de factores y valores internos
volumen_m3 = calc_infil.obtener_volumen_cuarto('m3')
volumen_ft3 = calc_infil.obtener_volumen_cuarto('ft3')
factor_base = calc_infil.obtener_factor_infiltracion_base()
renovaciones = calc_infil.obtener_renovaciones_diarias(tipo_uso=tipo_uso_infiltracion)

print("\n--- 1. FACTORES Y VALORES INTERNOS ---")
print(f"Volumen de la camara (m3): {volumen_m3}")
print(f"Volumen de la camara (ft3): {volumen_ft3}")
print(f"Factor de Infiltracion Base (segun Temp ext {T_exterior} C y Temp int {T_camara} C): {factor_base}")
print(f"Renovaciones de Aire Diarias (Uso '{tipo_uso_infiltracion}'): {renovaciones}")


# 2. Calculo de carga por metodo de VOLUMEN
print("\n--- 2. METODO POR RENOVACIONES VOLUMETRICAS ---")
resultados_volumen = calc_infil.calcular_carga_por_volumen(
    tiempo_control=Tiempo_OP,
    tipo_uso=tipo_uso_infiltracion
)

for clave, valor in resultados_volumen.items():
    print(f"{clave.capitalize()}: {valor}")


# 3. Calculo de carga por metodo de PUERTAS (Apertura directa)
print("\n--- 3. METODO POR APERTURA DE PUERTAS ---")

resultados_puertas = calc_infil.calcular_carga_por_puertas(
    alto_puerta_m=alto_puerta_m,
    ancho_puerta_m=ancho_puerta_m,
    tiempo_abierta_min=tiempo_abierto_min,
    cant_puertas=cant_puertas,
    tiempo_control=Tiempo_OP
)

for clave, valor in resultados_puertas.items():
    print(f"{clave.capitalize()}: {valor}")

print("\n" + "="*50)

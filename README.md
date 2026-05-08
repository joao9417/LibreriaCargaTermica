# LibreriaCargaTermica ❄️🌡️

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/Status-En_Desarrollo-orange.svg)
![Dominio](https://img.shields.io/badge/Dominio-Refrigeraci%C3%B3n_Industrial-00599C.svg)

Librería de Python orientada al cálculo automatizado y preciso de la carga térmica en cuartos fríos industriales y comerciales. 

Este motor de cálculo está diseñado basándose en prácticas empíricas validadas por la industria de la refrigeración y estrictos lineamientos termodinámicos. Su arquitectura limpia y desacoplada la hace ideal para integrarse como lógica de negocio en aplicaciones web (Django, Flask), APIs REST o herramientas de escritorio.

## Características Actuales (v0.2)

### 🧱 Módulo 1: Transmisión (Paredes, Techo, Piso)
* Cálculo automatizado de áreas considerando factores de seguridad estructural (+0.2m).
* Ajuste empírico de la Temperatura Sol-Aire para techos y paredes expuestas.
* Regla de negocio automatizada para estimar la temperatura del subsuelo según el clima local.
* Cálculo de Factores K (Transmitancia) ajustados dinámicamente por el tiempo de operación del compresor.

### 💨 Módulo 2: Infiltración de Aire
* Cálculo de carga térmica sensible y latente aportada por la entrada de aire exterior.
* Matriz tabulada y automatizada para buscar factores de aire (BTU/ft³) cruzando temperaturas internas y externas.
* Cálculo dinámico de renovaciones de aire diarias según el volumen volumétrico del cuarto.
* Soporte para factores de uso empíricos de puertas (`normal`, `trabajo_pesado`, `almacenaje_prolongado`, `dos_puertas`).

### 📦 Módulo 3: Producto
* Cálculo de calor sensible (enfriamiento y subenfriamiento) y calor latente (congelación).
* Determinación automática de etapas termodinámicas según las temperaturas de entrada, salida y punto de congelación.
* Soporte para calor de respiración en productos que lo requieran (frutas, verduras).

## Instalación

Al ser una librería de dominio independiente que utiliza únicamente librerías estándar de Python, no requiere instalación forzosa mediante `pip`. Simplemente clona este repositorio o copia la carpeta `LibreriaCargaTermica` dentro de la estructura principal de tu proyecto. 

*Nota: Se incluye un archivo `requirements.txt` y se puede crear un entorno virtual para mantener las buenas prácticas, aunque actualmente no existen dependencias de terceros.*

## Ejemplos de Uso

### 1. Cálculo por Transmisión Térmica
```python
from LibreriaCargaTermica.transmision import CalculadoraTransmisionTermica

# Instanciar con dimensiones (L, A, H en metros) y temperaturas (°C)
calc_transmision = CalculadoraTransmisionTermica(10.0, 8.0, 3.5, -20.0, 35.0)

# Calcular pasando los espesores de los paneles (mm) y horas de control
resultados_trans = calc_transmision.calcular_carga_total(
    espesor_pared_mm=125, 
    espesor_techo_mm=125, 
    espesor_piso_mm=150, 
    tiempo_control=16.0
)

print(f"Carga por Transmisión: {resultados_trans['TOTAL']} BTU/día")
```

### 2. Cálculo por Infiltración de Aire
```python
from LibreriaCargaTermica.infiltracion import CalculadoraInfiltracion

# Instanciar con dimensiones (L, A, H en metros) y temperaturas (°C)
calc_infiltracion = CalculadoraInfiltracion(10.0, 8.0, 3.5, -20.0, 35.0)

# Calcular por método de volumen (renovaciones de aire)
resultados_inf = calc_infiltracion.calcular_carga_por_volumen(
    tiempo_control=16.0,
    tipo_uso='normal'
)

print(f"Carga por Infiltración (Volumen): {resultados_inf['TOTAL_INFILTRACION']} BTU/día")
```

### 3. Cálculo de Carga del Producto
```python
from LibreriaCargaTermica.producto import CalculadoraProducto

# Instanciar con las propiedades térmicas y operativas del producto
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

resultados_prod = papa.calcular_carga_producto()

print(f"Carga del Producto ({resultados_prod['producto']}): {resultados_prod['TOTAL_PRODUCTO']} BTU/día")
```
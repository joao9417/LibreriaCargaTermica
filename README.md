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

### 🗄️ Módulo 4: Catálogo y Base de Datos (Nuevo)
* Gestión automatizada de propiedades termodinámicas mediante SQLite.
* Carga masiva de productos desde archivos CSV (`productos.csv`).
* Métodos de búsqueda optimizados para integrar con el motor de cálculo.
* Arquitectura preparada para migración directa a frameworks como Django.

## Instalación

Al ser una librería de dominio independiente que utiliza únicamente librerías estándar de Python, no requiere instalación forzosa mediante `pip`. Simplemente clona este repositorio o copia la carpeta `LibreriaCargaTermica` dentro de la estructura principal de tu proyecto. 

*Nota: Se incluye un archivo `requirements.txt` y se puede crear un entorno virtual para mantener las buenas prácticas, aunque actualmente no existen dependencias de terceros.*

## Gestión de la Base de Datos

La librería incluye un sistema para gestionar el catálogo de productos de forma persistente sin necesidad de configurar servidores externos.

### Inicialización de la Base de Datos
Para generar la base de datos local y cargar los productos desde el CSV incluido:

```python
from LibreriaCargaTermica.catalogo import CatalogoProductosDB

# Instanciar (crea el archivo .db automáticamente si no existe)
db = CatalogoProductosDB()

# Poblar la base de datos desde el archivo CSV
db.poblar_desde_csv("productos.csv")

print("Base de datos lista para usar.")
```

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

### 3. Integración con el Catálogo de Productos
```python
from LibreriaCargaTermica.catalogo import CatalogoProductosDB
from LibreriaCargaTermica.producto import CalculadoraProducto

# 1. Buscar producto en el catálogo
db = CatalogoProductosDB()
datos_papa = db.buscar_producto("Papa")

# 2. Instanciar calculadora con datos del catálogo
papa = CalculadoraProducto(
    nombre=datos_papa['nombre'], 
    rotacion_kg=18144, 
    temp_entrada_c=10.0, 
    temp_salida_c=-18.0, 
    temp_congelacion_c=(datos_papa['temp_congelacion_f'] - 32) * 5/9, # Conversión a °C si es necesario
    cp_arriba_cong=datos_papa['cp_arriba'],
    cp_debajo_cong=datos_papa['cp_debajo'],
    calor_latente=datos_papa['calor_latente'],
    factor_carga=1.0
)

resultados_prod = papa.calcular_carga_producto()
print(f"Carga del Producto ({resultados_prod['producto']}): {resultados_prod['TOTAL_PRODUCTO']} BTU/día")
```
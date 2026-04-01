# LibreriaCargaTermica ❄️🌡️

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/Status-En_Desarrollo-orange.svg)
![Dominio](https://img.shields.io/badge/Dominio-Refrigeración_Industrial-00599C.svg)

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

## Instalación

Al ser una librería de dominio independiente, no requiere instalación mediante `pip`. Simplemente clona este repositorio o copia la carpeta `LibreriaCargaTermica` dentro de la estructura principal de tu proyecto.

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
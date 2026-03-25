# Libreria Carga Termica

Librería de Python orientada al cálculo automatizado y preciso de la carga térmica en cuartos fríos industriales y comerciales. 

Este motor de cálculo está diseñado basándose en prácticas empíricas validadas por la industria de la refrigeración y lineamientos termodinámicos. Su arquitectura desacoplada la hace ideal para integrarse como lógica de negocio en aplicaciones web (Django, Flask), APIs o herramientas de escritorio.

## Características Actuales (v0.1)

* **Módulo de Transmisión (Paredes, Techo, Piso):**
  * Cálculo automatizado de áreas considerando factores de seguridad estructural (+0.2m).
  * Ajuste empírico de la Temperatura Sol-Aire para techos y paredes expuestas.
  * Regla de negocio automatizada para estimar la temperatura del subsuelo según el clima local.
  * Soporte para múltiples sistemas de unidades (Áreas en m² o ft², ΔT en °C, °F, K).
  * Cálculo de Factores K (Transmitancia) ajustados dinámicamente por el tiempo de operación del compresor.

## Instalación

Al ser una librería de dominio independiente, no requiere instalación mediante `pip`. Simplemente clona este repositorio o copia la carpeta `LibreriaCargaTermica` dentro de la estructura de tu proyecto.

## Ejemplo de Uso

```python
from LibreriaCargaTermica.transmision import CalculadoraTransmisionTermica

# 1. Instanciar la calculadora con las dimensiones y temperaturas de diseño
# (Largo, Ancho, Alto en metros | T. Cámara, T. Exterior en °C)
calculadora = CalculadoraTransmisionTermica(
    largo_m=10.0, 
    ancho_m=8.0, 
    alto_m=3.5, 
    temp_camara_c=-20.0, 
    temp_exterior_c=35.0
)

# 2. Obtener la carga térmica total especificando los espesores de panel (en mm)
# y el tiempo de operación del equipo (en horas)
resultados = calculadora.calcular_carga_total(
    espesor_pared_mm=125, 
    espesor_techo_mm=125, 
    espesor_piso_mm=150, 
    tiempo_control=16.0
)

print(f"Carga Total por Transmisión: {resultados['TOTAL']} BTU/día")
print(f"Detalle por superficie: {resultados}")
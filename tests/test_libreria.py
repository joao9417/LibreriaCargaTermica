import unittest
import sys
import os

# Asegurar que la ruta principal esté en el path para poder importar la librería
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from transmision import CalculadoraTransmisionTermica
from infiltracion import CalculadoraInfiltracionTermica
from producto import CalculadoraProducto
from suplementarias import (
    CalculadoraCargaPersonas,
    CalculadoraIluminacion,
    CalculadoraEnvases,
    CalculadoraCargasInternas
)

class TestTransmision(unittest.TestCase):
    def setUp(self):
        # Configuramos un caso base para usar en múltiples pruebas
        # Cuarto de 10x8x3.5m, T_int=-20°C, T_ext=35°C
        self.calc = CalculadoraTransmisionTermica(
            largo_m=10.0, ancho_m=8.0, alto_m=3.5, 
            temp_camara_c=-20.0, temp_exterior_c=35.0
        )

    def test_calculo_areas_m2(self):
        """Verifica que el cálculo de áreas sume correctamente el factor de seguridad (0.2m)"""
        areas = self.calc.obtener_areas(unidad='m2')
        # Techo: (10 + 0.2) * (8 + 0.2) = 10.2 * 8.2 = 83.64
        self.assertAlmostEqual(areas['techo'], 83.64, places=2)
        
    def test_deltas_temperatura(self):
        """Verifica que los diferenciales de temperatura se ajusten por asoleamiento"""
        deltas = self.calc.obtener_deltas_temperatura(unidad='C')
        # Techo a 35°C ext + 5°C asoleamiento = 40°C. Camara a -20°C. Delta = 60°C.
        self.assertEqual(deltas['techo'], 60.0)

    def test_carga_total_transmision(self):
        """Prueba de integración del módulo de transmisión (caso de uso real)"""
        resultados = self.calc.calcular_carga_total(
            espesor_pared_mm=125, 
            espesor_techo_mm=125, 
            espesor_piso_mm=150, 
            tiempo_control=16.0
        )
        self.assertIn('TOTAL', resultados)
        self.assertTrue(resultados['TOTAL'] > 0)


class TestInfiltracion(unittest.TestCase):
    def setUp(self):
        self.calc = CalculadoraInfiltracionTermica(
            largo_m=10.0, ancho_m=8.0, alto_m=3.5, 
            temp_camara_c=-20.0, temp_exterior_c=35.0
        )

    def test_volumen_ft3(self):
        """Verifica la conversión de m3 a ft3"""
        volumen_m3 = 10.0 * 8.0 * 3.5 # 280 m3
        volumen_ft3 = self.calc.obtener_volumen_cuarto('ft3')
        # 280 * 35.3147 = 9888.116
        self.assertAlmostEqual(volumen_ft3, 9888.12, places=1)

    def test_carga_infiltracion_volumen(self):
        """Prueba el cálculo de infiltración por método de renovaciones volumétricas"""
        resultados = self.calc.calcular_carga_por_volumen(tiempo_control=16.0, tipo_uso='normal')
        self.assertIn('TOTAL_INFILTRACION', resultados)
        self.assertTrue(resultados['TOTAL_INFILTRACION'] > 0)


class TestProducto(unittest.TestCase):
    def setUp(self):
        # Caso base usando el ejemplo de "Papa"
        self.calc_producto = CalculadoraProducto(
            nombre="Papa", 
            rotacion_kg=18144, 
            temp_entrada_c=-13.0, 
            temp_salida_c=-18.0, 
            temp_congelacion_f=30.92,
            cp_arriba_cong=0.88,
            cp_debajo_cong=0.5,
            calor_latente=113.0,
            factor_carga=1.0
        )

    def test_masa_diaria_lbs(self):
        """Verifica la conversión de masa de kg a libras"""
        masa_lbs = self.calc_producto.obtener_masa_diaria_lbs()
        # 18144 * 2.20462 ≈ 40000 lbs
        self.assertTrue(39900 < masa_lbs < 40100)

    def test_fases_termodinamicas(self):
        """Verifica que el producto detecte correctamente las etapas (enfriamiento, congelación, subenfriamiento)"""
        deltas = self.calc_producto.obtener_deltas_temperatura()
        
        # Al entrar a -13°C y salir a -18°C, con congelación en -0.6°C:
        # El producto ya está congelado, por lo que SOLO debe haber subenfriamiento.
        self.assertEqual(deltas['refrigeracion_f'], 0.0)
        self.assertEqual(deltas['congelacion_flag'], 0.0)
        self.assertTrue(deltas['subenfriamiento_f'] > 0.0)

    def test_carga_producto_total(self):
        """Prueba el cálculo térmico general del producto en BTU/día"""
        resultados = self.calc_producto.calcular_carga_producto()
        self.assertIn('TOTAL_PRODUCTO', resultados)
        self.assertTrue(resultados['TOTAL_PRODUCTO'] > 0)


class TestPersonas(unittest.TestCase):
    def test_carga_personas(self):
        """Verifica el cálculo correcto de la disipación térmica por operarios."""
        calc = CalculadoraCargaPersonas(temp_camara_c=-20.0, cantidad_personas=2, tiempo_horas=18.0)
        res = calc.calcular_carga()
        self.assertIn('TOTAL_SUPLEMENTARIA', res)
        self.assertTrue(res['TOTAL_SUPLEMENTARIA'] > 0)

class TestIluminacion(unittest.TestCase):
    def test_carga_iluminacion(self):
        """Verifica que el sistema de iluminación calcule lámparas y calor correctamente."""
        calc = CalculadoraIluminacion(
            largo_m=10.0, ancho_m=8.0, alto_m=3.5, 
            luxes_deseados=400, horas_uso=24.0, 
            potencia_lampara_w=120.0, eficiencia_lampara_lm_w=140.0
        )
        res = calc.calcular_carga()
        self.assertIn('TOTAL_SUPLEMENTARIA', res)
        self.assertTrue(res['lamparas_sugeridas'] > 0)
        self.assertTrue(res['watts_reales'] >= res['watts_teoricos'])

class TestEnvases(unittest.TestCase):
    def test_carga_envases(self):
        """Verifica el cálculo de enfriamiento de los envases (canastas)."""
        calc = CalculadoraEnvases(rotacion_kg=15000, temp_entrada_c=6.0, temp_salida_c=2.0, tamano_canasta_cm=25)
        res = calc.calcular_carga()
        self.assertIn('TOTAL_SUPLEMENTARIA', res)
        self.assertTrue(res['unidades_estimadas'] > 0)
        self.assertTrue(res['TOTAL_SUPLEMENTARIA'] > 0)

class TestCargasInternas(unittest.TestCase):
    def test_cargas_internas_gas_caliente(self):
        """Verifica motores, equipos adicionales y lógica de gas caliente (0 watts resistencias)."""
        calc = CalculadoraCargasInternas(
            temp_camara_c=-20.0, volumen_m3=280.0, cambios_aire_hora=20.0, 
            horas_operacion_equipo=20.0, hp_adicionales=10.0, watts_adicionales=5000.0,
            cantidad_cargas_hp=1, horas_operacion_hp=8.0,
            cantidad_cargas_watts=1, horas_operacion_watts=8.0,
            tipo_evaporador='industrial_pesado', tipo_deshielo='gas_caliente'
        )
        res = calc.calcular_carga(subtotal_carga_previa_dia=1000000.0)
        self.assertIn('TOTAL_SUPLEMENTARIA', res)
        # Con gas caliente, la potencia eléctrica instalada en deshielo debe ser 0
        self.assertEqual(res['potencia_estimada_resistencias_W'], 0)
        self.assertTrue(res['btu_dia_ventiladores'] > 0)
        self.assertTrue(res['btu_dia_equipos_extra'] > 0)

    def test_cargas_internas_electrico(self):
        """Verifica que con deshielo eléctrico haya resistencias detectadas."""
        calc = CalculadoraCargasInternas(
            temp_camara_c=-20.0, volumen_m3=280.0, cambios_aire_hora=20.0, 
            horas_operacion_equipo=20.0,
            tipo_deshielo='electrico'
        )
        res = calc.calcular_carga(subtotal_carga_previa_dia=1000000.0)
        # Con deshielo eléctrico, la potencia instalada de resistencias debe ser mayor a 0
        self.assertTrue(res['potencia_estimada_resistencias_W'] > 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)

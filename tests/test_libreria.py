import unittest
import sys
import os

# Asegurar que la ruta principal esté en el path para poder importar la librería
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from transmision import CalculadoraTransmisionTermica
from infiltracion import CalculadoraInfiltracion
from producto import CalculadoraProducto

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
        self.calc = CalculadoraInfiltracion(
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
            temp_congelacion_c=-0.6,
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


if __name__ == '__main__':
    unittest.main(verbosity=2)

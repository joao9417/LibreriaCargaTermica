import sqlite3  
import csv
import os

class CatalogoProductosDB:
    """
    Manejador de la base de datos SQLite para las propiedades
    termodinamicas de los alimentos, actua como un repositorio independiente
    al motor de calculo
    """

    def __init__(self, db_name="productos.db"):
        self.db_name = db_name
        self._crear_tabla()

    def _conectar(self):
        # Configura la conexion para que devuelva los datos como un diccionario
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def _crear_tabla(self):
        # crea la tabla termodinamica si no existe
        query = """
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT,
            nombre TEXT UNIQUE NOT NULL,
            temp_congelacion_f REAL,
            cp_arriba REAL NOT NULL,
            cp_debajo REAL NOT NULL,
            calor_latente REAL NOT NULL,
            resp_0 REAL,
            resp_5 REAL,
            resp_10 REAL,
            resp_15 REAL,
            resp_20 REAL
            )
            """
            
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    def insertar_producto(self, categoria: str, nombre: str, temp_congelacion_f: float, cp_arriba: float, cp_debajo: float, calor_latente: float,
    resp_0: float, resp_5: float, resp_10: float, resp_15: float, resp_20: float):
        # Inserta o actualiza un producto de la base de datos
        query = """
        INSERT INTO productos(categoria, nombre, temp_congelacion_f, cp_arriba, cp_debajo, calor_latente, resp_0, resp_5, resp_10, resp_15, resp_20)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(nombre) DO UPDATE SET
            categoria = excluded.categoria,
            temp_congelacion_f = excluded.temp_congelacion_f,
            cp_arriba = excluded.cp_arriba,
            cp_debajo = excluded.cp_debajo,
            calor_latente = excluded.calor_latente,
            resp_0 = excluded.resp_0,
            resp_5 = excluded.resp_5,
            resp_10 = excluded.resp_10,
            resp_15 = excluded.resp_15,
            resp_20 = excluded.resp_20  
        """
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (categoria, nombre, temp_congelacion_f, cp_arriba, cp_debajo, calor_latente, resp_0, resp_5, resp_10, resp_15, resp_20))
            conn.commit()
    
    def buscar_producto(self, nombre: str) -> dict:
        # Busca un producto por su nombre y devuelve sus propiedades
        query = "SELECT * FROM productos WHERE nombre = ?"

        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (nombre,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            else:
                raise ValueError(f"El producto '{nombre}' no se encuentra en la base de datos.")
    

    def poblar_desde_csv(self, ruta_csv:str):
        """
        Lee el archivo CSV y llena la base de datos automaticamente.
        """
        if not os.path.exists(ruta_csv):
            print(f"Error: No se encontro el archivo '{ruta_csv}'.")
            return
        
        print(f"Cargando datos desde CSV: {ruta_csv}")

        # Funcion interna para limpiar la celda de Excel
        def _limpiar_numero(valor_str):
            valor = valor_str.strip().upper()
            if valor == "FALTA" or valor == "" or valor =="N/A":
                return None
            return float(valor.replace(",", "."))
        
        with open(ruta_csv, mode='r', encoding='latin-1') as archivo:
            # Detectar el delimitador automaticamente
            muestra = archivo.readline()
            delimitador = ';' if ';' in muestra else ','
            archivo.seek(0)
            
            lector = csv.reader(archivo, delimiter=delimitador)
            next(lector) # Saltar cabeceras

            contador = 0
            for fila in lector:
                if not fila or not fila[0].strip():
                    continue

                try:
                    categoria = fila[0].strip()
                    nombre = fila[1].strip()
                    
                    # Limpiamos todas las columnas usando nuestra nueva funcion
                    temp_congelacion_f = _limpiar_numero(fila[2])
                    cp_arriba = _limpiar_numero(fila[3])
                    cp_debajo = _limpiar_numero(fila[4])
                    calor_latente = _limpiar_numero(fila[5])

                    # Extraemos los datos de respiracion
                    resp_0 = _limpiar_numero(fila[6]) if len(fila) > 6 else None
                    resp_5 = _limpiar_numero(fila[7]) if len(fila) > 7 else None
                    resp_10 = _limpiar_numero(fila[8]) if len(fila) > 8 else None
                    resp_15 = _limpiar_numero(fila[9]) if len(fila) > 9 else None
                    resp_20 = _limpiar_numero(fila[10]) if len(fila) > 10 else None
                    
                    self.insertar_producto(
                        categoria, nombre, temp_congelacion_f, cp_arriba, cp_debajo, calor_latente,
                        resp_0, resp_5, resp_10, resp_15, resp_20
                    )
                    contador += 1
                    
                except Exception as e:
                    print(f"Error al procesar '{fila[0] if fila else 'Fila vacia'}': {e}")
                    
        print(f"Finalizado! Se guardaron {contador} productos en la base de datos SQLite.")

    def obtener_todos_los_productos(self) -> list:
        """
        Extrae todos los productos de la base de datos SQLite.
        Este metodo funciona como un puente para exportar los datos a Django o APIs
        """

        query = "SELECT * FROM productos"
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            filas = cursor.fetchall()

            # Convierte las filas en SQLite en una lista de diccionarios limpios
            return [dict(fila) for fila in filas]

            """
            models.py
            Django side
            when you create your Django project, you will create a django model to migrate the data from the sqlite database to the django database

            from django.db import models

            class ProductoTermico(models.Model):
                categoria = models.CharField(max_length=100, null=True, blank=True)
                nombre = models.CharField(max_length=100, unique=True)
                temp_congelacion_f = models.FloatField(null=True, blank=True)
                cp_arriba = models.FloatField()
                cp_debajo = models.FloatField()
                calor_latente = models.FloatField()
                
                # Datos de respiración
                resp_0 = models.FloatField(null=True, blank=True)
                resp_5 = models.FloatField(null=True, blank=True)
                resp_10 = models.FloatField(null=True, blank=True)
                resp_15 = models.FloatField(null=True, blank=True)
                resp_20 = models.FloatField(null=True, blank=True)

                def __str__(self):
                    return self.nombre
            """

            """
            The Django migration Script
            migrar_catalogo.py

            from django.core.management.base import BaseCommand
            from mi_app.models import ProductoTermico # Your Django model

            # Import the custom library!
            from LibreriaCargaTermica.catalogo import CatalogoProductosDB 

            class Command(BaseCommand):
                help = 'Migra la base de datos SQLite de la librería térmica al ORM de Django'

                def handle(self, *args, **kwargs):
                    self.stdout.write("Iniciando migración desde SQLite...")
                    
                    # 1. Instanciamos la base de datos de tu librería
                    db_libreria = CatalogoProductosDB(db_name="ruta/a/tu/productos.db")
                    
                    # 2. Obtenemos todos los datos usando el método puente
                    productos_sqlite = db_libreria.obtener_todos_los_productos()
                    
                    contador = 0
                    for prod in productos_sqlite:
                        # 3. Usamos update_or_create para evitar duplicados si corres el script 2 veces
                        obj, created = ProductoTermico.objects.update_or_create(
                            nombre=prod['nombre'],
                            defaults={
                                'categoria': prod['categoria'],
                                'temp_congelacion_f': prod['temp_congelacion_f'],
                                'cp_arriba': prod['cp_arriba'],
                                'cp_debajo': prod['cp_debajo'],
                                'calor_latente': prod['calor_latente'],
                                'resp_0': prod['resp_0'],
                                'resp_5': prod['resp_5'],
                                'resp_10': prod['resp_10'],
                                'resp_15': prod['resp_15'],
                                'resp_20': prod['resp_20'],
                            }
                        )
                        contador += 1
                        
                    self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se migraron {contador} productos a Django.'))


            """



if __name__ == "__main__":
    db = CatalogoProductosDB()
    db.poblar_desde_csv("productos.csv")
            

    
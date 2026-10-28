"""Carga e inspección inicial del conjunto de datos de emisiones de CO2.

Fuente: Our World in Data (OWID), repositorio owid/co2-data.
"""
import os

import pandas as pd

# Columnas mínimas que debe tener el archivo para continuar con el análisis.
COLUMNAS_ESPERADAS = [
    "country",
    "year",
    "iso_code",
    "population",
    "gdp",
    "co2",
    "co2_per_capita",
]


def cargar_datos(ruta):
    """
    Carga un conjunto de datos desde un archivo (CSV, JSON o Excel).

    Parámetros
    ----------
    ruta : str
        Ruta relativa del archivo.

    Retorna
    -------
    pandas.DataFrame
        DataFrame con los datos cargados, o None si ocurre un error.
    """
    extension = os.path.splitext(ruta)[1].lower()
    try:
        if extension == ".csv":
            datos = pd.read_csv(ruta)
        elif extension == ".json":
            datos = pd.read_json(ruta)
        elif extension in (".xlsx", ".xlsm", ".xls"):
            datos = pd.read_excel(ruta)
        else:
            print(f"Error: formato '{extension}' no soportado.")
            return None
        return datos
    except FileNotFoundError:
        print(f"Error: no se encontró el archivo '{ruta}'.")
    except pd.errors.EmptyDataError:
        print("Error: el archivo no contiene datos.")
    except pd.errors.ParserError:
        print("Error: no fue posible interpretar el archivo.")
    except UnicodeDecodeError:
        print("Error: la codificación del archivo no es compatible.")
    return None


def validar_estructura(datos, columnas=COLUMNAS_ESPERADAS):
    """Verifica que el DataFrame contenga las columnas necesarias.

    Retorna True si están todas presentes; en caso contrario informa
    cuáles faltan y retorna False.
    """
    faltantes = [c for c in columnas if c not in datos.columns]
    if faltantes:
        print(f"Advertencia: faltan columnas esperadas: {faltantes}")
        return False
    print("Estructura válida: están presentes todas las columnas esperadas.")
    return True


def inspeccionar_datos(datos):
    """Muestra un diagnóstico inicial del DataFrame."""
    if datos is None:
        print("No existen datos disponibles para inspeccionar.")
        return

    print("\nDimensiones:")
    print(datos.shape)

    print("\nColumnas:")
    print(datos.columns.tolist())

    print("\nTipos de datos:")
    print(datos.dtypes)

    print("\nPrimeros registros:")
    print(datos.head())

    print("\nValores nulos por columna:")
    print(datos.isna().sum())

    print("\nFilas duplicadas:")
    print(datos.duplicated().sum())

    print("\nResumen estadístico:")
    print(datos.describe(include="all"))

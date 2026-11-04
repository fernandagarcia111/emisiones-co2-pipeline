"""Pipeline de datos: emisiones de CO2.

Ejecutar desde la raíz del proyecto:  python main.py
"""
import os

import pandas as pd

from src import limpieza, transformaciones, validaciones
from src.carga import cargar_datos, inspeccionar_datos

RUTA_ORIGINAL = os.path.join("datos", "originales", "owid-co2-data.csv")
RUTA_LIMPIO = os.path.join("datos", "procesados", "dataset_limpio.csv")
RUTA_MUNDIAL = os.path.join("datos", "procesados", "serie_mundial.csv")
CARPETA_REPORTES = "reportes"

# Variables documentadas en el diccionario de datos (Avance 1).
VARIABLES = ["country", "year", "iso_code", "population", "gdp", "co2",
             "co2_per_capita", "co2_growth_prct", "share_global_co2",
             "cumulative_co2"]


def etapa(numero, nombre):
    print("\n" + "=" * 70)
    print(f"ETAPA {numero}: {nombre}")
    print("=" * 70)


def guardar(tabla, nombre):
    tabla.to_csv(os.path.join(CARPETA_REPORTES, nombre), index=False)


def main():
    pd.set_option("display.width", 110)
    pd.set_option("display.max_columns", 20)
    os.makedirs(os.path.dirname(RUTA_LIMPIO), exist_ok=True)
    os.makedirs(CARPETA_REPORTES, exist_ok=True)
    registro = []

    # ------------------------------------------------------------- 1. Carga
    etapa(1, "Carga de datos originales")
    original = cargar_datos(RUTA_ORIGINAL)
    if original is None:
        print("El programa finalizó sin procesar los datos.")
        return
    if not validaciones.validar_columnas(original, validaciones.COLUMNAS_MINIMAS):
        return
    huella_inicial = validaciones.calcular_sha256(RUTA_ORIGINAL)
    print(f"Archivo: {RUTA_ORIGINAL}")
    print(f"Huella SHA-256: {huella_inicial[:16]}...")
    print(f"Dimensiones: {original.shape}")

    # ------------------------------------------------------- 2. Diagnóstico
    etapa(2, "Diagnóstico de calidad")
    antes = validaciones.diagnosticar(original, validaciones.RANGOS_ORIGINAL)
    print(f"Filas: {antes['filas']:,}   Columnas: {antes['columnas']}")
    print(f"Tipos de columnas: {antes['tipos']}")
    print(f"Valores nulos (79 columnas): {antes['nulos_total']:,}")
    print(f"Filas duplicadas: {antes['duplicados_filas']}")
    print(f"Pares country-year repetidos: {antes['duplicados_clave']}")
    print("\nValores nulos en las variables del diccionario:")
    tabla_n = antes["tabla_nulos"].loc[VARIABLES].sort_values("nulos", ascending=False)
    print(tabla_n)
    print("\nValores fuera de rango por variable:")
    print(antes["fuera_de_rango"])
    sin_iso = original.loc[original["iso_code"].isna(), "country"].nunique()
    print(f"\nEntidades sin iso_code (agregados o regiones): {sin_iso}")
    print("\ndf[variables].info():")
    original[VARIABLES].info()
    guardar(antes["tabla_nulos"].reset_index(names="variable"), "diagnostico_inicial.csv")

    # ------------------------------------------------------------ 3. Limpieza
    etapa(3, "Limpieza")
    nulos_iniciales = original[VARIABLES].isna().sum()
    df = limpieza.normalizar_nombres(original, registro)
    df = limpieza.limpiar_texto(df, registro)
    df = limpieza.recuperar_codigos_iso(df, registro)
    mundial = limpieza.extraer_serie_mundial(df)
    df = limpieza.separar_paises(df, registro)
    df = limpieza.filtrar_periodo(df, registro)
    df = limpieza.eliminar_entidades_sin_co2(df, registro)
    df = limpieza.eliminar_duplicados(df, registro)
    df = df[list(limpieza.RENOMBRAR.values())]
    print(f"Filas tras la limpieza: {len(df):,}")
    print(f"Variables conservadas: {df.shape[1]} de {original.shape[1]}")

    # ------------------------------------------------- 4. Tratamiento de nulos
    etapa(4, "Tratamiento de nulos")
    df = limpieza.tratar_nulos(df, mundial, registro)
    tabla_nulos = limpieza.tabla_nulos(nulos_iniciales, df)
    print(tabla_nulos[["variable", "nulos_iniciales", "estrategia", "nulos_finales"]]
          .to_string(index=False, max_colwidth=48))
    print("\nRegistro de acciones (se exporta a reportes/registro_limpieza.csv):")
    print(pd.DataFrame(registro)[["accion", "filas_afectadas"]]
          .to_string(index=False, max_colwidth=62))

    # ----------------------------------------------------- 5. Transformaciones
    etapa(5, "Transformaciones")
    df, tabla_trans = transformaciones.aplicar_transformaciones(df)
    print(tabla_trans[["variable_original", "resultado", "tipo_final"]]
          .to_string(index=False))

    # ------------------------------------------------------------ 6. Validación
    etapa(6, "Validación")
    errores = validaciones.validar_dataset_limpio(df)
    if errores:
        for e in errores:
            print("ERROR:", e)
        print("El dataset no se exportó porque falló la validación.")
        return
    print("Validación superada: columnas, tipos, duplicados, categorías y rangos.")
    despues = validaciones.diagnosticar(df, validaciones.RANGOS_LIMPIO, ("pais", "anio"))
    sin_tratar = validaciones.contar_fuera_de_rango(
        df, validaciones.RANGOS_LIMPIO,
        excluir={"co2_per_capita_t": df["atipico_per_capita"]}).sum()
    print(f"Valores fuera de rango sin tratar: {int(sin_tratar)}")
    print(f"Valores atípicos marcados (co2_per_capita_t > 100): "
          f"{int(df['atipico_per_capita'].sum())}")

    # ------------------------------------------------------------ 7. Exportación
    etapa(7, "Exportación")
    df.to_csv(RUTA_LIMPIO, index=False)
    mundial.to_csv(RUTA_MUNDIAL, index=False)
    print(f"Dataset limpio: {RUTA_LIMPIO}  {df.shape}")
    print(f"Serie mundial: {RUTA_MUNDIAL}  {mundial.shape}")

    origen = {v.strip() for fila in tabla_trans["variable_original"]
              for v in fila.replace(" y ", ",").split(",")}
    nuevas = [c for c in df.columns if c not in limpieza.RENOMBRAR.values()]
    nulos_vars = int(df[list(limpieza.RENOMBRAR.values())].isna().sum().sum())
    comparacion = pd.DataFrame([
        ["Filas", antes["filas"], len(df)],
        ["Columnas", antes["columnas"], df.shape[1]],
        ["Valores nulos (todas las columnas)", antes["nulos_total"], despues["nulos_total"]],
        ["Valores nulos (10 variables del diccionario)", int(nulos_iniciales.sum()), nulos_vars],
        ["Filas duplicadas", antes["duplicados_filas"], despues["duplicados_filas"]],
        ["Valores fuera de rango", antes["fuera_de_rango_total"], int(sin_tratar)],
        ["Variables transformadas", 0, len(origen)],
        ["Variables nuevas", 0, len(nuevas)],
    ], columns=["indicador", "antes", "despues"])
    print("\nComparación antes y después:")
    print(comparacion.to_string(index=False))

    guardar(pd.DataFrame(registro), "registro_limpieza.csv")
    guardar(tabla_nulos, "tratamiento_nulos.csv")
    guardar(tabla_trans, "transformaciones.csv")
    guardar(comparacion, "comparacion_antes_despues.csv")

    huella_final = validaciones.calcular_sha256(RUTA_ORIGINAL)
    intacto = "sí" if huella_final == huella_inicial else "NO"
    print(f"\nArchivo original sin modificaciones: {intacto}")

    print("\ndf.info() del dataset limpio:")
    df.info()
    columnas = ["pais", "anio", "periodo_politica", "co2_mt", "co2_per_capita_t",
                "nivel_per_capita", "atipico_per_capita"]
    print("\ndf[columnas].sample(5, random_state=1):")
    print(df[columnas].sample(5, random_state=1))


if __name__ == "__main__":
    main()

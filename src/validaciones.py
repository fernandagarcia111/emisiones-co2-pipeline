"""Validaciones: columnas, tipos, rangos y diagnóstico de calidad.

Este módulo no modifica datos: solo revisa y entrega indicadores.
"""
import hashlib

import pandas as pd

# Rangos de plausibilidad por variable, con los nombres originales del archivo.
# Formato: columna -> (mínimo, máximo). None significa sin límite.
RANGOS_ORIGINAL = {
    "year": (1750, 2024),
    "population": (1, None),
    "gdp": (1, None),
    "co2": (0, None),
    "co2_per_capita": (0, 100),
    "share_global_co2": (0, 100),
    "cumulative_co2": (0, None),
}

# Los mismos rangos, con los nombres de columna del dataset limpio.
RANGOS_LIMPIO = {
    "anio": (1950, 2024),
    "poblacion": (1, None),
    "pib": (1, None),
    "co2_mt": (0, None),
    "co2_per_capita_t": (0, 100),
    "participacion_mundial_pct": (0, 100),
    "co2_acumulado_mt": (0, None),
}

COLUMNAS_MINIMAS = [
    "country", "year", "iso_code", "population", "gdp", "co2", "co2_per_capita",
]

COLUMNAS_LIMPIO = [
    "pais", "codigo_iso", "anio", "fecha", "decada", "periodo_politica",
    "poblacion", "pib", "co2_mt", "co2_gt", "co2_per_capita_t",
    "nivel_per_capita", "atipico_per_capita", "co2_por_pib_kg",
    "variacion_anual_pct", "participacion_mundial_pct", "co2_acumulado_mt",
]

PERIODOS_VALIDOS = {"pre_kioto", "kioto_a_paris", "post_paris"}


def validar_columnas(df, columnas):
    """Retorna True si el DataFrame tiene todas las columnas indicadas."""
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        print(f"Advertencia: faltan columnas: {faltantes}")
        return False
    return True


def contar_fuera_de_rango(df, rangos, excluir=None):
    """Cuenta valores fuera de rango por columna.

    excluir: diccionario columna -> serie booleana con las filas que no se
    deben contar (por ejemplo, valores ya marcados como atípicos).
    """
    resultado = {}
    for col, (minimo, maximo) in rangos.items():
        if col not in df.columns:
            continue
        serie = df[col]
        fuera = pd.Series(False, index=df.index)
        if minimo is not None:
            fuera |= serie < minimo
        if maximo is not None:
            fuera |= serie > maximo
        if excluir and col in excluir:
            fuera &= ~excluir[col]
        resultado[col] = int(fuera.sum())
    return pd.Series(resultado, dtype="int64")


def diagnosticar(df, rangos, clave=("country", "year")):
    """Indicadores de calidad de un DataFrame, listos para informar."""
    nulos = df.isna().sum()
    tabla_nulos = pd.DataFrame({
        "nulos": nulos,
        "porcentaje": (nulos / len(df) * 100).round(1),
    }).sort_values("nulos", ascending=False)
    clave = [c for c in clave if c in df.columns]
    fuera = contar_fuera_de_rango(df, rangos)
    return {
        "filas": len(df),
        "columnas": df.shape[1],
        "nulos_total": int(nulos.sum()),
        "tabla_nulos": tabla_nulos,
        "duplicados_filas": int(df.duplicated().sum()),
        "duplicados_clave": int(df.duplicated(clave).sum()) if clave else 0,
        "fuera_de_rango": fuera,
        "fuera_de_rango_total": int(fuera.sum()),
        "tipos": df.dtypes.astype(str).value_counts().to_dict(),
    }


def validar_dataset_limpio(df):
    """Comprueba que el dataset final cumpla las reglas esperadas.

    Retorna una lista con los errores encontrados (vacía si todo está bien).
    """
    errores = []
    if not validar_columnas(df, COLUMNAS_LIMPIO):
        errores.append("Faltan columnas esperadas en el dataset limpio.")
        return errores

    # Tipos
    if not pd.api.types.is_integer_dtype(df["anio"]):
        errores.append("anio debe ser entero.")
    if not pd.api.types.is_datetime64_any_dtype(df["fecha"]):
        errores.append("fecha debe ser datetime.")
    if not pd.api.types.is_bool_dtype(df["atipico_per_capita"]):
        errores.append("atipico_per_capita debe ser booleana.")
    for col in ["poblacion", "pib", "co2_mt", "co2_gt", "co2_per_capita_t",
                "co2_por_pib_kg", "variacion_anual_pct",
                "participacion_mundial_pct", "co2_acumulado_mt"]:
        if not pd.api.types.is_numeric_dtype(df[col]):
            errores.append(f"{col} debe ser numérica.")

    # Identificadores y duplicados
    if df.duplicated().any():
        errores.append("Existen filas duplicadas.")
    if df.duplicated(["pais", "anio"]).any():
        errores.append("Existen pares pais-anio repetidos.")
    if df["pais"].isna().any() or df["codigo_iso"].isna().any():
        errores.append("pais y codigo_iso no deben tener nulos.")
    if not df["codigo_iso"].astype(str).str.fullmatch(r"[A-Z]{3}").all():
        errores.append("codigo_iso debe tener 3 letras mayúsculas.")

    # Texto sin espacios sobrantes
    pais = df["pais"].astype(str)
    if (pais != pais.str.strip()).any():
        errores.append("Hay nombres de país con espacios sobrantes.")

    # Categorías y rangos (los atípicos marcados no cuentan como error)
    if not set(df["periodo_politica"].astype(str)) <= PERIODOS_VALIDOS:
        errores.append("periodo_politica contiene categorías no previstas.")
    fuera = contar_fuera_de_rango(
        df, RANGOS_LIMPIO, excluir={"co2_per_capita_t": df["atipico_per_capita"]}
    )
    for col, cantidad in fuera.items():
        if cantidad > 0:
            errores.append(f"{col}: {cantidad} valores fuera de rango sin marcar.")
    return errores


def calcular_sha256(ruta):
    """Huella del archivo, para comprobar que el original no se modificó."""
    h = hashlib.sha256()
    with open(ruta, "rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()

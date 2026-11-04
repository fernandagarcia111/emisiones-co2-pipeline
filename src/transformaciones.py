"""Transformaciones: conversión de tipos y creación de variables."""
import numpy as np
import pandas as pd

UMBRAL_ATIPICO = 100   # t por persona; sobre este valor se marca como atípico


def _anotar(tabla, origen, transformacion, resultado, tipo_final):
    tabla.append({
        "variable_original": origen,
        "transformacion": transformacion,
        "resultado": resultado,
        "tipo_final": str(tipo_final),
    })


def convertir_tipos(df, tabla):
    """Convierte columnas a tipos adecuados."""
    df = df.copy()
    df["anio"] = df["anio"].astype("int64")
    df["poblacion"] = df["poblacion"].round().astype("Int64")
    df["pais"] = df["pais"].astype("category")
    df["codigo_iso"] = df["codigo_iso"].astype("string")
    _anotar(tabla, "poblacion", "float64 a entero con nulos (astype Int64)",
            "poblacion", df["poblacion"].dtype)
    _anotar(tabla, "pais", "texto a categoría", "pais", df["pais"].dtype)
    _anotar(tabla, "codigo_iso", "object a string", "codigo_iso", df["codigo_iso"].dtype)
    return df


def convertir_fecha(df, tabla):
    """Crea una fecha real a partir del año (1 de enero)."""
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["anio"].astype(str), format="%Y")
    _anotar(tabla, "anio", "pd.to_datetime(anio, format='%Y')", "fecha",
            df["fecha"].dtype)
    return df


def extraer_decada(df, tabla):
    """Extrae la década del año."""
    df = df.copy()
    df["decada"] = (df["anio"] // 10) * 10
    _anotar(tabla, "anio", "Extraer década: anio // 10 * 10", "decada",
            df["decada"].dtype)
    return df


def clasificar_periodo_politica(df, tabla):
    """Clasifica cada año según los hitos Kioto (1997) y París (2015)."""
    df = df.copy()
    df["periodo_politica"] = pd.cut(
        df["anio"], bins=[-np.inf, 1996, 2014, np.inf],
        labels=["pre_kioto", "kioto_a_paris", "post_paris"]).astype("string")
    _anotar(tabla, "anio", "Clasificar por rangos (pd.cut): hasta 1996, 1997-2014, desde 2015",
            "periodo_politica", df["periodo_politica"].dtype)
    return df


def convertir_unidades(df, tabla):
    """Pasa las emisiones de millones a miles de millones de toneladas."""
    df = df.copy()
    df["co2_gt"] = df["co2_mt"] / 1000
    _anotar(tabla, "co2_mt", "Cambio de unidad: Mt a Gt (dividir por 1000)",
            "co2_gt", df["co2_gt"].dtype)
    return df


def calcular_intensidad(df, tabla):
    """Kilogramos de CO2 por dólar internacional de PIB."""
    df = df.copy()
    pib = df["pib"].where(df["pib"] > 0)
    df["co2_por_pib_kg"] = df["co2_mt"] * 1e9 / pib
    _anotar(tabla, "co2_mt y pib", "Nueva variable: co2_mt * 1e9 / pib",
            "co2_por_pib_kg", df["co2_por_pib_kg"].dtype)
    return df


def clasificar_nivel_per_capita(df, tabla):
    """Clasifica las emisiones per cápita en cuatro niveles."""
    df = df.copy()
    df["nivel_per_capita"] = pd.cut(
        df["co2_per_capita_t"], bins=[-np.inf, 2, 6, 12, np.inf],
        labels=["bajo", "medio", "alto", "muy_alto"]).astype("string")
    _anotar(tabla, "co2_per_capita_t",
            "Clasificar por rangos: hasta 2, 2-6, 6-12 y más de 12 t por persona",
            "nivel_per_capita", df["nivel_per_capita"].dtype)
    return df


def marcar_atipicos(df, tabla):
    """Marca valores per cápita sobre el umbral, sin eliminarlos."""
    df = df.copy()
    df["atipico_per_capita"] = (df["co2_per_capita_t"] > UMBRAL_ATIPICO).fillna(False).astype(bool)
    _anotar(tabla, "co2_per_capita_t",
            f"Marcar valores mayores a {UMBRAL_ATIPICO} t por persona",
            "atipico_per_capita", df["atipico_per_capita"].dtype)
    return df


def aplicar_transformaciones(df):
    """Ejecuta todas las transformaciones y retorna (df, tabla)."""
    tabla = []
    df = convertir_tipos(df, tabla)
    df = convertir_fecha(df, tabla)
    df = extraer_decada(df, tabla)
    df = clasificar_periodo_politica(df, tabla)
    df = convertir_unidades(df, tabla)
    df = calcular_intensidad(df, tabla)
    df = clasificar_nivel_per_capita(df, tabla)
    df = marcar_atipicos(df, tabla)
    orden = [
        "pais", "codigo_iso", "anio", "fecha", "decada", "periodo_politica",
        "poblacion", "pib", "co2_mt", "co2_gt", "co2_per_capita_t",
        "nivel_per_capita", "atipico_per_capita", "co2_por_pib_kg",
        "variacion_anual_pct", "participacion_mundial_pct", "co2_acumulado_mt",
    ]
    return df[orden], pd.DataFrame(tabla)

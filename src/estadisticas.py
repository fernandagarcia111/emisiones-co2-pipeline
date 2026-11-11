"""Estadística descriptiva del dataset limpio.

Todas las funciones reciben el DataFrame de datos/procesados/dataset_limpio.csv
y retornan tablas listas para exportar a resultados/.
"""
import pandas as pd

VARIABLES_NUMERICAS = {
    "co2_mt": "Emisiones de CO2 (Mt)",
    "co2_per_capita_t": "Emisiones per cápita (t/persona)",
    "poblacion": "Población (personas)",
    "pib": "PIB (USD internacionales)",
    "co2_por_pib_kg": "Intensidad de CO2 (kg/USD)",
    "variacion_anual_pct": "Variación anual de CO2 (%)",
    "participacion_mundial_pct": "Participación mundial (%)",
}

VARIABLES_CATEGORICAS = ["periodo_politica", "nivel_per_capita"]


def estadisticas_numericas(df, variables=VARIABLES_NUMERICAS):
    """Medidas descriptivas por variable numérica."""
    filas = []
    for col, nombre in variables.items():
        s = df[col].astype("float64").dropna()
        q1, mediana, q3 = s.quantile([0.25, 0.5, 0.75])
        filas.append({
            "variable": col,
            "descripcion": nombre,
            "registros_validos": int(s.count()),
            "nulos": int(df[col].isna().sum()),
            "media": s.mean(),
            "mediana": mediana,
            "minimo": s.min(),
            "maximo": s.max(),
            "rango": s.max() - s.min(),
            "desv_estandar": s.std(),
            "q1": q1,
            "q3": q3,
            "rango_intercuartil": q3 - q1,
        })
    return pd.DataFrame(filas).round(3)


def frecuencias_categoricas(df, variables=VARIABLES_CATEGORICAS):
    """Frecuencia absoluta y relativa de las variables categóricas."""
    filas = []
    for col in variables:
        conteo = df[col].value_counts(dropna=True)
        total = conteo.sum()
        for categoria, n in conteo.items():
            filas.append({
                "variable": col,
                "categoria": categoria,
                "frecuencia": int(n),
                "porcentaje": round(n / total * 100, 1),
            })
    return pd.DataFrame(filas)


def estadisticas_por_periodo(df):
    """Mediana y media de variables clave según el período de política."""
    orden = ["pre_kioto", "kioto_a_paris", "post_paris"]
    grupos = df.groupby("periodo_politica")
    tabla = grupos.agg(
        registros=("pais", "size"),
        co2_mediana_mt=("co2_mt", "median"),
        per_capita_mediana_t=("co2_per_capita_t", "median"),
        per_capita_media_t=("co2_per_capita_t", "mean"),
        variacion_anual_mediana_pct=("variacion_anual_pct", "median"),
        variacion_anual_media_pct=("variacion_anual_pct", "mean"),
    ).reindex(orden)
    return tabla.round(3).reset_index()

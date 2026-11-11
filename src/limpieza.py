"""Limpieza de datos: nombres, texto, entidades, duplicados y nulos.

Cada función que elimina o corrige datos deja constancia en `registro`,
una lista de diccionarios que main.py exporta a reportes/registro_limpieza.csv.
"""
import numpy as np
import pandas as pd

ANIO_INICIO = 1950      # antes de esta fecha la cobertura es escasa
MAX_BRECHA = 5          # años consecutivos máximos que se interpolan
CODIGOS_RECUPERADOS = {"Kosovo": "XKX"}   # país sin código ISO oficial

RENOMBRAR = {
    "country": "pais",
    "iso_code": "codigo_iso",
    "year": "anio",
    "population": "poblacion",
    "gdp": "pib",
    "co2": "co2_mt",
    "co2_per_capita": "co2_per_capita_t",
    "co2_growth_prct": "variacion_anual_pct",
    "share_global_co2": "participacion_mundial_pct",
    "cumulative_co2": "co2_acumulado_mt",
}

# Estrategia y justificación por variable (se usa en la tabla del informe).
ESTRATEGIAS = {
    "pais": ("Sin nulos", "Columna completa en el original."),
    "anio": ("Sin nulos", "Columna completa en el original."),
    "codigo_iso": (
        "Recuperar Kosovo (XKX) y eliminar entidades que no son países",
        "El nulo identifica agregados (World, continentes). Kosovo es un país "
        "sin código ISO oficial y se recupera con el código de uso común."),
    "poblacion": (
        "Mantener nulo",
        "Los nulos restantes corresponden a Antártida e Isla Christmas, sin "
        "población en la fuente. No hay otra fuente para recuperarla."),
    "pib": (
        "Mantener nulo",
        "Variable auxiliar con datos hasta 2022. Imputarla con media o cero "
        "inventaría producción económica."),
    "co2_mt": (
        "Interpolar brechas internas de hasta 5 años; mantener el resto",
        "Una brecha corta entre dos años observados se aproxima bien con una "
        "recta. Un nulo al inicio de la serie significa que no hay registro."),
    "co2_per_capita_t": (
        "Recalcular como co2 por población",
        "Es una razón exacta entre dos variables ya disponibles."),
    "variacion_anual_pct": (
        "Mantener nulo",
        "El primer año de cada serie no tiene año anterior; la variación "
        "no está definida."),
    "participacion_mundial_pct": (
        "Recalcular como co2 país sobre co2 mundial",
        "Se usa la serie mundial del mismo archivo."),
    "co2_acumulado_mt": (
        "Interpolar brechas internas de hasta 5 años; mantener el resto",
        "Mismo criterio que co2: es una serie monótona y creciente."),
}


def _anotar(registro, etapa, accion, filas, justificacion):
    registro.append({
        "etapa": etapa,
        "accion": accion,
        "filas_afectadas": int(filas),
        "justificacion": justificacion,
    })


def normalizar_nombres(df, registro):
    """Limpia los nombres de columna y los traduce al español."""
    limpios = (df.columns.str.strip().str.lower()
               .str.replace(r"\s+", "_", regex=True))
    df = df.copy()
    df.columns = limpios
    renombradas = [c for c in RENOMBRAR if c in df.columns]
    df = df.rename(columns=RENOMBRAR)
    _anotar(registro, "Limpieza", "Normalizar y renombrar columnas",
            len(renombradas),
            f"{len(renombradas)} columnas renombradas al español para "
            "facilitar su uso y documentación.")
    return df


def limpiar_texto(df, registro):
    """Elimina espacios sobrantes en las columnas de texto."""
    df = df.copy()
    cambios = 0
    for col in ["pais", "codigo_iso"]:
        original = df[col].astype("string")
        limpio = original.str.strip().str.replace(r"\s+", " ", regex=True)
        cambios += int((original.fillna("") != limpio.fillna("")).sum())
        df[col] = limpio
    _anotar(registro, "Limpieza", "Eliminar espacios sobrantes en texto",
            cambios, "Evita categorías distintas para un mismo país.")
    return df


def recuperar_codigos_iso(df, registro):
    """Asigna código a países que no lo traen en la fuente."""
    df = df.copy()
    total = 0
    for pais, codigo in CODIGOS_RECUPERADOS.items():
        mascara = (df["pais"] == pais) & df["codigo_iso"].isna()
        df.loc[mascara, "codigo_iso"] = codigo
        total += int(mascara.sum())
    _anotar(registro, "Nulos", "Recuperar codigo_iso de Kosovo (XKX)", total,
            "Kosovo es un país, no un agregado. XKX es el código de uso común "
            "(no es oficial ISO).")
    return df


def extraer_serie_mundial(df):
    """Retorna la serie de 'World' desde ANIO_INICIO, para uso de referencia."""
    mundial = df[(df["pais"] == "World") & (df["anio"] >= ANIO_INICIO)]
    columnas = ["anio", "poblacion", "co2_mt", "co2_per_capita_t"]
    return mundial[columnas].reset_index(drop=True)


def separar_paises(df, registro):
    """Elimina filas que no son países (agregados y regiones)."""
    sin_codigo = df["codigo_iso"].isna()
    entidades = sorted(df.loc[sin_codigo, "pais"].unique())
    _anotar(registro, "Limpieza",
            f"Eliminar {len(entidades)} entidades que no son países", sin_codigo.sum(),
            "World, continentes, grupos de ingreso y regiones duplican a los "
            "países y distorsionan rankings. World se conserva aparte.")
    return df[~sin_codigo].copy()


def filtrar_periodo(df, registro, desde=ANIO_INICIO):
    """Elimina registros anteriores al año de inicio del análisis."""
    antiguos = df["anio"] < desde
    _anotar(registro, "Limpieza", f"Eliminar registros anteriores a {desde}",
            antiguos.sum(),
            "Antes de 1950 la cobertura es escasa y la mayoría de los nulos "
            "se concentra ahí. Kioto (1997) y París (2015) quedan dentro.")
    return df[~antiguos].copy()


def eliminar_entidades_sin_co2(df, registro):
    """Elimina países sin ninguna observación de CO2 en el período."""
    con_dato = df.groupby("pais")["co2_mt"].transform("count") > 0
    sin_dato = sorted(df.loc[~con_dato, "pais"].unique())
    _anotar(registro, "Limpieza",
            f"Eliminar países sin datos de CO2 ({', '.join(sin_dato)})",
            (~con_dato).sum(),
            "No aportan información sobre la variable principal del proyecto.")
    return df[con_dato].copy()


def eliminar_duplicados(df, registro):
    """Elimina filas repetidas y revisa identificadores repetidos."""
    dup_filas = int(df.duplicated().sum())
    dup_clave = int(df.duplicated(["pais", "anio"]).sum())
    df = df.drop_duplicates().reset_index(drop=True)
    _anotar(registro, "Limpieza", "Eliminar filas duplicadas", dup_filas,
            "Registro idéntico. No se encontraron en este dataset.")
    _anotar(registro, "Limpieza", "Revisar pares pais-anio repetidos", dup_clave,
            "El par pais-anio debe ser único. No se encontraron repetidos.")
    return df


def _interpolar_brechas_cortas(serie, max_brecha=MAX_BRECHA):
    """Interpola nulos rodeados de datos, si la brecha es corta."""
    if serie.notna().sum() < 2:
        return serie
    interpolada = serie.interpolate(method="linear", limit_area="inside")
    largo_tramo = serie.isna().groupby(serie.notna().cumsum()).transform("sum")
    usar = serie.isna() & interpolada.notna() & (largo_tramo <= max_brecha)
    return serie.where(~usar, interpolada)


def tratar_nulos(df, mundial, registro):
    """Aplica la estrategia de nulos de cada variable."""
    df = df.sort_values(["pais", "anio"]).reset_index(drop=True)
    antes = df.isna().sum()

    # 1. Interpolación de brechas internas cortas en co2 y co2 acumulado.
    for col in ["co2_mt", "co2_acumulado_mt"]:
        nulos_ini = int(df[col].isna().sum())
        df[col] = df.groupby("pais")[col].transform(_interpolar_brechas_cortas)
        llenados = nulos_ini - int(df[col].isna().sum())
        _anotar(registro, "Nulos", f"Interpolar brechas cortas en {col}", llenados,
                f"Brechas internas de hasta {MAX_BRECHA} años entre datos observados.")

    # 2. Recalcular per cápita donde falta y existen co2 y población.
    pc_faltante = (df["co2_per_capita_t"].isna() & df["co2_mt"].notna()
                   & df["poblacion"].notna())
    df.loc[pc_faltante, "co2_per_capita_t"] = (
        df.loc[pc_faltante, "co2_mt"] * 1e6 / df.loc[pc_faltante, "poblacion"])
    _anotar(registro, "Nulos", "Recalcular co2_per_capita_t", pc_faltante.sum(),
            "Razón entre co2 y población, ambas disponibles.")

    # 3. Recalcular la participación mundial con la serie World.
    co2_mundial = df["anio"].map(mundial.set_index("anio")["co2_mt"])
    part_faltante = (df["participacion_mundial_pct"].isna() & df["co2_mt"].notna()
                     & co2_mundial.notna())
    df.loc[part_faltante, "participacion_mundial_pct"] = (
        df.loc[part_faltante, "co2_mt"] / co2_mundial[part_faltante] * 100)
    _anotar(registro, "Nulos", "Recalcular participacion_mundial_pct",
            part_faltante.sum(), "Co2 del país sobre co2 mundial del mismo año.")

    # 4. Población, PIB y variación anual: se mantienen los nulos.
    for col, motivo in [("poblacion", "sin población en la fuente"),
                        ("pib", "sin datos de PIB en la fuente"),
                        ("variacion_anual_pct", "primer año de cada serie")]:
        _anotar(registro, "Nulos", f"Mantener nulos en {col}", df[col].isna().sum(),
                f"Nulo con significado: {motivo}. No se reemplaza por cero ni por promedio.")
    return df


def tabla_nulos(nulos_iniciales, df_final):
    """Tabla variable / nulos iniciales / estrategia / justificación / finales."""
    filas = []
    for original, nuevo in [("country", "pais"), ("year", "anio")] + [
            (k, v) for k, v in RENOMBRAR.items() if k not in ("country", "year")]:
        estrategia, justificacion = ESTRATEGIAS[nuevo]
        filas.append({
            "variable": nuevo,
            "nulos_iniciales": int(nulos_iniciales[original]),
            "estrategia": estrategia,
            "justificacion": justificacion,
            "nulos_finales": int(df_final[nuevo].isna().sum()),
        })
    return pd.DataFrame(filas)

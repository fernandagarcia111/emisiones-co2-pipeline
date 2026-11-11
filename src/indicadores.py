"""Indicadores automatizados para responder la pregunta del proyecto.

Cada indicador se calcula con una función independiente y retorna un
diccionario con nombre, método, resultado, unidad e interpretación.
"""
import numpy as np
import pandas as pd

ANIO_KIOTO = 1997
ANIO_PARIS = 2015
PERIODOS = {
    "pre_kioto": "Antes de Kioto",
    "kioto_a_paris": "Entre Kioto y París",
    "post_paris": "Después de París",
}


def panel_balanceado(df):
    """Países con dato de CO2 en todos los años del análisis.

    Evita que el total cambie solo porque entran países nuevos a la serie.
    """
    anios = df["anio"].nunique()
    con_dato = df.dropna(subset=["co2_mt"]).groupby("pais", observed=True)["anio"].nunique()
    return df[df["pais"].isin(con_dato[con_dato == anios].index)]


def serie_total(df):
    """Emisiones totales por año (Mt) del panel balanceado."""
    return panel_balanceado(df).groupby("anio")["co2_mt"].sum()


def _fila(nombre, metodo, resultado, unidad, interpretacion):
    return {"indicador": nombre, "metodo_calculo": metodo, "resultado": resultado,
            "unidad": unidad, "interpretacion": interpretacion}


def registros_validos(df):
    n = int(df["co2_mt"].notna().sum())
    pct = n / len(df) * 100
    return _fila(
        "Registros válidos de CO2",
        "Filas con co2_mt no nulo sobre el total de filas del dataset limpio",
        round(pct, 1), "%",
        f"{n:,} de {len(df):,} registros país-año tienen dato de emisiones; "
        "el análisis descansa en una base casi completa.".replace(",", "."))


def total_ultimo_anio(df):
    s = serie_total(df)
    ultimo, base = s.index.max(), ANIO_PARIS
    var = (s[ultimo] / s[base] - 1) * 100
    return _fila(
        f"Emisiones totales en {ultimo}",
        "Suma de co2_mt de los países con serie completa (panel balanceado)",
        round(s[ultimo] / 1000, 2), "Gt CO2",
        f"Respecto de {base}, el total varió {var:+.1f}%. "
        "Un valor positivo indica aumento en este conjunto fijo de países.")


def crecimiento_por_periodo(df):
    """Tasa de crecimiento medio anual (CAGR) del total en cada período."""
    s = serie_total(df)
    limites = {"pre_kioto": (s.index.min(), ANIO_KIOTO - 1),
               "kioto_a_paris": (ANIO_KIOTO, ANIO_PARIS - 1),
               "post_paris": (ANIO_PARIS, s.index.max())}
    filas = []
    for clave, (ini, fin) in limites.items():
        cagr = ((s[fin] / s[ini]) ** (1 / (fin - ini)) - 1) * 100
        filas.append(_fila(
            f"Crecimiento medio anual ({PERIODOS[clave]}, {ini}-{fin})",
            "((total_final / total_inicial) ^ (1 / años) - 1) * 100 sobre el total del panel",
            round(cagr, 2), "% por año",
            "Mide qué tan rápido crecen las emisiones totales en el período; "
            "una tasa menor que la del período previo sugiere desaceleración."))
    return filas


def paises_en_descenso(df):
    p = df.pivot_table(index="pais", columns="anio", values="co2_mt", observed=True)
    ultimo = df["anio"].max()
    par = p[[ANIO_PARIS, ultimo]].dropna()
    bajan = int((par[ultimo] < par[ANIO_PARIS]).sum())
    return _fila(
        f"Países con emisiones menores en {ultimo} que en {ANIO_PARIS}",
        "Cuenta de países con co2_mt(último año) < co2_mt(2015), sobre los que tienen ambos datos",
        round(bajan / len(par) * 100, 1), "% de países",
        f"{bajan} de {len(par)} países redujeron sus emisiones tras París; "
        "el resto las aumentó o las mantuvo.")


def mayor_emisor(df):
    ultimo = df["anio"].max()
    d = df[df["anio"] == ultimo].nlargest(1, "co2_mt").iloc[0]
    return _fila(
        f"País con mayores emisiones en {ultimo}",
        "País con el máximo co2_mt del último año y su participación mundial",
        f"{d['pais']} ({d['co2_mt'] / 1000:.2f} Gt; {d['participacion_mundial_pct']:.1f}%)",
        "Gt CO2 y % del mundo",
        "Identifica dónde se concentran las decisiones con mayor efecto sobre el total global.")


def concentracion_top5(df):
    ultimo = df["anio"].max()
    d = df[df["anio"] == ultimo].dropna(subset=["co2_mt"])
    top = d.nlargest(5, "co2_mt")
    pct = top["co2_mt"].sum() / d["co2_mt"].sum() * 100
    nombres = ", ".join(top["pais"].astype(str))
    return _fila(
        f"Concentración de los 5 mayores emisores ({ultimo})",
        "Suma de co2_mt de los 5 países con más emisiones sobre la suma de todos los países",
        round(pct, 1), "% del total",
        f"{nombres} concentran el {pct:.0f}% de las emisiones; "
        "las políticas de pocos países pesan más que las del resto.")


def indicador_chile(df, pais="Chile"):
    ultimo = df["anio"].max()
    a = df[(df["pais"] == pais) & (df["anio"] == ANIO_PARIS)].iloc[0]
    b = df[(df["pais"] == pais) & (df["anio"] == ultimo)].iloc[0]
    v_tot = (b["co2_mt"] / a["co2_mt"] - 1) * 100
    v_pc = (b["co2_per_capita_t"] / a["co2_per_capita_t"] - 1) * 100
    return _fila(
        f"Variación de emisiones de {pais} ({ANIO_PARIS}-{ultimo})",
        "(valor último año / valor 2015 - 1) * 100, para co2_mt y co2_per_capita_t",
        f"Total {v_tot:+.1f}%; per cápita {v_pc:+.1f}%", "% de variación",
        "Permite contrastar el caso nacional con la tendencia global tras el Acuerdo de París.")


def intensidad_carbono(df, ini=2000):
    fin = int(df.loc[df["pib"].notna(), "anio"].max())
    m = df.groupby("anio")["co2_por_pib_kg"].median()
    var = (m[fin] / m[ini] - 1) * 100
    return _fila(
        f"Variación de la intensidad de CO2 por PIB ({ini}-{fin})",
        "Mediana entre países de co2_por_pib_kg en cada año; variación porcentual entre ambos años",
        round(var, 1), "%",
        "La mediana transversal de emisiones por unidad de PIB disminuyó; "
        "no implica por sí sola reducción de emisiones absolutas ni efecto causal de políticas.")


def calcular_indicadores(df):
    """Ejecuta todos los indicadores y retorna una tabla."""
    filas = [registros_validos(df), total_ultimo_anio(df)]
    filas += crecimiento_por_periodo(df)
    filas += [paises_en_descenso(df), mayor_emisor(df), concentracion_top5(df),
              indicador_chile(df), intensidad_carbono(df)]
    return pd.DataFrame(filas)

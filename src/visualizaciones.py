"""Gráficos con Matplotlib/Pyplot. Cada función guarda un PNG y retorna su ruta."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.indicadores import ANIO_KIOTO, ANIO_PARIS, PERIODOS, serie_total

ROJO = "#B01513"
GRIS = "#595959"
COLORES = {"pre_kioto": "#9E9E9E", "kioto_a_paris": "#E08A3C", "post_paris": ROJO}


def _estilo(ax):
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)


def grafico_evolucion_total(df, carpeta):
    """Gráfico 1: evolución de las emisiones totales con los hitos de política."""
    s = serie_total(df) / 1000
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(s.index, s.values, color=ROJO, linewidth=2.2, label="Emisiones totales (países)")
    for anio, texto in [(ANIO_KIOTO, "Protocolo de Kioto (1997)"),
                        (ANIO_PARIS, "Acuerdo de París (2015)")]:
        ax.axvline(anio, color=GRIS, linestyle="--", linewidth=1)
        ax.text(anio - 0.8, s.max() * 0.12, texto, rotation=90, ha="right", va="bottom",
                fontsize=9, color=GRIS)
    ax.set_title("Evolución de las emisiones totales de CO2, 1950-2024", fontsize=13)
    ax.set_xlabel("Año")
    ax.set_ylabel("Emisiones de CO2 (Gt)")
    ax.set_ylim(0, s.max() * 1.1)
    ax.legend(loc="upper left", frameon=False)
    _estilo(ax)
    fig.text(0.01, 0.01, "Fuente: Our World in Data / Global Carbon Project. "
             "Países con serie completa 1950-2024.", fontsize=7.5, color=GRIS)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    ruta = os.path.join(carpeta, "grafico_01.png")
    fig.savefig(ruta, dpi=200)
    plt.close(fig)
    return ruta


def grafico_top_emisores(df, carpeta, n=10):
    """Gráfico 2: ranking de los mayores emisores del último año."""
    ultimo = df["anio"].max()
    d = (df[df["anio"] == ultimo].dropna(subset=["co2_mt"])
         .nlargest(n, "co2_mt").sort_values("co2_mt"))
    fig, ax = plt.subplots(figsize=(9, 5))
    barras = ax.barh(d["pais"].astype(str), d["co2_mt"] / 1000, color=ROJO, label=f"Emisiones {ultimo}")
    for b, pct in zip(barras, d["participacion_mundial_pct"]):
        ax.text(b.get_width() + 0.1, b.get_y() + b.get_height() / 2,
                f"{b.get_width():.2f} Gt ({pct:.1f}%)", va="center", fontsize=8.5)
    ax.set_title(f"Los {n} países con mayores emisiones de CO2 en {ultimo}", fontsize=13)
    ax.set_xlabel("Emisiones de CO2 (Gt)")
    ax.set_ylabel("País")
    ax.set_xlim(0, d["co2_mt"].max() / 1000 * 1.25)
    ax.grid(axis="x", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="lower right", frameon=False)
    fig.text(0.01, 0.01, "Entre paréntesis: participación en las emisiones mundiales. "
             "Fuente: Our World in Data.", fontsize=7.5, color=GRIS)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    ruta = os.path.join(carpeta, "grafico_02.png")
    fig.savefig(ruta, dpi=200)
    plt.close(fig)
    return ruta


def grafico_variacion_por_periodo(df, carpeta):
    """Gráfico 3: distribución de la variación anual de emisiones por período."""
    claves = list(PERIODOS)
    datos = [df.loc[df["periodo_politica"] == k, "variacion_anual_pct"].dropna()
             for k in claves]
    fig, ax = plt.subplots(figsize=(9, 5))
    bp = ax.boxplot(datos, tick_labels=[PERIODOS[k] for k in claves], patch_artist=True,
                    showfliers=False, medianprops={"color": "black", "linewidth": 1.8})
    for caja, k in zip(bp["boxes"], claves):
        caja.set_facecolor(COLORES[k])
        caja.set_alpha(0.8)
    ax.axhline(0, color=GRIS, linestyle="--", linewidth=1, label="Sin variación (0 %)")
    ax.set_title("Variación anual de las emisiones de CO2 por período de política", fontsize=13)
    ax.set_xlabel("Período")
    ax.set_ylabel("Variación anual (%)")
    ax.legend(loc="upper right", frameon=False)
    _estilo(ax)
    fig.text(0.01, 0.01, "Cada observación es un país-año. Los puntos extremos no se dibujan; "
             "la mediana es la línea negra.", fontsize=7.5, color=GRIS)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    ruta = os.path.join(carpeta, "grafico_03.png")
    fig.savefig(ruta, dpi=200)
    plt.close(fig)
    return ruta


def generar_graficos(df, carpeta):
    """Crea y guarda los tres gráficos."""
    os.makedirs(carpeta, exist_ok=True)
    return [grafico_evolucion_total(df, carpeta),
            grafico_top_emisores(df, carpeta),
            grafico_variacion_por_periodo(df, carpeta)]

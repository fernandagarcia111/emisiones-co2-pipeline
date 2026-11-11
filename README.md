# Evolución de emisiones de CO₂

Proyecto Integrador de Programación Avanzada (Ing. Civil Plan Común, Sede Temuco, Universidad Autónoma de Chile). Grupo 6.

**Pregunta orientadora:** ¿las políticas ambientales han influido en la reducción de emisiones de CO₂?

## Estado
- Avance 1: definición del problema, diccionario de datos y carga inicial.
- Avance 2: diagnóstico de calidad, limpieza, tratamiento de nulos, transformaciones y validación. Genera `datos/procesados/dataset_limpio.csv`.
- Avance 3: estadística descriptiva, indicadores automatizados y gráficos con Matplotlib. Genera la carpeta `resultados/`.

## Estructura
```
proyecto/
├── datos/
│   ├── originales/        dataset sin modificar
│   └── procesados/        dataset_limpio.csv y serie_mundial.csv
├── resultados/
│   ├── estadisticas.csv   medidas descriptivas por variable
│   ├── indicadores.csv    indicadores con método, resultado e interpretación
│   └── graficos/          grafico_01.png, grafico_02.png, grafico_03.png
├── reportes/              informes (avance_1, avance_2, avance_3) y registros en CSV
├── src/
│   ├── __init__.py
│   ├── carga.py           lectura e inspección del archivo
│   ├── limpieza.py        nombres, entidades, duplicados y nulos
│   ├── estadisticas.py    estadística descriptiva
│   ├── indicadores.py     indicadores automatizados
│   ├── visualizaciones.py gráficos con Pyplot
│   ├── transformaciones.py conversión de tipos y variables nuevas
│   └── validaciones.py    columnas, tipos, rangos y diagnóstico
├── README.md
├── requirements.txt
└── main.py                ejecuta el pipeline completo
```

## Requisitos
Python 3.10 o superior. Pipeline verificado localmente con el dataset adjunto; instalar las dependencias de requirements.txt.

## Ejecución
```bash
git clone https://github.com/fernandagarcia111/emisiones-co2-pipeline.git
cd emisiones-co2-pipeline
pip install -r requirements.txt
python main.py
```
Debe ejecutarse desde la raíz del proyecto (todas las rutas son relativas).

## Qué hace el pipeline
1. Carga `datos/originales/owid-co2-data.csv`.
2. Diagnóstico: filas, columnas, tipos, nulos, duplicados y valores fuera de rango.
3. Limpieza: renombra columnas, elimina entidades que no son países, filtra desde 1950, revisa duplicados.
4. Tratamiento de nulos: estrategia distinta por variable.
5. Transformaciones: tipos, fecha, década, período de política, unidades y clasificaciones.
6. Validación del dataset final. Si falla, no se exporta.
7. Exportación a `datos/procesados/` y registros a `reportes/`.
8. Estadística descriptiva: `resultados/estadisticas.csv`, `frecuencias_categoricas.csv` y `estadisticas_por_periodo.csv`.
9. Indicadores automatizados: `resultados/indicadores.csv`.
10. Gráficos PNG en `resultados/graficos/`.

El archivo original nunca se modifica: el programa comprueba su huella SHA-256 al inicio y al final.

## Archivos que genera
| Archivo | Contenido |
|---|---|
| `datos/procesados/dataset_limpio.csv` | 16.200 filas y 17 columnas |
| `datos/procesados/serie_mundial.csv` | Serie "World" desde 1950, para referencia |
| `reportes/registro_limpieza.csv` | Cada eliminación o corrección, con su justificación |
| `reportes/tratamiento_nulos.csv` | Nulos iniciales, estrategia y nulos finales por variable |
| `reportes/transformaciones.csv` | Transformaciones aplicadas |
| `reportes/comparacion_antes_despues.csv` | Indicadores antes y después |
| `resultados/estadisticas.csv` | Media, mediana, mínimo, máximo, rango, desviación y cuartiles |
| `resultados/indicadores.csv` | 10 indicadores con método de cálculo e interpretación |
| `resultados/graficos/` | Tres gráficos en PNG |

## Fuente de datos
Our World in Data, basado en el Global Carbon Budget (2025). Licencia CC BY 4.0. Detalles en `datos/README.md`.

## Integrantes
- Fernanda García
- Benjamín Fuentes
- Martín Inostroza
- Martín García

Docente: Alex. Secciones 1 y 2.

## Criterios de análisis y límites
- El archivo limpio contiene 16.200 registros país-año, 216 países y el período 1950–2024.
- Los totales históricos se construyen con 175 países que tienen emisiones observadas en todos los años: son un panel constante y **no equivalen al total mundial completo**.
- El porcentaje de países que disminuyen entre 2015 y 2024 tiene como denominador los países con dato en ambos años (216 en esta versión).
- Las frecuencias de `nivel_per_capita` excluyen 980 valores faltantes: base de 15.220 registros.
- Los hitos Kioto (1997) y París (2015) delimitan períodos descriptivos; la coincidencia temporal no demuestra causalidad de políticas ambientales.
- El gráfico de caja oculta puntos extremos con `showfliers=False`, pero utiliza los valores originales para calcular cuartiles.
- El máximo de variación anual de 1950 se toma de la variable de crecimiento provista por la fuente original y puede reflejar una base anterior a 1950.

## Verificación reproducible
Desde la raíz, ejecutar `python main.py`. Comprobar la presencia de los cuatro CSV de resultados y de `grafico_01.png`, `grafico_02.png` y `grafico_03.png`. La salida comprobada se conserva en `reportes/salida_avance3.txt`.

## Entrega del Avance 3
`reportes/avance_3.pdf` — estadísticas, diez indicadores, tres gráficos, interpretaciones, conclusión y evidencia de ejecución.

**Repositorio de referencia:** https://github.com/fernandagarcia111/emisiones-co2-pipeline

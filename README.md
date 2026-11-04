# Evolución de emisiones de CO₂

Proyecto Integrador de Programación Avanzada (Ing. Civil Plan Común, Sede Temuco, Universidad Autónoma de Chile). Grupo 6.

**Pregunta orientadora:** ¿las políticas ambientales han influido en la reducción de emisiones de CO₂?

## Estado
- Avance 1: definición del problema, diccionario de datos y carga inicial.
- Avance 2: diagnóstico de calidad, limpieza, tratamiento de nulos, transformaciones y validación. Genera `datos/procesados/dataset_limpio.csv`.

## Estructura
```
proyecto/
├── datos/
│   ├── originales/        dataset sin modificar
│   └── procesados/        dataset_limpio.csv y serie_mundial.csv
├── reportes/              informes (avance_1.pdf, avance_2.pdf) y registros en CSV
├── src/
│   ├── __init__.py
│   ├── carga.py           lectura e inspección del archivo
│   ├── limpieza.py        nombres, entidades, duplicados y nulos
│   ├── transformaciones.py conversión de tipos y variables nuevas
│   └── validaciones.py    columnas, tipos, rangos y diagnóstico
├── README.md
├── requirements.txt
└── main.py                ejecuta el pipeline completo
```

## Requisitos
Python 3.9 o superior. Probado con pandas 2.2 y 3.0.

## Ejecución
```bash
git clone <URL_DEL_REPOSITORIO>
cd <carpeta_del_repositorio>
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

## Fuente de datos
Our World in Data, basado en el Global Carbon Budget (2025). Licencia CC BY 4.0. Detalles en `datos/README.md`.

## Integrantes
- Completar con los nombres del equipo.

# Evolución de emisiones de CO₂

Proyecto Integrador de Programación Avanzada (Ing. Civil Plan Común, Sede Temuco, Universidad Autónoma de Chile). Grupo 6.

**Pregunta orientadora:** ¿las políticas ambientales han influido en la reducción de emisiones de CO₂?

## Estado
Avance 1: definición del problema, diccionario de datos, diseño del pipeline y carga inicial con Pandas.

## Estructura
```
proyecto/
├── datos/            dataset y README con su procedencia
├── reportes/         informe del avance (avance_1.pdf)
├── src/
│   ├── __init__.py
│   └── carga.py      carga, validación e inspección
├── .gitignore
├── README.md
├── requirements.txt
└── main.py
```

## Requisitos
Python 3.9 o superior.

## Ejecución
```bash
git clone <URL_DEL_REPOSITORIO>
cd <carpeta_del_repositorio>
pip install -r requirements.txt
python main.py
```
Debe ejecutarse desde la raíz del proyecto. El programa carga `datos/owid-co2-data.csv` y muestra dimensiones, columnas, tipos, nulos, duplicados y resumen estadístico.

## Fuente de datos
Our World in Data, basado en el Global Carbon Budget (2025). Licencia CC BY 4.0. Detalles en `datos/README.md`.

## Integrantes
- Completar con los nombres del equipo.

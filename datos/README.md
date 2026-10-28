# Datos

## Conjunto de datos
**Data on CO2 and Greenhouse Gas Emissions by Our World in Data** (`owid-co2-data.csv`).

- Organización responsable: Our World in Data (OWID).
- Repositorio: https://github.com/owid/co2-data
- Archivo directo: https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv
- Diccionario oficial: https://github.com/owid/co2-data/blob/master/owid-co2-codebook.csv
- Fecha de consulta: 27/10/2026
- Cobertura: 1750 a 2024, 254 países y agregados regionales, 79 variables, 50.411 registros.
- Licencia: Creative Commons BY 4.0 (se permite su redistribución citando la fuente).

## Cómo obtenerlo
El archivo ya está incluido en esta carpeta. Si se necesita actualizar:

```bash
curl -L -o datos/owid-co2-data.csv https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv
```

## Nota
El archivo contiene países y también agregados (World, continentes, grupos de ingreso).
Estos últimos se identifican porque no tienen `iso_code`.

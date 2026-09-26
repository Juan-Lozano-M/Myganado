# Datos reales - Raw

Esta carpeta almacena exclusivamente datos originales provenientes de fuentes reales y documentadas.

## Reglas

- No modificar directamente los archivos originales.
- Guardar la fuente, fecha de consulta y licencia.
- Mantener registros en formato reproducible (.csv, .xlsx, .parquet, etc.).
- Separar claramente entre datos reales, derivados y simulados.

## Estructura esperada

- `raw/`: datos originales tal como se descargaron.
- `cleaned/`: datos con limpieza y validación aplicada.
- `processed/`: datos listos para entrenamiento y validación.

## Nota

Los datasets simulados no deben almacenarse aquí.

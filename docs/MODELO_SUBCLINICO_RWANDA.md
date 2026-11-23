# Modelo exploratorio de mastitis subclínica

## Fuente y objetivo

Se incorporó `ml/data/raw/rwanda_subclinical_mastitis.xlsx`, archivo suplementario S1 del estudio de mastitis en hatos pequeños de Ruanda. El estudio evaluó vacas mediante California Mastitis Test (CMT); registra 411 vacas y distingue resultados positivos y negativos de mastitis subclínica. Fuente: https://doi.org/10.5281/zenodo.17873853. El artículo es de acceso abierto bajo CC BY; conservar la cita y atribución al redistribuir los datos.

El script `ml/scripts/train_subclinical_model.py` asigna CMT positivo a `MEDIO` y CMT negativo a `BAJO`, únicamente dentro de este modelo exploratorio. No hay etiqueta de mastitis clínica grave (`ALTO`) en este conjunto. El archivo procesado y el artefacto quedan separados del modelo clínico existente.

## Entrenamiento y evaluación

- 411 observaciones: 234 positivas (`MEDIO`) y 177 negativas (`BAJO`).
- Predictores: respuestas del cuestionario de manejo y bioseguridad; se excluye la columna objetivo.
- Partición estratificada 75/25, semilla 42.
- Se compararon regresión logística y Random Forest por F1 macro; se seleccionó Random Forest.
- Prueba reservada: exactitud 0,748 y F1 macro 0,734.
- Matriz de confusión, filas reales y columnas predichas en orden `BAJO`, `MEDIO`: `[[27, 17], [9, 50]]`.

La prueba contiene 103 observaciones y es una única partición aleatoria, no validación externa por finca. El desempeño es exploratorio y puede variar con otra partición.

## Límites de uso

Este artefacto predice estado subclínico a partir de variables de encuesta de Ruanda. No usa las variables de medición de la API de My Ganado, no predice `ALTO` y no se integra al endpoint de predicción clínica. `MEDIO` aquí significa CMT positivo/subclínico, no mastitis clínica moderada ni un nivel universal de gravedad. No es diagnóstico veterinario.

Para reproducir:

```powershell
python ml/scripts/train_subclinical_model.py
```

Artefactos generados:

- `ml/data/processed/rwanda_subclinical_mastitis.csv`
- `ml/models/subclinical_mastitis_model.joblib`
- `ml/models/subclinical_mastitis_metrics.json`

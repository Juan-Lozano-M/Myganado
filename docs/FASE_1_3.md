# Fases 1 a 3 - Requisitos, investigación y documentación inicial

## Fase 1 - Definición de requisitos, variables y alcance

### Objetivo

Establecer el alcance funcional del MVP y las variables clave del sistema.

### Entregables

- Alcance del proyecto definido.
- Variables del animal y del ambiente identificadas.
- Reglas de clasificación en BAJO, MEDIO y ALTO.
- Limitaciones del MVP documentadas.

### Criterio de cierre

- El alcance queda registrado y se entiende qué sí y qué no se incluye.
- Se evita la sobreingeniería y se mantiene el enfoque académico.

### Estado

Completado en la documentación base del proyecto y en la trazabilidad.

---

## Fase 2 - Investigación y selección de fuentes de datos reales

### Objetivo

Investigar datasets reales con enfoque en confianza, calidad y relación con bovinos.

### Entregables

- Matriz de fuentes candidatas.
- Evaluación metodológica de cada fuente.
- Decisión de la fuente principal para la semilla de datos.

### Criterio de cierre

- La fuente final queda documentada con justificación técnica y metodológica.

### Estado

Completada para la semilla inicial: dataset de mastitis clínica de Mendeley Data, DOI `10.17632/kbvcdw5b4m.1`, licencia CC BY 4.0. La fuente tiene una etiqueta binaria y no permite inferir una clase intermedia.

---

## Fase 3 - Obtención y documentación de datasets

### Objetivo

Guardar y registrar la información original sin alterar su estado inicial.

### Entregables

- Directorio `ml/data/raw` listo para almacenamiento.
- Fichas de documentación por dataset.
- Separación clara entre datos originales, derivados y simulados.

### Criterio de cierre

- Los datos originales se conservan tal como se obtuvieron.
- La documentación explica origen, variables, uso y limitaciones.

### Estado

En progreso. El original está en `ml/data/raw/cattle_mastitis.csv` y la ficha concreta está documentada. La limpieza se actualizó para mantener `cow_id` como variable de agrupación; se deben regenerar los CSV limpio/procesado y generar el perfil de calidad.

---

## Evidencia actual

Se han dejado los siguientes artefactos:

- [README.md](../README.md)
- [TRAZABILIDAD.md](../TRAZABILIDAD.md)
- [PRODUCT.md](../PRODUCT.md)
- [docs/FUENTES_DATASET.md](FUENTES_DATASET.md)
- [docs/FICHA_DATASET_FINAL.md](FICHA_DATASET_FINAL.md)
- [ml/scripts/profile_data.py](../ml/scripts/profile_data.py)

## Siguiente acción recomendada

Ejecutar `prepare_data.py`, `profile_data.py` y `train_models.py` en el entorno con las dependencias ML instaladas. El nuevo protocolo divide por animal para evitar que mediciones de una misma vaca aparezcan en entrenamiento y evaluación.

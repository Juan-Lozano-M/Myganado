# Selección y documentación de la semilla de datos reales

## Propósito

Establecer la estrategia real para la semilla de datos del modelo de Machine Learning de My Ganado, asegurando que la fuente sea verificable, documentada y apropiada para el problema académico de riesgo bovino.

## Fuente elegida para la semilla inicial

La estrategia recomendada para esta primera versión es usar una combinación documentada de fuentes oficiales y académicas, en lugar de asumir que un único dataset cubre todas las variables del sistema.

### 1) FAOSTAT / FAO

- Tipo: base estadística oficial internacional.
- Uso: contexto agropecuario, producción bovina, indicadores generales de sanidad y producción.
- Fortalezas: fuente institucional confiable, internacionalmente reconocida, accesible y bien documentada.
- Limitaciones: normalmente no contiene datos fisiológicos detallados a nivel la unidad animal.

### 2) ICA (Instituto Colombiano Agropecuario)

- Tipo: fuente institucional nacional.
- Uso: contexto del ganado colombiano, sanidad animal, producción y seguimiento sectorial.
- Fortalezas: muy relevante para el contexto local y la validación del proyecto.
- Limitaciones: puede requerir integración y normalización para adaptarlo a un dataset de modelado.

### 3) Repositorios académicos (Zenodo, Mendeley, universidades, Datasets científicos)

- Tipo: datos de investigación pública.
- Uso: variables fisiológicas, comportamentales o de salud animal que permitan completar el semillero real.
- Fortalezas: más cercanos al objetivo del sistema y útiles para construir una variable objetivo derivada.
- Limitaciones: requieren validación de metodología, número de registros y calidad de variables.

## Justificación de la estrategia

El proyecto no exige que todos los atributos de My Ganado existan en un único conjunto de datos. La propuesta es técnicamente y metodológicamente defensible porque:

- se separa claramente entre datos originales y datos derivados,
- se usa información real y verificable,
- se integran fuentes cuando una sola base no alcanza el objetivo,
- la variable objetivo puede ser derivada si la fuente original no define directamente riesgo,
- la semilla real se conserva como base del modelo, mientras que los datos simulados se usan para pruebas funcionales y demostración.

## Reglas para la integración

La integración debe cumplirse con:

- identificación de cada fuente,
- revisión de licencia y metodología,
- limpieza y conversión de unidades,
- eliminación de duplicados,
- tratamiento de valores faltantes,
- normalización y codificación de variables,
- separación de dataset original, limpio y procesado.

## Variable objetivo

La clasificación final del modelo será:

- BAJO
- MEDIO
- ALTO

Dado que un único dataset real no siempre incluye directamente esas categorías, se prioriza una estrategia documentada de variable objetivo derivada con base en indicadores fisiológicos, ambientales y de comportamiento, de forma explícita y no como una medición original.

## Documentación requerida por dataset

Para cada fuente real se registrará una ficha con:

- nombre,
- fuente,
- autor o institución,
- URL,
- fecha de consulta,
- licencia,
- número de registros,
- variables,
- unidades,
- variables utilizadas,
- variables descartadas,
- problemas detectados,
- proceso de limpieza,
- transformaciones realizadas,
- limitaciones.

## Estado actual

- La estrategia de fuente real quedó definida.
- Se continúa con la documentación de la ficha específica de la semilla de datos.
- La estructura de almacenamiento ya quedó preparada en `ml/data/`.

## Siguiente paso

Documentar la ficha final de la fuente elegida y dejarla lista para su descarga y limpieza en la carpeta `ml/data/raw/`.

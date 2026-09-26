# Ficha del dataset base para My Ganado

## 1. Nombre

Semilla real de datos bovinos para riesgo ganadero y monitoreo ambiental

## 2. Fuente principal

Estrategia recomendada para la primera versión:

- Instituto Colombiano Agropecuario (ICA)
- FAOSTAT / FAO
- Datos científicos públicos y verificables complementarios

## 3. Justificación metodológica

La primera versión del proyecto no exige que todas las variables del sistema se encuentren en un único dataset. La estrategia seleccionada consiste en construir una semilla real y documentada a partir de fuentes oficiales y académicas que aporten contexto productivo, sanitario y ambiental del ganado bovino.

Esto es compatible con el alcance del proyecto porque:

- evita inventar datos como si fueran reales,
- permite diferenciar datos originales, derivados y simulados,
- respeta el principio de trazabilidad,
- facilita la construcción de una variable objetivo derivada con metodología explícita.

## 4. Autor o institución

- Instituto Colombiano Agropecuario (ICA)
- Organizacion de las Naciones Unidas para la Agricultura y la Alimentación (FAO)
- Repositorios de investigación y universidades con datasets de bovinos verificados

## 5. URL base

- https://www.ica.gov.co/
- https://www.fao.org/faostat/
- Repositorios científicos y de datos abiertos con dataset verificable

## 6. Fecha de consulta

Por definir durante la descarga final de la semilla.

## 7. Licencia

- Las fuentes oficiales de ICA y FAO suelen disponer de condiciones administrativas y de uso público.
- Los datasets científicos deben revisarse caso por caso para verificar licencia o términos de uso.

## 8. Número de registros

Se estiman valores variables. La cantidad final dependerá del dataset elegido y del proceso de limpieza.

## 9. Variables esperadas

Se priorizarán variables relacionadas con:

- identificación o tipo de bovino,
- edad o categoría animal,
- peso,
- indicadores de salud,
- temperatura y comportamiento si existen en la fuente,
- condiciones ambientales o de manejo,
- producción y sanidad general.

## 10. Unidades de medida

- edad: meses o años,
- peso: kg,
- temperatura: °C,
- humedad: %,
- temperatura ambiental: °C,
- consumo de agua y alimento: L o kg según la fuente,
- actividad: unidades o indicadores derivados según el dataset.

## 11. Variables utilizadas

Las variables usadas en la semilla final serán únicamente las que cumplan con:

- calidad de datos,
- consistencia entre registros,
- relación directa con el problema de riesgo ganadero,
- posibilidad de transformación para la variable objetivo.

## 12. Variables descartadas

Se descartarán las columnas que:

- no aporten información al problema,
- estén duplicadas,
- presenten demasiados faltantes,
- no tengan una documentación clara,
- no puedan convertirse a un formato útil para el modelo.

## 13. Problemas esperados

- datos parciales o incompletos,
- formatos heterogéneos,
- falta de variable objetivo directa,
- desbalance de clases,
- datos no completamente alineados con las variables del MVP.

## 14. Proceso de limpieza

- validación de la fuente,
- normalización de columnas,
- eliminación de duplicados,
- tratamiento de valores faltantes,
- detección de inconsistencias,
- detección de atípicos,
- conversión de unidades,
- codificación de variables categóricas,
- normalización de atributos numéricos,
- división train/test.

## 15. Transformaciones realizadas

Se aplicarán transformaciones documentadas como:

- renombrado de columnas,
- conversión de texto a categorías,
- imputación de faltantes,
- cálculo de indicadores derivados,
- construcción de la variable objetivo derivada cuando haga falta.

## 16. Limitaciones

- no necesariamente se tendrá una variable exacta de riesgo en la fuente original,
- puede haber sesgos por región o sistema de producción,
- algunos datos serán contextuales y no fisiológicos directos,
- la clasificación de riesgo será una aproximación administrativa/analítica y no un diagnóstico veterinario.

## 17. Estado actual

- Fuente base seleccionada en principio: ICA + FAOSTAT + datos científicos complementarios.
- Pendiente descarga y validación final.
- La documentación base del proyecto ya quedó definida y trazada.

## 18. Siguiente paso

Descar la fuente concreta, dejarla en `ml/data/raw/` y documentar la ficha final con número real de registros, variables exactas y resultados de limpieza.

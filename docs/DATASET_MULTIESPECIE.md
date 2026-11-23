# Fuente secundaria de salud multiespecie

## Fuente

Lane, J.; Vidal, G.; Smith, W.; Jackson, W.; Fentie, T.; Kebede, N. *LSIL Ethiopia Young Stock Mortality Animal Health and Disease Surveillance Data*. Harvard Dataverse, V1, publicado el 25 de mayo de 2022. DOI: [10.7910/DVN/E6EV2K](https://doi.org/10.7910/DVN/E6EV2K). Dataverse indica licencia CC0 1.0.

El registro describe encuestas, examen físico y vigilancia de salud en 1.480 animales jóvenes (terneros, corderos y cabritos) de Etiopía, entre noviembre de 2017 y mayo de 2019. Incluye raza, sexo, edad, hallazgos físicos, manejo y pruebas diagnósticas para patógenos entéricos y respiratorios; no todos los resultados están disponibles para cada animal.

## Integración en My Ganado

- Archivo tabular preservado: `ml/data/raw/young_stock/YSM_Animal_Health_Data.tab`.
- Hash local SHA-256: `ADD36A5235EAA90514B55D92F56DF09213C3C61A16ED471716917B73D96F1241`.
- Preparación independiente: `ml/scripts/prepare_young_stock.py`.
- Salida limpia generada: `ml/data/cleaned/young_stock/young_stock_health_cleaned.csv`.
- Perfil generado: `ml/data/processed/young_stock/young_stock_profile.json`.

La copia descargada tiene 1.480 filas y 146 columnas, sin filas exactamente duplicadas. `Species` contiene 300 valores `Bovine`, 97 `lamb`, 44 `goat kid` y 1.039 vacíos. Hay 105.447 celdas vacías y tres temperaturas rectales fuera del rango exploratorio de revisión (28.4, 369.1 y 3838); se conservan y se señalan sin corregirlas automáticamente. No se imputará la especie ni se asignará una etiqueta única BAJO/MEDIO/ALTO: los resultados clínicos son variables distintas y dispersas, por lo que se deben escoger objetivos específicos con asesoría veterinaria y con el libro de códigos de la fuente.

Esta fuente se conserva separada del dataset de mastitis bovina. Sus animales jóvenes, regiones, enfermedades, protocolos y variables no son equivalentes a las mediciones de ubre del dataset original de My Ganado. Puede respaldar un módulo exploratorio multiespecie, pero todavía no un modelo integrado ni una predicción clínica desplegada.

## Referencias

- [Registro de Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/E6EV2K)
- [Descripción y alcance de la fuente en Lanfrica](https://lanfrica.com/en/record/lsil-ethiopia-young-stock-mortality-animal-health-and-disease-surveillance-data)

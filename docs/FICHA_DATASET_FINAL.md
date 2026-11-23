# Ficha del dataset usado en el prototipo

## Identificación y procedencia

- **Nombre:** Clinical Mastitis in Cows based on Udder Parameter using Internet of Things (IoT).
- **Autores:** K. Ankitha, D. H. Manjaiah y M. Kartik.
- **Repositorio:** [Mendeley Data, versión 1](https://data.mendeley.com/datasets/kbvcdw5b4m/1).
- **DOI:** `10.17632/kbvcdw5b4m.1`.
- **Licencia indicada por el repositorio:** CC BY 4.0.
- **Fecha de publicación:** 22 de octubre de 2020.
- **Fecha de consulta y perfil local:** 24 de octubre de 2026.

La ficha de Mendeley describe mediciones de cuatro cuadrantes de la ubre, temperatura y señales asociadas a mastitis clínica. La etiqueta fuente es binaria: normal (`0`) y mastitis (`1`). Por tanto, `risk_level` en este proyecto es una recodificación de la etiqueta clínica original (`BAJO`/`ALTO`), no un diagnóstico ni una variable de tres niveles.

## Archivos locales y resumen observado

- Original: `ml/data/raw/cattle_mastitis.csv`.
- Limpio y procesado: `ml/data/cleaned/` y `ml/data/processed/`.
- Perfil reproducible: `ml/scripts/profile_data.py` genera `docs/DATASET_PROFILE.md`.
- El CSV original local contiene 6.600 filas, 18 columnas, 1.100 identificadores de animal y ninguna celda vacía observada.
- Distribución de etiqueta fuente: 5.490 normales (`0`, 83,18 %) y 1.110 con mastitis (`1`, 16,82 %).
- El perfil debe volver a generarse después de preparar los archivos para reflejar la conservación de `cow_id` y los duplicados bajo ambos criterios.

Las filas repetidas por animal no son observaciones independientes. La preparación conserva `cow_id` para dividir entrenamiento y evaluación por animal, pero lo excluye como atributo predictivo. Si un dataset procesado no contiene `cow_id`, el script informa que utiliza una división por filas, que puede sobrestimar el rendimiento por fuga entre mediciones del mismo animal.

## Variables

Las columnas disponibles incluyen identificador de vaca, día, raza, meses desde el parto, historial de mastitis, límites de inspiración y espiración de los cuatro cuadrantes, temperatura, dureza, dolor, visibilidad de leche y etiqueta binaria. La fuente documenta medidas del sensor de ubre, pero las unidades y condiciones de medición deben verificarse en el artículo asociado antes de interpretarlas como rangos fisiológicos universales.

## Transformaciones reproducibles

`ml/scripts/prepare_data.py` renombra columnas, transforma `class1` a `risk_level`, elimina duplicados exactos incluyendo el identificador y conserva `cow_id` para la partición por grupos. El CSV original bajo `raw/` no se modifica. El entrenamiento procesa las variables en un pipeline de scikit-learn y deja fuera el identificador.

Ejecutar desde la raíz:

```powershell
python ml/scripts/prepare_data.py
python ml/scripts/profile_data.py
python ml/scripts/train_models.py
```

## Limitaciones

- Es un conjunto específico de mastitis clínica, no una muestra representativa de todas las enfermedades bovinas, fincas, razas o zonas de Colombia.
- La etiqueta solo admite dos clases. No hay respaldo para inventar una clase `MEDIO`; cualquier extensión requiere datos y metodología independientes y explícitos.
- La etiqueta de mastitis es el objetivo del dataset fuente; mapearla a BAJO/ALTO no convierte el modelo en diagnóstico veterinario.
- Algunas variables de entrada de la API son simuladas y deben coincidir en definición, unidades y distribución con las usadas en el entrenamiento.
- Una partición por animal es necesaria para evaluar generalización a animales no vistos. Los resultados de una división aleatoria por filas no deben reportarse como validación independiente.

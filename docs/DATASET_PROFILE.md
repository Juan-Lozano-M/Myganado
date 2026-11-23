# Perfil de calidad del dataset

Generado por `ml/scripts/profile_data.py`. Los rangos son descriptivos y no representan umbrales clínicos.

## Datos originales

```json
{
  "rows": 6600,
  "columns": 18,
  "missing_cells": 0,
  "duplicate_rows": 0,
  "classes": {
    "0": 5490,
    "1": 1110
  },
  "numeric_ranges": {
    "Day": {
      "min": 1.0,
      "max": 6.0
    },
    "Months after giving birth": {
      "min": 1.0,
      "max": 6.0
    },
    "Previous_Mastits_status": {
      "min": 0.0,
      "max": 1.0
    },
    "IUFL": {
      "min": 130.0,
      "max": 322.0
    },
    "EUFL": {
      "min": 152.0,
      "max": 372.0
    },
    "IUFR": {
      "min": 130.0,
      "max": 343.0
    },
    "EUFR": {
      "min": 151.0,
      "max": 393.0
    },
    "IURL": {
      "min": 130.0,
      "max": 327.0
    },
    "EURL": {
      "min": 152.0,
      "max": 367.0
    },
    "IURR": {
      "min": 121.0,
      "max": 315.0
    },
    "EURR": {
      "min": 151.0,
      "max": 360.0
    },
    "Temperature": {
      "min": 24.0,
      "max": 58.0
    },
    "Hardness": {
      "min": 0.0,
      "max": 1.0
    },
    "Pain": {
      "min": 0.0,
      "max": 1.0
    },
    "Milk_visibility": {
      "min": 0.0,
      "max": 1.0
    },
    "class1": {
      "min": 0.0,
      "max": 1.0
    }
  },
  "class_percentages": {
    "0": 83.18,
    "1": 16.82
  }
}
```

## Datos limpios

```json
{
  "rows": 6600,
  "columns": 18,
  "missing_cells": 0,
  "duplicate_rows": 0,
  "classes": {
    "BAJO": 5490,
    "ALTO": 1110
  },
  "animals": 1100,
  "duplicate_rows_without_animal_id": 583,
  "breeds": {
    "Jersey": 6498,
    "hostlene": 102
  },
  "numeric_ranges": {
    "day": {
      "min": 1.0,
      "max": 6.0
    },
    "months_after_giving_birth": {
      "min": 1.0,
      "max": 6.0
    },
    "previous_mastitis_status": {
      "min": 0.0,
      "max": 1.0
    },
    "iu_fl": {
      "min": 130.0,
      "max": 322.0
    },
    "eu_fl": {
      "min": 152.0,
      "max": 372.0
    },
    "iu_fr": {
      "min": 130.0,
      "max": 343.0
    },
    "eu_fr": {
      "min": 151.0,
      "max": 393.0
    },
    "iu_rl": {
      "min": 130.0,
      "max": 327.0
    },
    "eu_rl": {
      "min": 152.0,
      "max": 367.0
    },
    "iu_rr": {
      "min": 121.0,
      "max": 315.0
    },
    "eu_rr": {
      "min": 151.0,
      "max": 360.0
    },
    "temperature": {
      "min": 24.0,
      "max": 58.0
    },
    "hardness": {
      "min": 0.0,
      "max": 1.0
    },
    "pain": {
      "min": 0.0,
      "max": 1.0
    },
    "milk_visibility": {
      "min": 0.0,
      "max": 1.0
    }
  },
  "class_percentages": {
    "BAJO": 83.18,
    "ALTO": 16.82
  }
}
```

## Interpretación y límites

La etiqueta original es binaria (`0` normal, `1` mastitis) y se transforma en `BAJO`/`ALTO`; no hay clase `MEDIO`. Las mediciones repetidas por animal deben permanecer agrupadas al evaluar modelos. El identificador se conserva para esa partición y se excluye de las variables predictoras. La detección de duplicados se informa tanto con como sin `cow_id`, porque quitarlo puede hacer equivalentes observaciones de animales distintos. El dataset describe mastitis clínica y no representa por sí solo todas las enfermedades ni las condiciones ambientales del producto.

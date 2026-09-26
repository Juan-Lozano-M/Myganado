# My Ganado

## Proyecto académico

Sistema inteligente de monitoreo ganadero para pequeños y medianos productores, desarrollado como MVP con enfoque en Machine Learning, simulación de sensores y alertas de seguimiento.

## Objetivo general

Desarrollar un prototipo funcional para registrar animales bovinos, simular lecturas fisiológicas y ambientales, aplicar Machine Learning supervisado para estimar nivel de riesgo y generar alertas para propietario y veterinario cuando corresponda.

## Fases iniciales del proyecto

### Fase 1 - Definición de requisitos, variables y alcance

- Requisitos funcionales y no funcionales definidos.
- Variables del animal y del ambiente identificadas.
- Alcance del MVP y limitaciones documentados.

### Fase 2 - Investigación y selección de fuentes de datos reales

- Investigación de datasets reales relacionados con bovinos y salud animal.
- Evaluación de fuente, metodología, calidad de datos, licencia y relación con el objetivo.
- Selección de una semilla real y documentada para modelado.

### Fase 3 - Obtención y documentación de datasets

- Descarga y control de los datos originales.
- Documentación de la fuente, variables y limitaciones.
- Preparación de la estructura de almacenamiento para data raw/cleaned/processed.

## Estructura propuesta del repositorio

```text
my-ganado/
├── README.md
├── PRODUCT.md
├── TRAZABILIDAD.md
├── .github/
│   └── skills/
│       └── impeccable/
├── backend/
│   └── app/
│       ├── api/
│       ├── models/
│       ├── services/
│       └── ...
├── frontend/
├── ml/
│   ├── data/
│   │   ├── raw/
│   │   ├── cleaned/
│   │   └── processed/
│   ├── notebooks/
│   ├── scripts/
│   └── models/
├── docs/
├── database/
├── docker-compose.yml
└── .impeccable/
```

## Estado actual

- Fase 1: completada en la documentación base del proyecto.
- Fase 2: iniciada con investigación de datasets reales.
- Fase 3: iniciada con estructura de almacenamiento y documentación de datos.
- Dashboard inicial: disponible en `frontend/`, conectado a animales, alertas y simulaciones de la API.

## Siguientes pasos

1. Definir la fuente real final para ML.
2. Registrar la ficha técnica del dataset.
3. Crear scripts y notebooks de limpieza.
4. Preparar el primer pipeline de entrenamiento.
5. Completar vistas de historial, alertas y flujo integral del dashboard.

## Nota metodológica

Este proyecto se centra en un enfoque académico, con separación explícita entre:

- datos reales,
- datos derivadas,
- datos simulados,
- y variables de riesgo documentadas.

No se debe presentar la simulación como diagnóstico veterinario ni como una fuente real de entrenamiento.

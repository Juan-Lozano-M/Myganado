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
- Fase 2: fuente Mendeley Data documentada con DOI y licencia.
- Fase 3: dataset original y ficha disponibles; limpieza actualizada para conservar ID de animal, falta regenerar los artefactos procesados.
- Fuente secundaria multiespecie añadida en `ml/data/raw/young_stock/` (terneros, corderos y cabritos); permanece aislada del modelo bovino y tiene perfil y copia limpia propios.
- Backend y dashboard inicial: disponibles y conectados para registrar animales, guardar simulaciones asociadas, consultar alertas y revisar historial.
- Política de alertas: `BAJO` no genera alerta activa; `MEDIO` alerta al propietario y escala tras tres eventos consecutivos; `ALTO` escala a propietario y veterinario.

## Siguientes pasos

1. Resolver la definición de la clase `MEDIO` y reentrenar el modelo si corresponde.
2. Implementar el adaptador de notificaciones y registrar sus estados.
3. Añadir pruebas automatizadas de validación y flujo integral.
4. Preparar Docker Compose y la migración a PostgreSQL.
5. Completar métricas, gráficas históricas y evidencia de demostración.

## Ejecución con Docker

Con Docker Compose instalado, desde la raíz del repositorio:

```powershell
docker compose up --build
```

El dashboard queda disponible en `http://localhost:8080`; la API y la base SQLite se ejecutan en contenedores y los datos persisten en el volumen `myganado_data`. Para detener los servicios conserva los datos con `docker compose down`.

## Nota metodológica

Este proyecto se centra en un enfoque académico, con separación explícita entre:

- datos reales,
- datos derivadas,
- datos simulados,
- y variables de riesgo documentadas.

No se debe presentar la simulación como diagnóstico veterinario ni como una fuente real de entrenamiento.

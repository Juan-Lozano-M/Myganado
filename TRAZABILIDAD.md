# My Ganado - Trazabilidad del proyecto

**Asignatura:** Aprendizaje Automático  
**Institución:** Universidad del Tolima  
**Versión:** 0.1  
**Fecha de creación:** 2026-09-25  
**Estado general:** Pendiente de iniciar

## 1. Propósito del documento

Este documento centraliza la trazabilidad del MVP de **My Ganado**: relaciona objetivos, requisitos, componentes, datos, fases de desarrollo, pruebas y evidencias. Debe actualizarse cada vez que un requisito cambie de estado o se genere un entregable.

La trazabilidad debe permitir responder:

- Qué se quiere construir.
- Por qué se necesita cada funcionalidad.
- En qué componente se implementará.
- Cómo se verificará.
- Qué evidencia demuestra que está terminada.

## 2. Objetivo y límites

### Objetivo general

Construir un prototipo funcional que registre bovinos, simule lecturas de sensores, estime un nivel de riesgo mediante Machine Learning supervisado y genere alertas de seguimiento para el propietario y, cuando corresponda, para el veterinario.

### Clasificación inicial

- `BAJO`
- `MEDIO`
- `ALTO`

> El sistema es una herramienta de apoyo para seguimiento. No realiza diagnóstico veterinario ni prescribe tratamientos.

### Incluido en el MVP

- Registro de animales y mediciones.
- Variables fisiológicas, de comportamiento y ambientales.
- Dataset real documentado y separado de los datos simulados.
- Limpieza, preparación, entrenamiento y evaluación de modelos.
- Simuladores de animal, ambiente y sensores virtuales.
- API REST con FastAPI.
- Persistencia en PostgreSQL.
- Dashboard React con historial y alertas.
- Predicciones, alertas, notificaciones y escalamiento.
- Pruebas funcionales, de integración y de escenarios.
- Docker Compose para ejecución local.

### Fuera del MVP

- Cámaras y visión artificial.
- Sensores físicos, ESP32 o Arduino.
- Diagnóstico veterinario.
- Automatización de tratamientos o medicamentos.
- Integración obligatoria con hardware real.
- WhatsApp, Twilio o SMS.

## 3. Convenciones de seguimiento

### Estados

- `Pendiente`: todavía no iniciado.
- `En progreso`: trabajo activo.
- `Bloqueado`: depende de una decisión, fuente o recurso pendiente.
- `En revisión`: implementado, pero falta validar o documentar.
- `Completado`: validado y con evidencia registrada.
- `Descartado`: eliminado del alcance con justificación.

### Prioridades

- `P0`: indispensable para demostrar el flujo completo del MVP.
- `P1`: necesario para completar el MVP, pero no bloquea el primer prototipo.
- `P2`: mejora o preparación futura.

### Formato de evidencia

Cada requisito completado debe enlazar o indicar al menos una evidencia:

- Código o módulo implementado.
- Notebook, script o modelo entrenado.
- Dataset y ficha de procedencia.
- Captura o video de demostración.
- Resultado de prueba.
- Documento técnico.

## 4. Requisitos trazables

| ID      | Requisito                                                                        | Prioridad | Componente                    |     Fase | Criterio de aceptación                                                                                           | Estado    | Evidencia |
| ------- | -------------------------------------------------------------------------------- | --------: | ----------------------------- | -------: | ---------------------------------------------------------------------------------------------------------------- | --------- | --------- |
| REQ-001 | Registrar animales bovinos con identificador, raza, edad, peso y propietario.    |        P0 | Backend / BD / Frontend       |    10-11 | Se puede crear, listar y consultar un animal desde la interfaz o API.                                            | Completado | `POST/GET /api/v1/animals`, SQLite |
| REQ-002 | Registrar mediciones fisiológicas, de comportamiento y fecha/hora.               |        P0 | Backend / BD                  |       10 | Una medición válida queda almacenada y asociada a un animal.                                                     | Completado | `POST /api/v1/animals/{animal_id}/measurements` |
| REQ-003 | Registrar condiciones ambientales.                                               |        P0 | Backend / BD / Simulador      |     9-10 | Temperatura, humedad, hora y disponibilidad quedan asociadas a la medición.                                      | Pendiente | -         |
| REQ-004 | Consultar el historial de un animal.                                             |        P0 | Backend / Frontend            |       16 | El historial muestra mediciones, ambiente, predicciones y alertas ordenados por fecha.                           | Completado | `GET /api/v1/animals/{animal_id}/history`; prueba aislada |
| REQ-005 | Seleccionar y documentar una fuente de datos reales relacionada con bovinos.     |        P0 | ML / Documentación            |      2-3 | Existe una ficha con autor, institución, URL, licencia, variables, unidades y limitaciones.                      | En progreso | `docs/FICHA_DATASET_FINAL.md`, Mendeley Data |
| REQ-006 | Conservar los datos originales sin modificarlos.                                 |        P0 | ML / Datos                    |      3-4 | Los datos originales están en `ml/data/raw/` y son distinguibles de los procesados.                              | Completado | `ml/data/raw/cattle_mastitis.csv` |
| REQ-007 | Construir un dataset limpio mediante un proceso reproducible.                    |        P0 | ML                            |        4 | Se documentan formatos, duplicados, faltantes, inconsistencias, atípicos, unidades y codificación.               | Completado | `ml/scripts/prepare_data.py`, `ml/data/cleaned/` |
| REQ-008 | Diferenciar datos originales, derivados y simulados.                             |        P0 | ML / Documentación            |      4-8 | La documentación y los archivos identifican el origen de cada variable.                                          | Pendiente | -         |
| REQ-009 | Definir la variable objetivo con respaldo metodológico.                          |        P0 | ML / Documentación            |      4-7 | La clase proviene del dataset o se declara como objetivo derivado con justificación técnica.                     | Completado | `risk_level` deriva de `class1`; `ml/scripts/prepare_data.py` |
| REQ-010 | Evaluar la calidad y representatividad de la semilla de datos.                   |        P0 | ML                            |        5 | Se reportan registros, clases, faltantes, duplicados, rangos, desbalance, razas y edades disponibles.            | Pendiente | -         |
| REQ-011 | Entrenar Random Forest, Decision Tree y Logistic Regression.                     |        P0 | ML                            |        6 | Los tres modelos se entrenan con el mismo protocolo y partición reproducible.                                    | Completado | `ml/scripts/train_models.py`, salida de entrenamiento |
| REQ-012 | Comparar modelos usando métricas apropiadas.                                     |        P0 | ML                            |        7 | Se reportan accuracy, precision, recall, F1-score y matriz de confusión por modelo.                              | Completado | Salida de entrenamiento: accuracy y F1 = 1.0000 en los tres modelos |
| REQ-013 | Seleccionar el modelo con base en resultados experimentales.                     |        P0 | ML / Backend                  |   7 / 12 | La selección está documentada y el modelo exportado es el evaluado.                                              | Completado | `ml/models/risk_model.joblib`, Random Forest |
| REQ-014 | Generar datos simulados plausibles y no puramente aleatorios.                    |        P0 | Simulador                     |      8-9 | Las lecturas respetan rangos, reglas y relaciones entre ambiente y animal.                                       | Completado | `backend/app/services/simulator.py` |
| REQ-015 | Simular escenarios normal, estrés ambiental, posible riesgo, alto y persistente. |        P0 | Simulador / Pruebas           | 8-9 / 17 | Cada escenario produce condiciones esperadas y reproducibles mediante una semilla configurable.                  | Completado | `POST /api/v1/simulations`; escenarios normal y alto validados |
| REQ-016 | Permitir sustituir el simulador por sensores IoT en el futuro.                   |        P1 | Arquitectura / Backend        |  10 / 18 | La entrada de mediciones utiliza una interfaz o contrato independiente del origen de los datos.                  | Pendiente | -         |
| REQ-017 | Exponer una API REST con FastAPI y Pydantic.                                     |        P0 | Backend                       |  10 / 12 | La API valida solicitudes y publica los endpoints definidos en la documentación OpenAPI.                         | Completado | `backend/app/main.py`, `GET /health` |
| REQ-018 | Implementar predicción de riesgo para `BAJO`, `MEDIO` y `ALTO`.                  |        P0 | Backend / ML                  |       12 | Una medición válida devuelve clase, probabilidad y fecha/hora, sin presentarse como diagnóstico.                 | En progreso | `POST /api/v1/predictions`; semilla actual produce BAJO/ALTO |
| REQ-019 | Persistir predicciones y sus probabilidades.                                     |        P0 | Backend / BD                  |  12 / 16 | Cada predicción queda asociada a animal y medición.                                                              | Completado | Tabla `predictions`; prueba con `prediction_id=1` |
| REQ-020 | Generar alertas según el nivel de riesgo.                                        |        P0 | Backend                       |       13 | `BAJO` registra; `MEDIO` alerta y notifica al propietario; `ALTO` alerta y notifica a propietario y veterinario. | En progreso | `GET /api/v1/alerts`; riesgo ALTO queda `pendiente_notificacion` |
| REQ-021 | Detectar persistencia configurable del riesgo medio.                             |        P0 | Backend / BD                  |       15 | Tras el número o periodo configurado de eventos medios, se crea un escalamiento.                                 | Pendiente | -         |
| REQ-022 | Registrar notificaciones y estados de envío.                                     |        P0 | Backend / Notificaciones / BD |    14-15 | Cada notificación registra destinatario, tipo, estado y fecha/hora.                                              | Pendiente | -         |
| REQ-023 | Enviar notificaciones por correo electrónico.                                    |        P1 | Notificaciones                |    14-15 | El sistema intenta el envío y conserva éxito o error sin perder la alerta.                                       | Pendiente | -         |
| REQ-024 | Mostrar dashboard operativo.                                                     |        P0 | Frontend                      |       11 | Se visualizan cantidad de animales, animales en riesgo, última medición, ambiente y alertas.                     | En progreso | `frontend/index.html`, dashboard conectado a API |
| REQ-025 | Mostrar detalle y evolución histórica de un animal.                              |        P0 | Frontend / Recharts           |  11 / 16 | Se muestran variables, riesgo, alertas y gráficas históricas sin mezclar animales.                               | Pendiente | -         |
| REQ-026 | Validar datos faltantes, fuera de rango y errores de servicios.                  |        P0 | Backend / ML / Pruebas        |   4 / 17 | El sistema responde con errores controlados y no almacena datos inválidos como mediciones válidas.               | Pendiente | -         |
| REQ-027 | Ejecutar el sistema localmente con Docker Compose.                               |        P1 | Infraestructura               |       18 | Frontend, backend y PostgreSQL arrancan con instrucciones reproducibles.                                         | Pendiente | -         |
| REQ-028 | Probar el flujo completo de demostración.                                        |        P0 | Integración                   |       18 | Animal → simulación → API → predicción → alerta → notificación → persistencia → historial.                       | Pendiente | -         |
| REQ-029 | Documentar limitaciones, riesgos y uso no diagnóstico.                           |        P0 | Documentación                 |       19 | README y documentos ML explican alcance, calidad de datos y límites del modelo.                                  | Pendiente | -         |

## 5. Trazabilidad de objetivos a requisitos

| Objetivo                             | Requisitos relacionados            | Evidencia esperada                                                              |
| ------------------------------------ | ---------------------------------- | ------------------------------------------------------------------------------- |
| Monitorear animales bovinos          | REQ-001, REQ-002, REQ-003, REQ-004 | API, tablas, dashboard e historial funcionales.                                 |
| Usar una semilla real para ML        | REQ-005 a REQ-010                  | Ficha de dataset, datos raw/cleaned/processed y notebook reproducible.          |
| Clasificar riesgo con ML             | REQ-011, REQ-012, REQ-013, REQ-018 | Comparación de modelos, métricas, modelo seleccionado y endpoint de predicción. |
| Simular sensores de manera plausible | REQ-014, REQ-015, REQ-016          | Código del simulador, escenarios y pruebas de entradas.                         |
| Gestionar alertas y seguimiento      | REQ-019 a REQ-023                  | Registros de alertas, notificaciones, persistencia y escalamiento.              |
| Entregar una experiencia usable      | REQ-024, REQ-025                   | Dashboard y vista individual operativos.                                        |
| Mantener calidad y reproducibilidad  | REQ-026, REQ-027, REQ-028, REQ-029 | Pruebas, Docker Compose, documentación y evidencia de ejecución.                |

## 6. Plan por fases y entregables

| Fase | Actividad                                         | Entregable                                                 | Requisitos                                  | Estado    |
| ---: | ------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------- | --------- |
|    1 | Definir alcance, variables y criterios de riesgo. | Documento de requisitos aprobado.                          | Todos                                       | Pendiente |
|    2 | Investigar fuentes reales.                        | Matriz de fuentes candidatas y decisión justificada.       | REQ-005                                     | Pendiente |
|    3 | Descargar y documentar datasets.                  | `ml/data/raw/` y fichas de datasets.                       | REQ-005, REQ-006                            | Pendiente |
|    4 | Limpiar e integrar datos.                         | Dataset limpio, script/notebook y bitácora.                | REQ-007, REQ-008, REQ-009                   | Pendiente |
|    5 | Realizar análisis exploratorio.                   | Notebook EDA y reporte de calidad.                         | REQ-010                                     | Pendiente |
|    6 | Entrenar modelos.                                 | Notebook/script de entrenamiento y artefactos.             | REQ-011                                     | Pendiente |
|    7 | Evaluar y seleccionar modelo.                     | Tabla comparativa, matrices y decisión.                    | REQ-012, REQ-013                            | Pendiente |
|    8 | Construir simulador animal.                       | Módulo de lecturas del animal.                             | REQ-014, REQ-015                            | Pendiente |
|    9 | Construir simulador ambiental.                    | Módulo de ambiente y escenarios.                           | REQ-014, REQ-015                            | Pendiente |
|   10 | Implementar backend y persistencia.               | FastAPI, modelos, esquemas y PostgreSQL.                   | REQ-001, REQ-002, REQ-003, REQ-016, REQ-017 | Pendiente |
|   11 | Implementar dashboard.                            | Dashboard operativo conectado a la API.                    | REQ-024, REQ-025                            | En progreso |
|   12 | Integrar modelo con API.                          | Endpoint de predicción funcional.                          | REQ-018, REQ-019                            | Pendiente |
|   13 | Implementar alertas.                              | Reglas, almacenamiento y consulta de alertas.              | REQ-020, REQ-021                            | Pendiente |
|   14 | Implementar notificación al propietario.          | Adaptador de correo y registro de estado.                  | REQ-022, REQ-023                            | Pendiente |
|   15 | Implementar persistencia y veterinario.           | Escalamiento y notificación correspondiente.               | REQ-021, REQ-022, REQ-023                   | Pendiente |
|   16 | Implementar historial.                            | Consultas, gráficas y línea temporal.                      | REQ-004, REQ-025                            | Pendiente |
|   17 | Ejecutar pruebas por escenarios.                  | Reporte de pruebas y resultados.                           | REQ-015, REQ-026, REQ-028                   | Pendiente |
|   18 | Integrar y empaquetar.                            | Docker Compose y demostración completa.                    | REQ-016, REQ-027, REQ-028                   | Pendiente |
|   19 | Documentar y cerrar.                              | README, limitaciones, guía de ejecución y evidencia final. | REQ-029                                     | Pendiente |

## 7. Variables y origen de datos

| Grupo            | Variables                                               | Origen permitido                      | Tratamiento requerido                                  |
| ---------------- | ------------------------------------------------------- | ------------------------------------- | ------------------------------------------------------ |
| Identificación   | ID, raza, edad, propietario                             | Registro del usuario / fuente real    | Validación de formato y valores obligatorios.          |
| Fisiología       | Peso, temperatura corporal                              | Fuente real y simulador               | Unidades documentadas, rangos plausibles y validación. |
| Comportamiento   | Actividad, alimentación, consumo de agua                | Fuente real y simulador               | Codificación consistente y relación con ambiente.      |
| Salud contextual | Vacunación, antecedentes, observaciones                 | Registro del usuario                  | No convertir observaciones en diagnóstico automático.  |
| Ambiente         | Temperatura, humedad, hora, agua, alimento, condiciones | Fuente real cuando exista y simulador | Registrar fecha/hora y disponibilidad.                 |
| Objetivo         | Bajo, medio, alto                                       | Original o derivado documentado       | Nunca inventarlo sin metodología y fuente técnica.     |

## 8. Reglas funcionales de riesgo y alertas

Estas reglas son una base para implementar y deben confirmarse con los resultados del modelo y las decisiones del equipo:

| Nivel | Acción mínima                     | Notificación               | Persistencia                             |
| ----- | --------------------------------- | -------------------------- | ---------------------------------------- |
| BAJO  | Registrar predicción e historial. | Ninguna externa.           | No escala.                               |
| MEDIO | Crear alerta y seguimiento.       | Propietario.               | Escala si cumple el umbral configurable. |
| ALTO  | Crear alerta prioritaria.         | Propietario y veterinario. | No requiere esperar persistencia.        |

El número de mediciones, ventana temporal y condición exacta para escalar un riesgo medio deben ser configurables y quedar documentados antes de la implementación de la fase 15.

## 9. Matriz de escenarios de prueba

| ID       | Escenario                | Entrada esperada                                                 | Resultado esperado                                                  | Requisitos                | Estado    |
| -------- | ------------------------ | ---------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------- | --------- |
| TEST-001 | Animal saludable         | Ambiente normal y lecturas normales.                             | Riesgo bajo, sin notificación externa.                              | REQ-015, REQ-020          | Completado: BAJO, probabilidad 0.97 |
| TEST-002 | Estrés ambiental         | Temperatura y humedad altas, actividad reducida.                 | Riesgo potencialmente mayor y alerta según modelo.                  | REQ-015, REQ-020          | Pendiente |
| TEST-003 | Posible riesgo           | Temperatura corporal elevada, actividad baja y consumo alterado. | Riesgo medio y aviso al propietario.                                | REQ-018, REQ-020          | Pendiente |
| TEST-004 | Riesgo alto              | Temperatura elevada, actividad muy baja y ambiente adverso.      | Riesgo alto, aviso al propietario y veterinario.                    | REQ-018, REQ-020          | Completado: ALTO, probabilidad 0.81 |
| TEST-005 | Riesgo medio persistente | Varias mediciones medias consecutivas.                           | Escalamiento y notificación al veterinario.                         | REQ-021, REQ-022          | Pendiente |
| TEST-006 | Recuperación             | Lecturas que vuelven a rangos normales.                          | Se registra la recuperación y no se crean escalaciones nuevas.      | REQ-004, REQ-021          | Pendiente |
| TEST-007 | Datos faltantes          | Solicitud sin una variable obligatoria.                          | Error controlado y no se genera predicción inválida.                | REQ-026                   | Pendiente |
| TEST-008 | Fuera de rango           | Temperatura, peso o humedad imposibles.                          | Validación rechaza o marca el dato según la regla definida.         | REQ-026                   | Pendiente |
| TEST-009 | Modelo no disponible     | Servicio o artefacto ML ausente.                                 | Error controlado, alerta técnica y sin pérdida de datos recibidos.  | REQ-026                   | Pendiente |
| TEST-010 | Error de correo          | Proveedor de correo no disponible.                               | Alerta permanece registrada y notificación queda en estado fallido. | REQ-022, REQ-023          | Pendiente |
| TEST-011 | Aislamiento de animales  | Registrar mediciones para dos animales.                          | El historial y las alertas no se mezclan.                           | REQ-001, REQ-004, REQ-025 | Pendiente |
| TEST-012 | Flujo completo           | Ejecutar simulación desde el dashboard.                          | Se completa el ciclo hasta historial visible.                       | REQ-028                   | Pendiente |

## 10. Estructura de entregables propuesta

```text
my-ganado/
├── frontend/
├── backend/
├── ml/
│   ├── notebooks/
│   ├── data/
│   │   ├── raw/
│   │   ├── cleaned/
│   │   └── processed/
│   ├── models/
│   ├── scripts/
│   └── README.md
├── database/
│   ├── migrations/
│   └── seeds/
├── docs/
│   ├── datasets/
│   ├── decisions/
│   └── evidence/
├── docker-compose.yml
├── README.md
└── TRAZABILIDAD.md
```

## 11. Decisiones pendientes

| ID      | Decisión                                                            | Responsable              | Fecha límite      | Estado    |
| ------- | ------------------------------------------------------------------- | ------------------------ | ----------------- | --------- |
| DEC-001 | Seleccionar dataset o combinación de datasets reales.               | Equipo ML                | Antes de fase 3   | Pendiente |
| DEC-002 | Confirmar si la variable objetivo es original o derivada.           | Equipo ML                | Antes de entrenar | Pendiente |
| DEC-003 | Definir la metodología técnica para derivar riesgo si es necesario. | Equipo ML                | Antes de entrenar | Pendiente |
| DEC-004 | Definir umbral de persistencia del riesgo medio.                    | Equipo backend / dominio | Antes de fase 15  | Pendiente |
| DEC-005 | Definir proveedor de correo para desarrollo.                        | Equipo backend           | Antes de fase 14  | Pendiente |
| DEC-006 | Definir variables mínimas obligatorias para una predicción.         | Equipo ML / backend      | Antes de fase 12  | Pendiente |
| DEC-007 | Definir estrategia ante desbalance de clases.                       | Equipo ML                | Después de EDA    | Pendiente |
| DEC-008 | Definir protocolo de versionado de datasets y modelos.              | Equipo ML                | Antes de fase 6   | Pendiente |

## 12. Riesgos y controles

| Riesgo                                                         | Impacto | Control                                                                                   |
| -------------------------------------------------------------- | ------- | ----------------------------------------------------------------------------------------- |
| No encontrar un dataset con las tres clases de riesgo.         | Alto    | Investigar una metodología documentada para objetivo derivado y declarar la limitación.   |
| Dataset pequeño, sesgado o no representativo.                  | Alto    | Reportar calidad, separar datos, usar validación adecuada y evitar afirmaciones clínicas. |
| Datos simulados confundidos con datos reales.                  | Alto    | Mantener carpetas, metadatos y documentación de origen separados.                         |
| Métricas altas por fuga de información o partición incorrecta. | Alto    | Usar pipeline, partición reproducible y revisar variables antes del entrenamiento.        |
| Simulador produce números sin relaciones plausibles.           | Medio   | Basar rangos y reglas en estadística exploratoria y probar escenarios deterministas.      |
| Servicio de correo falla.                                      | Medio   | Registrar estado de envío, conservar la alerta y permitir reintento.                      |
| Persistencia de riesgo mal definida.                           | Medio   | Hacer parámetros configurables y cubrirla con pruebas de secuencia temporal.              |
| Modelo interpretado como diagnóstico.                          | Alto    | Mostrar avisos de uso, limitar el lenguaje de UI y documentar restricciones.              |

## 13. Criterio de finalización del MVP

El MVP se considerará terminado cuando:

- [ ] Existe un dataset real, su ficha de fuente y sus limitaciones.
- [ ] Se conservan los datos originales y las versiones procesadas.
- [ ] El proceso de limpieza y preparación es reproducible.
- [ ] Se compararon los tres modelos solicitados con métricas y matriz de confusión.
- [ ] El modelo seleccionado está integrado en un endpoint de predicción.
- [ ] El simulador produce lecturas relacionadas con el ambiente.
- [ ] Se pueden ejecutar los cinco escenarios principales.
- [ ] Se registran animales, mediciones, predicciones, alertas y notificaciones.
- [ ] Se detecta y documenta el riesgo medio persistente.
- [ ] El dashboard muestra estado actual e historial.
- [ ] Las pruebas críticas pasan, incluidos errores de validación y notificación.
- [ ] Docker Compose permite levantar el sistema localmente.
- [ ] La demostración completa queda documentada con evidencia.
- [ ] La documentación deja claro que el sistema no es diagnóstico veterinario.

## 14. Bitácora de cambios

| Fecha      | Cambio                                                                              | Autor               | Impacto                       |
| ---------- | ----------------------------------------------------------------------------------- | ------------------- | ----------------------------- |
| 2026-09-25 | Creación de la matriz de requisitos, fases, pruebas, riesgos y criterios de cierre. | Equipo del proyecto | Base inicial de trazabilidad. |

## 15. Próximo paso recomendado

Iniciar la **Fase 2** con una matriz de candidatos de datasets reales. No comenzar el entrenamiento hasta resolver `DEC-001`, `DEC-002` y `DEC-003`, porque la fuente y la definición de la variable objetivo controlan la validez de todo el flujo de Machine Learning.

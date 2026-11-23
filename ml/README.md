# Módulo de Machine Learning

## Propósito

El módulo ML está diseñado para construir la semilla real de datos, ejecutar la limpieza y preparación, entrenar modelos supervisados para predecir riesgo bovino y evaluar el rendimiento experimental antes de integrar el modelo al backend.

## Flujo recomendado

1. Cargar datos reales desde `ml/data/raw/`
2. Validar fuente, columnas y licencias
3. Limpiar y transformar los datos
4. Guardar versión limpia en `ml/data/cleaned/`
5. Preparar dataset para entrenamiento y validación en `ml/data/processed/`
6. Entrenar Random Forest, Decision Tree y Logistic Regression
7. Evaluar accuracy, precision, recall, F1-score y matriz de confusión
8. Seleccionar el mejor modelo con evidencia experimental
9. Exportar el modelo final para uso por la API

## Estructura

```text
ml/
├── README.md
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── processed/
├── notebooks/
├── scripts/
├── models/
└── docs/
```

## Modelos a evaluar

- Random Forest
- Decision Tree
- Logistic Regression

## Métricas mínimas

- Accuracy
- Precision
- Recall
- F1-score
- Matriz de confusión

## Reglas de calidad

- El modelo no se entrena con datos simulados como si fueran reales.
- La variable objetivo debe documentarse como original o derivada.
- Los datos originales no se deben alterar.
- La evaluación debe respaldar la selección final del modelo.

## Nota de uso

Este módulo es la base del componente de riesgo del sistema. La clasificación en BAJO, MEDIO y ALTO debe entenderse como apoyo para seguimiento y no como diagnóstico veterinario.

## Modelo exploratorio subclínico de Ruanda

`ml/scripts/train_subclinical_model.py` entrena por separado con el dataset S1 de Ruanda una clasificación CMT negativo (`BAJO`) / CMT positivo subclínico (`MEDIO`). Usa variables de encuesta, no las variables de la API clínica, y no produce `ALTO`; por eso no reemplaza ni se carga en el endpoint clínico. Resultados y límites: `docs/MODELO_SUBCLINICO_RWANDA.md`.

# Integración de categorías de especie

| Categoría | Filas de referencia | Fuente | Raza | Predicciones disponibles |
|---|---:|---|---|---|
| Bovina adulta (vaca) | 6.600 | Clinical Mastitis in Cows | Jersey, hostlene | Sí, modelo bovino actual |
| Bovino joven (ternera/o) | 300 | LSIL Ethiopia Young Stock | No especificada | No |
| Cordero | 97 | LSIL Ethiopia Young Stock | No especificada | No |
| Cabrito | 44 | LSIL Ethiopia Young Stock | No especificada | No |

El formulario consulta los catálogos de la API. El servidor valida especie y raza, asigna el ID automáticamente y conserva la especie en SQLite. Una migración compatible añade `bovine_adult` a los registros ya existentes. Las mediciones y simulaciones del modelo de mastitis están limitadas a bovinas adultas.

Esta integración conecta las categorías descriptivas del dataset joven con el registro. No importa las 1.480 filas como animales de una finca ni convierte diagnósticos heterogéneos en predicciones. Los 1.039 registros con especie sin identificar no se ofrecen como categoría seleccionable.

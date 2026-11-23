# Registro de animales

`POST /api/v1/animals` recibe `breed`, `age_months`, `weight_kg` y `owner`. El cliente no envía `animal_id`: el servidor genera un UUID v4 con prefijo `MG-` y la base de datos impone unicidad. La creación y la asignación a la cuenta autenticada se guardan en una transacción. Enviar un ID u otros campos no admitidos produce una respuesta 422.

`GET /api/v1/catalogs/breeds` devuelve únicamente las categorías de la columna `Breed` de `ml/data/raw/cattle_mastitis.csv`, también presentes en la copia procesada: `Jersey` (6.498 registros) y `hostlene` (102 registros). El selector y la validación de nuevas bovinas adultas usan ese catálogo. Se conserva literalmente `hostlene`; no se sustituye por Holstein sin confirmar su significado en la fuente.

`GET /api/v1/catalogs/species` expone las categorías presentes en los datasets. El registro distingue bovina adulta (fuente de mastitis), bovino joven/ternera-o (300 filas bovinas de animales jóvenes), cordero (97) y cabrito (44). No se ofrece «especie sin identificar», pues no es útil como tipo de animal en el formulario. Para categorías de animales jóvenes se guarda «No especificada» como raza: la fuente joven no da un catálogo de razas. La app no ejecuta el modelo de mastitis para estas categorías.

Los registros anteriores mantienen sus IDs y sus nombres de raza. La migración agrega `species` con el valor `bovine_adult` a las filas previas, que pertenecían al registro bovino original. El esquema de respuesta se separa del esquema de creación para poder consultar esos datos históricos sin obligar a modificarlos.

El formulario desactiva el guardado mientras carga el catálogo o envía el registro. Si falla la carga, informa cómo reintentar. El control de doble clic no sustituye una estrategia de idempotencia para reintentos de red.

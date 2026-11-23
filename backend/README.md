# Backend My Ganado

## Ejecucion local

Desde la raiz del proyecto:

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --reload
```

Para ejecutar el sistema completo con contenedores, usa `docker compose up --build` desde la raíz y abre `http://localhost:8080`.

Las pruebas del repositorio se ejecutan desde la raíz con:

```powershell
$env:PYTHONPATH = "backend"
python -m unittest discover -s tests -v
```

Endpoints iniciales:

- `GET /health`
- `POST /api/v1/animals`
- `GET /api/v1/animals`
- `GET /api/v1/animals/{animal_id}/history`
- `GET /api/v1/alerts?animal_id=...`
- `POST /api/v1/predictions`
- `POST /api/v1/animals/{animal_id}/measurements`
- `POST /api/v1/simulations` (incluye `animal_id` para guardar la lectura)

El endpoint usa el modelo persistido en `ml/models/risk_model.joblib` y devuelve una clasificacion de apoyo, no un diagnostico veterinario.

Los escenarios disponibles son `normal`, `estres_ambiental`, `posible_riesgo`, `alto` y `persistente`. La semilla permite repetir la misma lectura.

La persistencia local usa SQLite en `backend/data/myganado.db`. Cada medicion registrada conserva la lectura, la prediccion y el estado inicial de alerta.

Las alertas activas se generan para riesgos `MEDIO` y `ALTO`; un tercer riesgo medio consecutivo queda escalado para veterinaria. El modelo incluido actualmente fue entrenado con las clases reales `BAJO` y `ALTO`, por lo que la clase `MEDIO` queda preparada en el contrato y en la política de alertas, pero requiere una nueva semilla o una metodología derivada documentada antes de activarse como predicción del modelo.

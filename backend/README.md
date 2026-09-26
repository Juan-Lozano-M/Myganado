# Backend My Ganado

## Ejecucion local

Desde la raiz del proyecto:

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --reload
```

Endpoints iniciales:

- `GET /health`
- `POST /api/v1/animals`
- `GET /api/v1/animals`
- `GET /api/v1/animals/{animal_id}/history`
- `GET /api/v1/alerts?animal_id=...`
- `POST /api/v1/predictions`
- `POST /api/v1/animals/{animal_id}/measurements`
- `POST /api/v1/simulations`

El endpoint usa el modelo persistido en `ml/models/risk_model.joblib` y devuelve una clasificacion de apoyo, no un diagnostico veterinario.

Los escenarios disponibles son `normal`, `estres_ambiental`, `posible_riesgo`, `alto` y `persistente`. La semilla permite repetir la misma lectura.

La persistencia local usa SQLite en `backend/data/myganado.db`. Cada medicion registrada conserva la lectura, la prediccion y el estado inicial de alerta.

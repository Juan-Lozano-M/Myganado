import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATABASE_PATH = PROJECT_ROOT / "backend" / "data" / "myganado.db"


class Repository:
    def __init__(self, database_path: Path = DATABASE_PATH) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS animals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id TEXT NOT NULL UNIQUE,
                    breed TEXT NOT NULL,
                    age_months INTEGER NOT NULL,
                    weight_kg REAL NOT NULL,
                    owner TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measurement_id INTEGER NOT NULL,
                    risk_level TEXT NOT NULL,
                    probability REAL NOT NULL,
                    model TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id TEXT NOT NULL,
                    prediction_id INTEGER NOT NULL,
                    risk_level TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def create_animal(self, animal: dict[str, Any]) -> dict[str, Any]:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO animals (animal_id, breed, age_months, weight_kg, owner, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    animal["animal_id"],
                    animal["breed"],
                    animal["age_months"],
                    animal["weight_kg"],
                    animal["owner"],
                    created_at,
                ),
            )
            return {"id": cursor.lastrowid, **animal, "created_at": created_at}

    def list_animals(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM animals ORDER BY id").fetchall()
            return [dict(row) for row in rows]

    def animal_exists(self, animal_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM animals WHERE animal_id = ?",
                (animal_id,),
            ).fetchone()
            return row is not None

    def get_history(self, animal_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT m.id AS measurement_id, m.animal_id, m.payload, m.created_at,
                       p.id AS prediction_id, p.risk_level, p.probability, p.model
                FROM measurements m
                JOIN predictions p ON p.measurement_id = m.id
                WHERE m.animal_id = ?
                ORDER BY m.created_at DESC
                """,
                (animal_id,),
            ).fetchall()

        history = []
        for row in rows:
            item = dict(row)
            item["payload"] = json.loads(item["payload"])
            history.append(item)
        return history

    def list_alerts(self, animal_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM alerts"
        parameters: tuple[str, ...] = ()
        if animal_id is not None:
            query += " WHERE animal_id = ?"
            parameters = (animal_id,)
        query += " ORDER BY created_at DESC"

        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
            return [dict(row) for row in rows]

    def save_measurement(
        self,
        animal_id: str,
        payload: dict[str, Any],
        risk_level: str,
        probability: float,
        model: str,
    ) -> dict[str, Any]:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            measurement_cursor = connection.execute(
                "INSERT INTO measurements (animal_id, payload, created_at) VALUES (?, ?, ?)",
                (animal_id, json.dumps(payload), created_at),
            )
            measurement_id = measurement_cursor.lastrowid
            prediction_cursor = connection.execute(
                """
                INSERT INTO predictions (measurement_id, risk_level, probability, model, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (measurement_id, risk_level, probability, model, created_at),
            )
            prediction_id = prediction_cursor.lastrowid
            alert_status = "registrada" if risk_level == "BAJO" else "pendiente_notificacion"
            connection.execute(
                """
                INSERT INTO alerts (animal_id, prediction_id, risk_level, status, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (animal_id, prediction_id, risk_level, alert_status, created_at),
            )

        return {
            "measurement_id": measurement_id,
            "prediction_id": prediction_id,
            "animal_id": animal_id,
            "risk_level": risk_level,
            "probability": probability,
            "model": model,
            "alert_status": alert_status,
            "created_at": created_at,
        }

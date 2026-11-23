import sqlite3
import json
from contextlib import contextmanager
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

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS animals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id TEXT NOT NULL UNIQUE,
                    species TEXT NOT NULL DEFAULT 'bovine_adult',
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
                CREATE TABLE IF NOT EXISTS animal_access (
                    animal_id TEXT NOT NULL, user_id INTEGER NOT NULL, access TEXT NOT NULL,
                    PRIMARY KEY (animal_id, user_id)
                );
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id TEXT NOT NULL, prediction_id INTEGER NOT NULL,
                    recipient_email TEXT NOT NULL, status TEXT NOT NULL,
                    error TEXT, created_at TEXT NOT NULL
                );
                """
            )
            columns = {row[1] for row in connection.execute("PRAGMA table_info(animals)")}
            if "species" not in columns:
                connection.execute("ALTER TABLE animals ADD COLUMN species TEXT NOT NULL DEFAULT 'bovine_adult'")
            notification_columns = {row[1] for row in connection.execute("PRAGMA table_info(notifications)")}
            if "prediction_id" not in notification_columns:
                connection.execute("ALTER TABLE notifications RENAME TO notifications_legacy")
                connection.execute("""CREATE TABLE notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id TEXT NOT NULL, prediction_id INTEGER NOT NULL,
                    recipient_email TEXT NOT NULL, status TEXT NOT NULL,
                    error TEXT, created_at TEXT NOT NULL
                )""")
                connection.execute("""INSERT INTO notifications
                    (id, animal_id, prediction_id, recipient_email, status, error, created_at)
                    SELECT n.id, n.animal_id,
                           COALESCE((SELECT a.prediction_id FROM alerts a WHERE a.id=n.alert_id), 0),
                           COALESCE(n.recipient_email, ''),
                           CASE WHEN n.recipient_email IS NULL THEN 'sin_configurar'
                                WHEN NOT EXISTS (SELECT 1 FROM alerts a WHERE a.id=n.alert_id) THEN 'fallida'
                                ELSE n.status END,
                           n.error, n.created_at FROM notifications_legacy n""")
                connection.execute("DROP TABLE notifications_legacy")

    def create_animal(self, animal: dict[str, Any], user_id: int | None = None) -> dict[str, Any]:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO animals (animal_id, species, breed, age_months, weight_kg, owner, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    animal["animal_id"],
                    animal.get("species", "bovine_adult"),
                    animal["breed"],
                    animal["age_months"],
                    animal["weight_kg"],
                    animal["owner"],
                    created_at,
                ),
            )
            if user_id is not None:
                connection.execute("INSERT INTO animal_access VALUES (?, ?, 'owner')", (animal["animal_id"], user_id))
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

    def list_notifications(self, animal_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM notifications"
        parameters = () if animal_id is None else (animal_id,)
        if animal_id is not None:
            query += " WHERE animal_id=?"
        with self._connect() as connection:
            return [dict(row) for row in connection.execute(query + " ORDER BY id DESC", parameters)]

    def pending_notifications(self, prediction_id: int) -> list[dict[str, Any]]:
        with self._connect() as connection:
            return [dict(row) for row in connection.execute(
                "SELECT * FROM notifications WHERE prediction_id=? AND status='pendiente'", (prediction_id,))]

    def update_notification(self, notification_id: int, status: str, error: str | None = None) -> None:
        with self._connect() as connection:
            connection.execute("UPDATE notifications SET status=?, error=? WHERE id=?", (status, error, notification_id))

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
            previous = [row[0] for row in connection.execute(
                "SELECT p.risk_level FROM predictions p JOIN measurements m ON m.id=p.measurement_id "
                "WHERE m.animal_id=? ORDER BY p.id DESC LIMIT 2", (animal_id,))]
            measurement_cursor = connection.execute(
                "INSERT INTO measurements (animal_id, payload, created_at) VALUES (?, ?, ?)",
                (animal_id, json.dumps(payload, default=str), created_at),
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
            if risk_level == "BAJO":
                alert_status = "sin_alerta"
                recipient_access = ()
            elif risk_level == "ALTO":
                alert_status = "pendiente_notificacion_propietario_veterinario"
                recipient_access = ("owner", "viewer")
            elif previous == ["MEDIO", "MEDIO"]:
                alert_status = "pendiente_notificacion_veterinario"
                recipient_access = ("viewer",)
            else:
                alert_status = "pendiente_notificacion_propietario"
                recipient_access = ("owner",)
            if risk_level != "BAJO":
                connection.execute(
                """
                INSERT INTO alerts (animal_id, prediction_id, risk_level, status, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (animal_id, prediction_id, risk_level, alert_status, created_at),
                )
                if connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='users'").fetchone():
                    for access in recipient_access:
                        for recipient in connection.execute(
                            "SELECT u.email FROM animal_access a JOIN users u ON u.id=a.user_id "
                            "WHERE a.animal_id=? AND a.access=?", (animal_id, access)):
                            connection.execute(
                                "INSERT INTO notifications (animal_id, prediction_id, recipient_email, status, created_at) "
                                "VALUES (?, ?, ?, 'pendiente', ?)",
                                (animal_id, prediction_id, recipient[0], created_at))

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

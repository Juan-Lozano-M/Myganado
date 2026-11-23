import tempfile
import unittest
from pathlib import Path

from app.services.repository import Repository


class RepositoryWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = Repository(Path(self.temp_dir.name) / "test.db")
        self.repository.create_animal(
            {
                "animal_id": "cow-test-1",
                "species": "bovine_adult",
                "breed": "Jersey",
                "age_months": 24,
                "weight_kg": 420.0,
                "owner": "Finca de prueba",
            }
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def save(self, risk_level):
        return self.repository.save_measurement(
            "cow-test-1",
            {"day": 1, "temperature": 38.5},
            risk_level,
            0.8,
            "RandomForest",
        )

    def test_low_risk_does_not_create_active_alert(self):
        result = self.save("BAJO")
        self.assertEqual(result["alert_status"], "sin_alerta")
        self.assertEqual(self.repository.list_alerts(), [])

    def test_high_risk_alerts_owner_and_veterinarian(self):
        result = self.save("ALTO")
        self.assertEqual(result["alert_status"], "pendiente_notificacion_propietario_veterinario")
        self.assertEqual(len(self.repository.list_alerts("cow-test-1")), 1)

    def test_third_consecutive_medium_risk_escalates(self):
        statuses = [self.save("MEDIO")["alert_status"] for _ in range(3)]
        self.assertEqual(
            statuses,
            [
                "pendiente_notificacion_propietario",
                "pendiente_notificacion_propietario",
                "pendiente_notificacion_veterinario",
            ],
        )

    def test_low_risk_breaks_medium_streak(self):
        self.save("MEDIO")
        self.save("MEDIO")
        self.save("BAJO")
        self.assertEqual(self.save("MEDIO")["alert_status"], "pendiente_notificacion_propietario")

    def test_legacy_notifications_migrate_without_losing_records(self):
        with self.repository._connect() as db:
            db.execute("INSERT INTO alerts (animal_id, prediction_id, risk_level, status, created_at) VALUES (?,?,?,?,?)",
                       ("cow-test-1", 7, "ALTO", "pendiente", "2026-01-01"))
            db.execute("DROP TABLE notifications")
            db.execute("""CREATE TABLE notifications (
                id INTEGER PRIMARY KEY, alert_id INTEGER NOT NULL, animal_id TEXT NOT NULL,
                recipient_role TEXT NOT NULL, recipient_email TEXT, status TEXT NOT NULL,
                error TEXT, created_at TEXT NOT NULL, attempted_at TEXT)""")
            db.execute("INSERT INTO notifications VALUES (1,1,'cow-test-1','owner','owner@example.com','enviada',NULL,'2026-01-01',NULL)")
        migrated = Repository(self.repository.database_path).list_notifications("cow-test-1")
        self.assertEqual(migrated[0]["prediction_id"], 7)
        self.assertEqual(migrated[0]["recipient_email"], "owner@example.com")
        self.assertEqual(migrated[0]["status"], "enviada")


if __name__ == "__main__":
    unittest.main()

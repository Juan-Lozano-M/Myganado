"""Authentication and account isolation, always against a temporary database."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from fastapi.testclient import TestClient
from app.main import app
from app.services.repository import Repository


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "auth.db"
        self.repo = Repository(self.path)
        self.patches = [patch(target, lambda: self.repo) for target in
                        ("app.services.auth.Repository", "app.main.Repository")]
        for item in self.patches:
            item.start()
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        for item in self.patches:
            item.stop()
        self.temp.cleanup()

    def register(self, client, email, role="productor"):
        response = client.post("/api/v1/auth/register", json={
            "email": email, "name": "Cuenta de prueba", "password": "Prueba-segura-123", "role": role})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertNotIn("password", response.text)
        return response

    def animal(self):
        response = self.client.post("/api/v1/animals", json={"animal_id": "test-1", "species": "bovine_adult", "breed": "Jersey",
                                   "age_months": 30, "weight_kg": 400, "owner": "Finca"})
        self.assertEqual(response.status_code, 201, response.text)

    def test_sessions_and_passwords(self):
        self.assertEqual(self.client.get("/api/v1/animals").status_code, 401)
        response = self.register(self.client, " USER@example.com ")
        self.assertIn("HttpOnly", response.headers["set-cookie"])
        self.assertIn("SameSite=strict", response.headers["set-cookie"])
        self.assertEqual(self.client.get("/api/v1/auth/me").json()["email"], "user@example.com")
        old_cookie = self.client.cookies.get("myganado_session")
        with self.repo._connect() as db:
            self.assertNotIn("Prueba-segura-123", db.execute("SELECT password_hash FROM users").fetchone()[0])
        self.client.post("/api/v1/auth/logout")
        self.client.cookies.set("myganado_session", old_cookie)
        self.assertEqual(self.client.get("/api/v1/auth/me").status_code, 401)
        self.client.cookies.clear()
        self.assertEqual(self.client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "incorrecta123"}).status_code, 401)
        self.assertEqual(self.client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "Prueba-segura-123"}).status_code, 200)
        with self.repo._connect() as db:
            db.execute("UPDATE sessions SET expires=0")
        self.assertEqual(self.client.get("/api/v1/auth/me").status_code, 401)

    def test_ownership_sharing_and_revocation(self):
        self.register(self.client, "owner@example.com")
        self.animal()
        with TestClient(app) as other, TestClient(app) as vet:
            self.register(other, "other@example.com")
            self.register(vet, "vet@example.com", "veterinario")
            for client in (other, vet):
                self.assertEqual(client.get("/api/v1/animals").json(), [])
                self.assertEqual(client.get("/api/v1/animals/test-1/history").status_code, 404)
                self.assertEqual(client.get("/api/v1/alerts?animal_id=test-1").status_code, 404)
            self.assertEqual(other.post("/api/v1/simulations", json={"animal_id": "test-1", "scenario": "normal"}).status_code, 404)
            route = "/api/v1/auth/animals/test-1/veterinarian"
            self.assertEqual(other.post(route, json={"email": "vet@example.com"}).status_code, 404)
            self.assertEqual(self.client.post(route, json={"email": "vet@example.com"}).status_code, 200)
            self.assertEqual(len(vet.get("/api/v1/animals").json()), 1)
            self.assertEqual(vet.get("/api/v1/animals/test-1/history").status_code, 200)
            self.assertEqual(vet.post("/api/v1/simulations", json={"animal_id": "test-1", "scenario": "normal"}).status_code, 403)
            self.assertEqual(self.client.request("DELETE", route, json={"email": "vet@example.com"}).status_code, 200)
            self.assertEqual(vet.get("/api/v1/animals/test-1/history").status_code, 404)

    def test_legacy_animals_not_claimed_by_registration(self):
        self.repo.create_animal({"animal_id": "legacy", "species": "bovine_adult", "breed": "Jersey", "age_months": 1, "weight_kg": 50, "owner": "Old"})
        self.register(self.client, "new@example.com")
        self.assertEqual(self.client.get("/api/v1/animals").json(), [])
        self.assertTrue(self.repo.animal_exists("legacy"))

    def test_roles_validation_csrf_and_throttle(self):
        self.assertEqual(self.client.post("/api/v1/auth/register", json={"email": "x@y.com", "name": "Admin", "password": "Prueba-segura-123", "role": "admin"}).status_code, 422)
        self.register(self.client, "user@example.com")
        self.assertEqual(self.client.post("/api/v1/auth/logout", headers={"Origin": "https://untrusted.example"}).status_code, 403)
        for _ in range(10):
            self.assertEqual(self.client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "incorrecta123"}).status_code, 401)
        self.assertEqual(self.client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "incorrecta123"}).status_code, 429)


if __name__ == "__main__":
    unittest.main()

"""Signed JWT authentication with server-side session revocation."""
import hashlib
import hmac
import logging
import os
import secrets
import sqlite3
import time
import jwt

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator
from typing import Literal

from app.services.repository import Repository

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
COOKIE = "myganado_session"
TTL = 8 * 60 * 60
JWT_ALGORITHM = "HS256"
JWT_ISSUER = "myganado-api"
JWT_AUDIENCE = "myganado-web"
JWT_SECRET = os.environ.get("MYGANADO_JWT_SECRET")
if not JWT_SECRET:
    if os.environ.get("MYGANADO_ENV", "development") != "development":
        raise RuntimeError("Configura MYGANADO_JWT_SECRET antes de iniciar el servidor")
    JWT_SECRET = secrets.token_urlsafe(48)
    logging.getLogger(__name__).warning(
        "JWT: clave temporal de desarrollo; reiniciar el servidor invalidará las sesiones. "
        "Configura MYGANADO_JWT_SECRET para usar una clave persistente."
    )
if len(JWT_SECRET.encode()) < 32:
    raise RuntimeError("MYGANADO_JWT_SECRET debe tener al menos 32 bytes aleatorios")


def database():
    repo = Repository()
    with repo._connect() as db:
        db.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL, role TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL, expires REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS animal_access (
                animal_id TEXT NOT NULL, user_id INTEGER NOT NULL, access TEXT NOT NULL,
                PRIMARY KEY (animal_id, user_id));
            CREATE TABLE IF NOT EXISTS login_attempts (
                email TEXT PRIMARY KEY, attempts INTEGER NOT NULL, started REAL NOT NULL);
        ''')
    return repo


class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=10, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        value = value.strip().lower()
        if len(value.split("@")) != 2 or not all(value.split("@")) or any(c.isspace() for c in value):
            raise ValueError("Introduce un correo válido")
        return value


class Registration(Credentials):
    name: str = Field(min_length=2, max_length=100)
    role: Literal["productor", "veterinario"]

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        if len(value.strip()) < 2:
            raise ValueError("Introduce tu nombre")
        return value.strip()


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
    return salt + ":" + digest


def public_user(user):
    return {key: user[key] for key in ("id", "name", "email", "role")}


def current_user(request: Request):
    token = request.cookies.get(COOKIE, "")
    try:
        claims = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER, audience=JWT_AUDIENCE,
            options={"require": ["sub", "iat", "nbf", "exp", "iss", "aud", "jti"]},
        )
        if not isinstance(claims["sub"], str) or not claims["sub"].isdigit():
            raise jwt.InvalidTokenError("Invalid subject")
        if not isinstance(claims["jti"], str) or not claims["jti"]:
            raise jwt.InvalidTokenError("Invalid token identifier")
    except jwt.InvalidTokenError as exc:
        raise HTTPException(401, "Tu sesión no es válida o ha caducado. Inicia sesión de nuevo.") from exc
    with database()._connect() as db:
        user = db.execute('''SELECT u.* FROM users u JOIN sessions s ON s.user_id=u.id
            WHERE s.token_hash=? AND s.expires>? AND u.id=?''',
            (hashlib.sha256(token.encode()).hexdigest(), time.time(), int(claims["sub"]))).fetchone()
    if user is None:
        raise HTTPException(401, "Inicia sesión para continuar")
    return public_user(user)


def authorize_animal(user, animal_id, write=False):
    with database()._connect() as db:
        access = db.execute("SELECT access FROM animal_access WHERE animal_id=? AND user_id=?",
                            (animal_id, user["id"])).fetchone()
    if not access or (write and access["access"] != "owner"):
        raise HTTPException(404, "Animal no disponible para esta cuenta")


def visible_ids(user):
    with database()._connect() as db:
        return {row[0] for row in db.execute("SELECT animal_id FROM animal_access WHERE user_id=?", (user["id"],))}


def start_session(user, request, response):
    now = int(time.time())
    token = jwt.encode(
        {"sub": str(user["id"]), "iat": now, "nbf": now, "exp": now + TTL,
         "iss": JWT_ISSUER, "aud": JWT_AUDIENCE, "jti": secrets.token_urlsafe(32)},
        JWT_SECRET, algorithm=JWT_ALGORITHM,
    )
    old = request.cookies.get(COOKIE, "")
    with database()._connect() as db:
        db.execute("DELETE FROM sessions WHERE expires<=? OR token_hash=?",
                   (time.time(), hashlib.sha256(old.encode()).hexdigest()))
        db.execute("INSERT INTO sessions VALUES (?, ?, ?)",
                   (hashlib.sha256(token.encode()).hexdigest(), user["id"], now + TTL))
    response.set_cookie(COOKIE, token, max_age=TTL, httponly=True,
                        secure=request.url.scheme == "https", samesite="strict", path="/")
    response.headers["Cache-Control"] = "no-store"
    return public_user(user)


@router.post("/register", status_code=201)
def register(data: Registration, request: Request, response: Response):
    try:
        with database()._connect() as db:
            cursor = db.execute("INSERT INTO users(name,email,password_hash,role) VALUES (?,?,?,?)",
                                (data.name, data.email, password_hash(data.password), data.role))
            user = {"id": cursor.lastrowid, **data.model_dump(exclude={"password"})}
    except sqlite3.IntegrityError:
        raise HTTPException(409, "No se pudo registrar ese correo. Intenta iniciar sesión.")
    return start_session(user, request, response)


@router.post("/login")
def login(data: Credentials, request: Request, response: Response):
    now = time.time()
    with database()._connect() as db:
        db.execute("DELETE FROM login_attempts WHERE started<?", (now - 900,))
        attempt = db.execute("SELECT attempts FROM login_attempts WHERE email=?", (data.email,)).fetchone()
        if attempt and attempt[0] >= 10:
            raise HTTPException(429, "Demasiados intentos. Espera 15 minutos e inténtalo de nuevo.")
        db.execute('''INSERT INTO login_attempts VALUES (?,1,?) ON CONFLICT(email)
            DO UPDATE SET attempts=attempts+1''', (data.email, now))
        user = db.execute("SELECT * FROM users WHERE email=?", (data.email,)).fetchone()
    stored = user["password_hash"] if user else password_hash("dummy-password", "00" * 16)
    valid = hmac.compare_digest(stored, password_hash(data.password, stored.split(":")[0]))
    if not user or not valid:
        raise HTTPException(401, "Correo o contraseña incorrectos")
    with database()._connect() as db:
        db.execute("DELETE FROM login_attempts WHERE email=?", (data.email,))
    return start_session(user, request, response)


@router.get("/me")
def me(response: Response, user=Depends(current_user)):
    response.headers["Cache-Control"] = "no-store"
    return user


@router.post("/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(COOKIE, "")
    with database()._connect() as db:
        db.execute("DELETE FROM sessions WHERE token_hash=?", (hashlib.sha256(token.encode()).hexdigest(),))
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


class ShareRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)


@router.post("/animals/{animal_id}/veterinarian")
def share(animal_id: str, data: ShareRequest, user=Depends(current_user)):
    authorize_animal(user, animal_id, write=True)
    with database()._connect() as db:
        vet = db.execute("SELECT id FROM users WHERE email=? AND role='veterinario'",
                         (data.email.strip().lower(),)).fetchone()
        if not vet:
            raise HTTPException(404, "No hay una cuenta veterinaria con ese correo")
        db.execute("INSERT OR IGNORE INTO animal_access VALUES (?, ?, 'viewer')", (animal_id, vet["id"]))
    return {"ok": True}


@router.delete("/animals/{animal_id}/veterinarian")
def unshare(animal_id: str, data: ShareRequest, user=Depends(current_user)):
    authorize_animal(user, animal_id, write=True)
    with database()._connect() as db:
        db.execute('''DELETE FROM animal_access WHERE animal_id=? AND access='viewer'
            AND user_id IN (SELECT id FROM users WHERE email=?)''', (animal_id, data.email.strip().lower()))
    return {"ok": True}

"""Explicit local assignment of a legacy animal to a registered producer."""
import argparse
from app.services.auth import database


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--animal", required=True)
    parser.add_argument("--email", required=True)
    args = parser.parse_args()
    with database()._connect() as db:
        db.execute("BEGIN IMMEDIATE")
        user = db.execute("SELECT id FROM users WHERE email=? AND role='productor'", (args.email.strip().lower(),)).fetchone()
        if not user:
            parser.error("No existe una cuenta de productor con ese correo")
        if not db.execute("SELECT 1 FROM animals WHERE animal_id=?", (args.animal,)).fetchone():
            parser.error("El animal no existe")
        if db.execute("SELECT 1 FROM animal_access WHERE animal_id=? AND access='owner'", (args.animal,)).fetchone():
            parser.error("El animal ya tiene propietario de cuenta; no se ha modificado")
        db.execute("INSERT INTO animal_access VALUES (?, ?, 'owner')", (args.animal, user[0]))
    print("Animal vinculado a la cuenta indicada.")


if __name__ == "__main__":
    main()

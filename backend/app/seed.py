"""Siembra la base de datos desde los CSV en seed_data/ y crea el superadmin.

Idempotente: solo carga cada tabla si esta vacia. Se ejecuta al iniciar la app.
"""
import csv
import unicodedata
from pathlib import Path

from sqlalchemy.orm import Session

from .auth import hash_password
from .config import settings
from .database import Base, SessionLocal, engine
from .models import Cups, Iss, Soat, Trazabilidad, User

SEED_DIR = Path(__file__).resolve().parent.parent / "seed_data"


def normalizar(texto: str) -> str:
    """Quita acentos y pasa a mayusculas para busqueda insensible a tildes."""
    t = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in t if not unicodedata.combining(c)).upper()


def _int(v):
    v = (v or "").strip()
    return int(v) if v.isdigit() else None


def _read(name):
    path = SEED_DIR / name
    with open(path, encoding="utf-8-sig") as f:
        yield from csv.DictReader(f)


def seed_cups(db: Session):
    if db.query(Cups).first():
        return
    objs = [Cups(codigo=r["codigo"], nombre=r["nombre"], nombre_norm=normalizar(r["nombre"]),
                 capitulo=r["capitulo"], vigente=r["vigente"] == "1")
            for r in _read("cups.csv")]
    db.bulk_save_objects(objs)
    db.commit()
    print(f"  cups: {len(objs)} registros")


def seed_soat(db: Session):
    if db.query(Soat).first():
        return
    objs = [Soat(codigo_cups=r["codigo_cups"], codigo_soat=r["codigo_soat"],
                 descripcion_soat=r["descripcion_soat"], clase=r["clase"],
                 cobertura=r["cobertura"], uvb=r["uvb"], valor_pesos=_int(r["valor_pesos"]))
            for r in _read("soat.csv")]
    db.bulk_save_objects(objs)
    db.commit()
    print(f"  soat: {len(objs)} registros")


def seed_iss(db: Session):
    if db.query(Iss).first():
        return
    objs = [Iss(codigo_cups=r["codigo_cups"], codigo_iss=r["codigo_iss"], clase=r["clase"],
                descripcion=r["descripcion"], tipo_valor=r["tipo_valor"],
                uvr=_int(r["uvr"]), valor_pesos=_int(r["valor_pesos"]))
            for r in _read("iss2001.csv")]
    db.bulk_save_objects(objs)
    db.commit()
    print(f"  iss2001: {len(objs)} registros")


def seed_trazabilidad(db: Session):
    if db.query(Trazabilidad).first():
        return
    objs = [Trazabilidad(codigo_no_vigente=r["codigo_no_vigente"],
                         descripcion_no_vigente=r["descripcion_no_vigente"],
                         accion=r["accion"], codigo_reemplazo=r["codigo_reemplazo"],
                         descripcion_reemplazo=r["descripcion_reemplazo"])
            for r in _read("trazabilidad.csv")]
    db.bulk_save_objects(objs)
    db.commit()
    print(f"  trazabilidad: {len(objs)} registros")


def seed_admin(db: Session):
    if db.query(User).filter(User.username == settings.admin_username).first():
        return
    admin = User(
        username=settings.admin_username,
        email=settings.admin_email,
        full_name=settings.admin_full_name,
        hashed_password=hash_password(settings.admin_password),
        is_active=True, is_admin=True, can_view_soat=True, can_view_iss=True,
    )
    db.add(admin)
    db.commit()
    print(f"  superadmin '{settings.admin_username}' creado")


def run_seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("Sembrando base de datos...")
        seed_cups(db)
        seed_soat(db)
        seed_iss(db)
        seed_trazabilidad(db)
        seed_admin(db)
        print("Siembra completa.")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()

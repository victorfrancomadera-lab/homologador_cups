"""Modelos ORM."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, Text

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False)
    full_name = Column(String(160), default="")
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    # Permisos granulares sobre que homologaciones puede ver el usuario
    can_view_soat = Column(Boolean, default=True, nullable=False)
    can_view_iss = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Cups(Base):
    __tablename__ = "cups"

    codigo = Column(String(16), primary_key=True)
    nombre = Column(Text, nullable=False)
    nombre_norm = Column(Text, default="", index=True)  # sin acentos, mayusculas
    capitulo = Column(Text, default="")
    vigente = Column(Boolean, default=True, nullable=False)


class Soat(Base):
    __tablename__ = "soat"

    id = Column(Integer, primary_key=True)
    codigo_cups = Column(String(16), index=True, nullable=False)
    codigo_soat = Column(String(16), default="")
    descripcion_soat = Column(Text, default="")
    clase = Column(String(64), default="")
    cobertura = Column(String(32), default="")
    uvb = Column(String(16), default="")
    valor_pesos = Column(Integer, nullable=True)


class Iss(Base):
    __tablename__ = "iss2001"

    id = Column(Integer, primary_key=True)
    codigo_cups = Column(String(16), index=True, nullable=False)
    codigo_iss = Column(String(16), default="")
    clase = Column(String(16), default="")
    descripcion = Column(Text, default="")
    tipo_valor = Column(String(16), default="")  # UVR | PESOS | POR_VERIFICAR
    uvr = Column(Integer, nullable=True)
    valor_pesos = Column(Integer, nullable=True)


class Trazabilidad(Base):
    __tablename__ = "trazabilidad"

    id = Column(Integer, primary_key=True)
    codigo_no_vigente = Column(String(16), index=True, nullable=False)
    descripcion_no_vigente = Column(Text, default="")
    accion = Column(String(64), default="")
    codigo_reemplazo = Column(String(16), default="")
    descripcion_reemplazo = Column(Text, default="")


Index("ix_cups_nombre", Cups.nombre)

"""Esquemas Pydantic (entrada/salida de la API)."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth / Usuarios ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    full_name: str = ""
    is_active: bool = True
    is_admin: bool = False
    can_view_soat: bool = True
    can_view_iss: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    can_view_soat: Optional[bool] = None
    can_view_iss: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=6)


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Homologacion ----------
class SoatOut(BaseModel):
    codigo_soat: str
    descripcion_soat: str
    clase: str
    cobertura: str
    uvb: str
    valor_pesos: Optional[int]

    class Config:
        from_attributes = True


class IssValorRol(BaseModel):
    rol: str
    valor_pesos: int


class IssOut(BaseModel):
    codigo_iss: str
    clase: str
    descripcion: str
    tipo_valor: str
    uvr: Optional[int]
    valor_pesos: Optional[int]          # para registros en pesos directos
    valores_por_rol: List[IssValorRol] = []  # para registros en UVR


class CupsInfo(BaseModel):
    codigo: str
    nombre: str
    capitulo: str
    vigente: bool


class HomologacionOut(BaseModel):
    consulta: str
    encontrado: bool
    estado: str  # VIGENTE | NO_VIGENTE | NO_ENCONTRADO
    cups: Optional[CupsInfo] = None
    mensaje: str = ""
    reemplazo: Optional[CupsInfo] = None
    soat: List[SoatOut] = []
    iss: List[IssOut] = []


class SugerenciaOut(BaseModel):
    codigo: str
    nombre: str
    vigente: bool

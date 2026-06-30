"""Router de busqueda y homologacion CUPS -> SOAT / ISS 2001."""
import unicodedata
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..config import settings
from ..database import get_db
from ..models import Cups, Iss, Soat, Trazabilidad, User
from ..schemas import (CupsInfo, HomologacionOut, IssOut, IssValorRol, SoatOut,
                       SugerenciaOut)

router = APIRouter(prefix="/api/search", tags=["busqueda"])


def _iss_to_out(row: Iss) -> IssOut:
    valores = []
    if row.tipo_valor == "UVR" and row.uvr:
        for rol, tarifa in (("Especialista quirurgico/gineco", settings.uvr_especialista),
                            ("Anestesiologia", settings.uvr_anestesia),
                            ("Medico ayudante quirurgico", settings.uvr_ayudante),
                            ("Medico u odontologo general", settings.uvr_general)):
            valores.append(IssValorRol(rol=rol, valor_pesos=row.uvr * tarifa))
    return IssOut(
        codigo_iss=row.codigo_iss, clase=row.clase, descripcion=row.descripcion,
        tipo_valor=row.tipo_valor, uvr=row.uvr, valor_pesos=row.valor_pesos,
        valores_por_rol=valores,
    )


@router.get("/sugerencias", response_model=List[SugerenciaOut])
def sugerencias(q: str = Query(min_length=2), db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    """Autocompletado por codigo o nombre (insensible a acentos, max 15)."""
    q = q.strip()
    norm = "".join(c for c in unicodedata.normalize("NFKD", q)
                   if not unicodedata.combining(c)).upper()
    rows = (db.query(Cups)
            .filter((Cups.codigo.ilike(f"{q}%")) | (Cups.nombre_norm.ilike(f"%{norm}%")))
            .order_by(Cups.codigo).limit(15).all())
    return [SugerenciaOut(codigo=r.codigo, nombre=r.nombre, vigente=r.vigente) for r in rows]


@router.get("/{codigo}", response_model=HomologacionOut)
def homologar(codigo: str, db: Session = Depends(get_db),
              user: User = Depends(get_current_user)):
    codigo = codigo.strip()
    cups = db.get(Cups, codigo)

    # Caso 1: codigo no esta en la tabla de vigentes -> revisar trazabilidad
    if not cups:
        traz = (db.query(Trazabilidad)
                .filter(Trazabilidad.codigo_no_vigente == codigo).first())
        if traz:
            reemplazo_cups = db.get(Cups, traz.codigo_reemplazo)
            reemplazo = None
            if reemplazo_cups:
                reemplazo = CupsInfo(codigo=reemplazo_cups.codigo, nombre=reemplazo_cups.nombre,
                                     capitulo=reemplazo_cups.capitulo, vigente=reemplazo_cups.vigente)
            return HomologacionOut(
                consulta=codigo, encontrado=True, estado="NO_VIGENTE",
                cups=CupsInfo(codigo=codigo, nombre=traz.descripcion_no_vigente,
                              capitulo="", vigente=False),
                mensaje=f"Codigo NO vigente. {traz.accion} {traz.codigo_reemplazo} "
                        f"({traz.descripcion_reemplazo}).",
                reemplazo=reemplazo,
            )
        return HomologacionOut(
            consulta=codigo, encontrado=False, estado="NO_ENCONTRADO",
            mensaje="El codigo no se encontro en la tabla de referencia CUPS vigente "
                    "ni en el registro de trazabilidad.",
        )

    # Caso 2: codigo vigente -> homologaciones segun permisos del usuario
    out = HomologacionOut(
        consulta=codigo, encontrado=True, estado="VIGENTE",
        cups=CupsInfo(codigo=cups.codigo, nombre=cups.nombre,
                      capitulo=cups.capitulo, vigente=cups.vigente),
        mensaje="Codigo CUPS vigente.",
    )
    if user.can_view_soat:
        soat_rows = db.query(Soat).filter(Soat.codigo_cups == codigo).all()
        out.soat = [SoatOut.model_validate(r) for r in soat_rows]
    if user.can_view_iss:
        iss_rows = db.query(Iss).filter(Iss.codigo_cups == codigo).all()
        out.iss = [_iss_to_out(r) for r in iss_rows]
    return out

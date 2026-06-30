"""
Exporta la hoja TRAZABILIDAD (CUPS retirados y su reemplazo) a CSV.

Entrada: archivo SOAT, hoja 'TRAZABILIDAD'
  Columnas: CODIGO (nuevo) | DESCRIPCION (nuevo) | ACCION | CODIGO (viejo) | DESCRIPCION (viejo)
  La accion tipica es "REEMPLAZA A": el codigo nuevo reemplaza al viejo (no vigente).
Salida: data/output/trazabilidad.csv
  codigo_no_vigente, descripcion_no_vigente, accion, codigo_reemplazo, descripcion_reemplazo
"""
import csv
from pathlib import Path

import openpyxl

XLSX = Path(r"H:\Mi unidad\0- SALUD\HOMOLOGADOR\01. Archivo homologación CUPS a SOAT - Año 2025.xlsx")
OUT = Path(__file__).resolve().parents[1] / "output" / "trazabilidad.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)


def clean(v):
    return str(v).strip() if v is not None else ""


def main():
    wb = openpyxl.load_workbook(XLSX, read_only=True)
    ws = wb["TRAZABILIDAD"]
    rows = []
    for i, r in enumerate(ws.iter_rows(min_row=2, values_only=True)):
        nuevo, desc_nuevo, accion, viejo, desc_viejo = (list(r) + [None] * 5)[:5]
        if not viejo:
            continue
        rows.append({
            "codigo_no_vigente": clean(viejo),
            "descripcion_no_vigente": clean(desc_viejo),
            "accion": clean(accion),
            "codigo_reemplazo": clean(nuevo),
            "descripcion_reemplazo": clean(desc_nuevo),
        })

    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.DictWriter(f, fieldnames=["codigo_no_vigente", "descripcion_no_vigente",
                                           "accion", "codigo_reemplazo", "descripcion_reemplazo"])
        wr.writeheader()
        wr.writerows(rows)

    print(f"Trazabilidad (no vigentes): {len(rows)}")
    print(f"Salida: {OUT}")


if __name__ == "__main__":
    main()

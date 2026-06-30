"""
Exporta la homologacion CUPS -> Manual SOAT 2025 a CSV normalizado.

Entrada: 01. Archivo homologacion CUPS a SOAT - Anio 2025.xlsx (hoja 'CUPS')
  Encabezados en fila 5, datos desde fila 6. Columnas (indice 0-based):
    18 CUPS VIGENTE | 20 DESCRIPCION SERVICIO | 24 COBERTURA
    26 Codigo SOAT  | 27 Descripcion SOAT     | 28 Clase
    31 Valor UVB (cantidad) | 32 Precio UVB (pesos a cobrar)
Salida: data/output/soat.csv
  codigo_cups, codigo_soat, descripcion_soat, clase, cobertura, uvb, valor_pesos
"""
import csv
from pathlib import Path

import openpyxl

XLSX = Path(r"H:\Mi unidad\0- SALUD\HOMOLOGADOR\01. Archivo homologación CUPS a SOAT - Año 2025.xlsx")
OUT = Path(__file__).resolve().parents[1] / "output" / "soat.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)

C_CUPS, C_DESC_SERV, C_COBERT = 18, 20, 24
C_SOAT, C_DESC_SOAT, C_CLASE = 26, 27, 28
C_UVB, C_PRECIO = 31, 32


def clean(v):
    return str(v).strip() if v is not None else ""


def main():
    wb = openpyxl.load_workbook(XLSX, read_only=True)
    ws = wb["CUPS"]
    rows = []
    con_soat = 0
    for r in ws.iter_rows(min_row=6, values_only=True):
        if len(r) <= C_PRECIO or r[C_CUPS] is None:
            continue
        codigo_cups = clean(r[C_CUPS])
        codigo_soat = clean(r[C_SOAT])
        if codigo_soat:
            con_soat += 1
        precio = r[C_PRECIO]
        try:
            valor = str(int(float(precio))) if precio not in (None, "") else ""
        except (ValueError, TypeError):
            valor = ""
        rows.append({
            "codigo_cups": codigo_cups,
            "codigo_soat": codigo_soat,
            "descripcion_soat": clean(r[C_DESC_SOAT]) or clean(r[C_DESC_SERV]),
            "clase": clean(r[C_CLASE]),
            "cobertura": clean(r[C_COBERT]),
            "uvb": clean(r[C_UVB]),
            "valor_pesos": valor,
        })

    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.DictWriter(f, fieldnames=["codigo_cups", "codigo_soat", "descripcion_soat",
                                           "clase", "cobertura", "uvb", "valor_pesos"])
        wr.writeheader()
        wr.writerows(rows)

    con_valor = sum(1 for r in rows if r["valor_pesos"])
    print(f"SOAT total filas: {len(rows)} | con codigo SOAT: {con_soat} | con valor: {con_valor}")
    print(f"CUPS unicos: {len({r['codigo_cups'] for r in rows})}")
    print(f"Salida: {OUT}")


if __name__ == "__main__":
    main()

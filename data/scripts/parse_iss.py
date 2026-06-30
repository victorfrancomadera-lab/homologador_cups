"""
Parser del Manual Tarifario ISS 2001 (Acuerdo 256 de 2001) - 213 paginas.

El manual mezcla dos tipos de valor segun el capitulo, distinguibles por el
encabezado de columna de cada pagina:
  - "UVR"   -> Capitulo I: procedimientos quirurgicos en Unidades de Valor Relativo
  - "VALOR" -> Capitulos II-IV: laboratorio, imagenologia, radioterapia,
               internacion, rehabilitacion, etc. -> valor directo en PESOS 2001
  - Cap V (paginas finales) es texto legal sin tablas tarifarias -> se ignora.

Estructura de columnas (coordenada x), consistente en todo el manual:
  - REF.        x ~90-135  : codigo de referencia ISS
  - CODIGO      x ~135-191 : codigo CUPS (enlace con la tabla CUPS del usuario)
  - DESCRIPCION x ~191-470
  - UVR/VALOR   x >470      : valor (UVR entero, o pesos con separador de miles)

Conversion UVR -> pesos 2001 (Art. 59), segun rol profesional:
  ESPECIALISTA=1270, ANESTESIA=960, AYUDANTE=360, GENERAL=810

Salida: data/output/iss2001.csv
  codigo_iss, clase, codigo_cups, descripcion, tipo_valor, uvr, valor_pesos
"""
import csv
import re
from pathlib import Path

import pdfplumber

PDF_PATH = Path(r"C:\Users\vfran\Downloads\TARIFAS ISS 2001.pdf")
OUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = OUT_DIR / "iss2001.csv"

X_ISS_MAX = 135
X_CLASE_MAX = 156
X_CUPS_MAX = 191
X_VALOR_MIN = 470

CODE_RE = re.compile(r"^[A-Z]?\d{3,7}$")          # ref o cups (a veces con letra)
NUM_RE = re.compile(r"^\d{1,3}(?:\.\d{3})*$|^\d{1,7}$")  # 380 | 1.200 | 188.800

NOISE = ("ACUERDO", "Diciembre", "POR EL CUAL", "MANUAL DE TARIFAS",
         "EPS-ISS", "REF.", "DESCRIPCION", "CONSIDERANDO", "ARTICULO",
         "PARAGRAFO", "CAPITULO", "---", "ACUERDA")


def detect_mode(words):
    """Devuelve 'UVR', 'PESOS' o None segun el encabezado de la pagina."""
    for w in words:
        if w["x0"] >= X_VALOR_MIN and w["top"] < 130:
            t = w["text"].strip().upper()
            if t == "UVR":
                return "UVR"
            if t == "VALOR":
                return "PESOS"
    return None


def group_lines(words, tol=3.0):
    lines, current, last_top = [], [], None
    for w in sorted(words, key=lambda x: (round(x["top"]), x["x0"])):
        if last_top is None or abs(w["top"] - last_top) <= tol:
            current.append(w)
            if last_top is None:
                last_top = w["top"]
        else:
            lines.append(current)
            current, last_top = [w], w["top"]
    if current:
        lines.append(current)
    return lines


def parse_line(words):
    iss = clase = cups = valor = None
    desc_parts = []
    for w in sorted(words, key=lambda x: x["x0"]):
        x, t = w["x0"], w["text"].strip()
        if not t:
            continue
        if x < X_ISS_MAX and iss is None and CODE_RE.match(t):
            iss = t
        elif x < X_CLASE_MAX and clase is None and t.isalpha() and len(t) <= 3:
            clase = t
        elif X_ISS_MAX <= x < X_CUPS_MAX and cups is None and CODE_RE.match(t):
            cups = t
        elif x >= X_VALOR_MIN and valor is None and NUM_RE.match(t):
            valor = t.replace(".", "")
        else:
            desc_parts.append(t)
    desc = " ".join(desc_parts).strip()
    if any(n in desc for n in NOISE):
        return ("ruido", None)
    if cups and valor:
        return ("registro", {"codigo_iss": iss or "", "clase": clase or "",
                              "codigo_cups": cups, "descripcion": desc, "valor": valor})
    if desc and not iss and not cups and not valor and not desc.upper().startswith("INCLUYE"):
        return ("continuacion", desc)
    return ("ruido", None)


def main():
    rows = []
    pages_uvr = pages_pesos = pages_skip = 0
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            words = page.extract_words(use_text_flow=False)
            mode = detect_mode(words)
            if mode is None:
                pages_skip += 1
                continue
            pages_uvr += mode == "UVR"
            pages_pesos += mode == "PESOS"
            for line in group_lines(words):
                kind, data = parse_line(line)
                if kind == "registro":
                    data["tipo_valor"] = mode
                    rows.append(data)
                elif kind == "continuacion" and rows:
                    rows[-1]["descripcion"] = (rows[-1]["descripcion"] + " " + data).strip()

    # columnas finales: uvr y valor_pesos separados
    final = []
    for r in rows:
        v = int(r["valor"])
        if r["tipo_valor"] == "UVR":
            final.append({**{k: r[k] for k in ("codigo_iss", "clase", "codigo_cups", "descripcion")},
                          "tipo_valor": "UVR", "uvr": v, "valor_pesos": ""})
        else:
            # valores < 100 son artefactos de parseo (notas al pie capturadas)
            tipo = "PESOS" if v >= 100 else "POR_VERIFICAR"
            final.append({**{k: r[k] for k in ("codigo_iss", "clase", "codigo_cups", "descripcion")},
                          "tipo_valor": tipo, "uvr": "", "valor_pesos": v if v >= 100 else ""})

    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.DictWriter(f, fieldnames=["codigo_iss", "clase", "codigo_cups",
                                           "descripcion", "tipo_valor", "uvr", "valor_pesos"])
        wr.writeheader()
        wr.writerows(final)

    uvr_rows = [r for r in final if r["tipo_valor"] == "UVR"]
    pes_rows = [r for r in final if r["tipo_valor"] == "PESOS"]
    print(f"Paginas: UVR={pages_uvr} PESOS={pages_pesos} ignoradas={pages_skip}")
    print(f"Total registros: {len(final)}")
    print(f"  UVR (quirurgico): {len(uvr_rows)}  | rango UVR: "
          f"{min(r['uvr'] for r in uvr_rows)}-{max(r['uvr'] for r in uvr_rows)}")
    print(f"  PESOS (lab/img/etc): {len(pes_rows)} | rango $: "
          f"{min(r['valor_pesos'] for r in pes_rows)}-{max(r['valor_pesos'] for r in pes_rows)}")
    print(f"  CUPS unicos: {len({r['codigo_cups'] for r in final})}")
    print(f"Salida: {OUT_CSV}")


if __name__ == "__main__":
    main()

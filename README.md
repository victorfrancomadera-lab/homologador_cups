# Homologador CUPS · SOAT / ISS 2001

Aplicación web para consultar la **vigencia de códigos CUPS** (Colombia) y sus
**equivalencias tarifarias** en el Manual SOAT vigente y el Manual ISS 2001
(Acuerdo 256 de 2001), con sus descripciones y valores a cobrar.

Incluye **autenticación** y un **panel de administración** donde el administrador
crea usuarios y define qué equivalencias puede consultar cada uno.

---

## ¿Qué hace?

El usuario ingresa un código CUPS (o busca por nombre) y la app responde:

- **Estado de vigencia**: `VIGENTE`, `NO VIGENTE` (con su código de reemplazo) o `NO ENCONTRADO`.
- **Equivalencia SOAT** (Manual SOAT 2025): código, descripción, clase, cobertura, UVB y **valor a cobrar en pesos**.
- **Equivalencia ISS 2001** (Acuerdo 256/2001):
  - Procedimientos **quirúrgicos**: puntos **UVR** + valor en pesos 2001 calculado para los 4 roles profesionales (especialista $1.270, anestesia $960, ayudante $360, general $810 por UVR — Art. 59).
  - Laboratorio, imágenes, etc.: **valor directo en pesos 2001**.

---

## Datos incluidos

| Fuente | Registros | Origen |
|---|---|---|
| CUPS vigentes | 10.024 | Tabla de referencia SISPRO/Minsalud |
| Homologación SOAT 2025 | 11.745 (8.555 con valor) | Archivo de homologación CUPS→SOAT |
| ISS 2001 | 5.503 (3.317 UVR + 2.184 pesos) | Manual Tarifario ISS 2001 (PDF Acuerdo 256/2001) |
| Trazabilidad (no vigentes) | 624 | Hoja TRAZABILIDAD del archivo SOAT |

Los datos procesados viven como CSV en [`backend/seed_data/`](backend/seed_data) y se
cargan automáticamente a la base de datos la primera vez que arranca la app.

---

## Arquitectura

```
Navegador ──HTTPS──► Servicio web (Railway)
                     ├── FastAPI (API /api/*)
                     └── React compilado (SPA, mismo origen)
                            │
                            └──► PostgreSQL (Railway)
```

- **Backend**: Python + FastAPI + SQLAlchemy. Auth con JWT (bcrypt).
- **Frontend**: React + Vite (servido como estáticos por el backend → un solo servicio).
- **Base de datos**: PostgreSQL (en local usa SQLite por defecto).

---

## Despliegue en Railway

1. Sube este repositorio a GitHub.
2. En [Railway](https://railway.app): **New Project → Deploy from GitHub repo**.
   Railway detecta el `Dockerfile` y `railway.json` automáticamente.
3. En el proyecto, **+ New → Database → PostgreSQL**.
4. En el servicio web, pestaña **Variables**, define:

   | Variable | Valor |
   |---|---|
   | `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |
   | `SECRET_KEY` | (una clave aleatoria larga) |
   | `ADMIN_USERNAME` | tu usuario admin |
   | `ADMIN_PASSWORD` | tu contraseña admin |
   | `ADMIN_EMAIL` | tu correo |
   | `ADMIN_FULL_NAME` | tu nombre |

   Genera el `SECRET_KEY` con:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
5. Railway construye y despliega. En **Settings → Networking → Generate Domain**
   obtienes la URL pública.
6. Entra con el usuario/contraseña admin. Desde **Usuarios** crea las demás cuentas.

> La base de datos se siembra sola en el primer arranque (idempotente: no duplica
> datos en reinicios). El superadmin se crea con las variables `ADMIN_*`.

---

## Desarrollo local

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate           # Windows  (o: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env            # ajusta valores si quieres
uvicorn app.main:app --reload --port 8000
```
La API queda en `http://127.0.0.1:8000` (docs en `/docs`). Usa SQLite local.

### Frontend
```bash
cd frontend
npm install
npm run dev                       # http://127.0.0.1:5173 (proxy /api al backend)
```

---

## Actualizar los datos

Cuando salgan nuevas versiones (tabla CUPS de SISPRO, Manual SOAT, etc.):

1. Descarga los archivos actualizados.
2. Ajusta las rutas en los scripts de [`data/scripts/`](data/scripts) si cambian.
3. Regenera los CSV:
   ```bash
   python data/scripts/export_cups.py
   python data/scripts/export_soat.py
   python data/scripts/export_trazabilidad.py
   python data/scripts/parse_iss.py        # solo si cambia el manual ISS
   ```
4. Copia los CSV a la semilla y vuelve a desplegar:
   ```bash
   copy data\output\*.csv backend\seed_data\
   ```
5. Para forzar la recarga en una BD ya sembrada, vacía las tablas correspondientes
   (o usa una BD nueva). La siembra solo carga tablas vacías.

> **Tabla CUPS oficial siempre actualizada:** SISPRO → Minsalud → *Tablas de referencia*.
> Si la descargas incluyendo códigos deshabilitados, el sistema también marcará como
> `NO VIGENTE` los que tengan `Habilitado = NO`.

---

## Notas sobre la homologación ISS 2001

- El valor del UVR en pesos no cambia: corresponde al fijado en el Acuerdo 256 de 2001 (Art. 59).
- Para procedimientos quirúrgicos se muestran los 4 valores por rol porque el pago
  depende de quién ejecuta el acto.
- 2 registros del manual (ultrasonografías) quedaron marcados como *"valor por verificar"*
  por un artefacto del PDF original; representan el 0,04 % del total.
- La equivalencia CUPS↔ISS proviene del propio manual, que lista el código CUPS junto a cada ítem.

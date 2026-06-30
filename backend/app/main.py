"""Punto de entrada de la API del Homologador CUPS."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings
from .routers import admin, auth, search
from .seed import run_seed

# Carpeta con el frontend compilado (frontend/dist), copiado al contenedor.
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend_dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # La siembra no debe impedir que la app arranque: si falla (p. ej. la base
    # de datos aun no esta lista), se registra el error pero el servidor sigue
    # vivo para responder el healthcheck. Reintentara sembrar en el proximo boot.
    try:
        run_seed()  # crea tablas, carga datos y superadmin (idempotente)
    except Exception as exc:  # noqa: BLE001
        import traceback
        print("ERROR durante la siembra inicial:", exc)
        traceback.print_exc()
    yield


app = FastAPI(
    title="Homologador CUPS - SOAT / ISS 2001",
    description="Consulta de vigencia de codigos CUPS y sus equivalencias "
                "en el Manual Tarifario SOAT y el Manual ISS 2001 (Acuerdo 256/2001).",
    version="1.0.0",
    lifespan=lifespan,
)

origins = ["*"] if settings.cors_origins.strip() == "*" else \
    [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(search.router)
app.include_router(admin.router)


@app.get("/api/health", tags=["sistema"])
def health():
    return {"status": "ok"}


# ---- Servir el SPA de React (si esta compilado) ----
if (FRONTEND_DIR / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.exception_handler(StarletteHTTPException)
    async def spa_fallback(request, exc):
        # Para rutas del cliente (no /api) que devuelven 404, sirve el index.html
        if exc.status_code == 404 and not request.url.path.startswith("/api"):
            return FileResponse(FRONTEND_DIR / "index.html")
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    @app.get("/", include_in_schema=False)
    async def root():
        return FileResponse(FRONTEND_DIR / "index.html")

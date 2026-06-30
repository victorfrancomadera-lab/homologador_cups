"""Configuracion via variables de entorno (Railway)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base de datos (Railway inyecta DATABASE_URL en el servicio Postgres)
    database_url: str = "sqlite:///./cups_local.db"

    # Seguridad
    secret_key: str = "CAMBIAR-ESTA-CLAVE-EN-PRODUCCION"
    access_token_expire_minutes: int = 60 * 8  # 8 horas
    algorithm: str = "HS256"

    # Superadministrador inicial (se crea al sembrar la BD)
    admin_username: str = "admin"
    admin_password: str = "admin123"
    admin_email: str = "admin@homologador.local"
    admin_full_name: str = "Administrador"

    # CORS: origen del frontend (coma-separado). "*" permite todos.
    cors_origins: str = "*"

    # Valor en pesos por UVR (Art. 59, Manual ISS 2001) segun rol profesional
    uvr_especialista: int = 1270
    uvr_anestesia: int = 960
    uvr_ayudante: int = 360
    uvr_general: int = 810


settings = Settings()

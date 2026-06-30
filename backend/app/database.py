"""Motor SQLAlchemy y sesion."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

# Railway/Heroku usan el prefijo "postgres://"; SQLAlchemy requiere "postgresql://"
url = settings.database_url
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
engine = create_engine(url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

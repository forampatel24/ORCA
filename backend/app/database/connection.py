"""DB connection - docs 05_DATABASE_DESIGN, 20_DATABSE_ARCHITECTURE."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def psycopg_conninfo() -> str:
    """psycopg conninfo derived from DATABASE_URL so host/port follow env.

    Team default is localhost:5432 (docker). Machines with a native postgres
    on 5432 use the override mapping localhost:5433 (see docker-compose.override.yml).
    """
    import os
    from urllib.parse import urlparse

    url = os.getenv("DATABASE_URL", "") or getattr(settings, "database_url", "")
    if url.startswith("postgresql"):
        url = url.replace("postgresql+psycopg://", "postgresql://")
        try:
            p = urlparse(url)
            return (
                f"host={p.hostname or 'localhost'} port={p.port or 5432} "
                f"dbname={(p.path or '/orca_db').lstrip('/')} "
                f"user={p.username or 'postgres'} password={p.password or 'postgres'}"
            )
        except Exception:
            pass
    return "host=localhost dbname=orca_db user=postgres password=postgres"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.models.base import Base

# PostgreSQL engine (locale)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# SQL Server engine (gestionale) - opzionale, verrà creato solo se disponibile
sqlserver_engine = None
SessionGestionale = None

try:
    sqlserver_engine = create_engine(
        settings.SQLSERVER_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    SessionGestionale = sessionmaker(autocommit=False, autoflush=False, bind=sqlserver_engine)
except Exception as e:
    print(f"Warning: SQL Server connection not available: {e}")
    print("Continuando solo con PostgreSQL locale...")

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency per ottenere sessione database locale"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_gestionale() -> Session:
    """Dependency per ottenere sessione database gestionale"""
    if SessionGestionale is None:
        raise Exception("SQL Server connection not configured")
    db = SessionGestionale()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inizializza il database creando tutte le tabelle"""
    Base.metadata.create_all(bind=engine)

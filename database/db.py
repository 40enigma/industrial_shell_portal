"""
SQLite database engine and session configuration.
Uses SQLAlchemy with a local SQLite file.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# Database file lives alongside the database package
DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "industrial_shells.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite + FastAPI
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(drop_first: bool = False):
    """Create all tables, optionally dropping first for schema updates."""
    from database.models import Shell, Document, IngestionBatch  # noqa: F401
    if drop_first:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

"""
Database setup for SQLAlchemy with SQLite (local file by default).
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from .config import get_settings

settings = get_settings()

# Determine if using SQLite to set appropriate connect args
is_sqlite = settings.database_url.startswith("sqlite")

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    echo=False,
    # For SQLite, `check_same_thread` must be False when using the connection across threads
    connect_args={"check_same_thread": False} if is_sqlite else {},
    pool_pre_ping=not is_sqlite,
    pool_recycle=3600 if not is_sqlite else None,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base
Base = declarative_base()


# PUBLIC_INTERFACE
@contextmanager
def get_db_session() -> Session:
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

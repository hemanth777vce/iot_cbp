import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from config import DATABASE_URL, DEFAULT_SETTINGS

Base = declarative_base()

_engine = None
_SessionFactory = None
_scoped_session = None

def get_engine(db_url=None):
    global _engine
    if _engine is None or db_url is not None:
        target_url = db_url or DATABASE_URL
        # Ensure SQLite handles threads properly
        connect_args = {"check_same_thread": False} if target_url.startswith("sqlite") else {}
        _engine = create_engine(target_url, echo=False, connect_args=connect_args)
    return _engine

def get_session_factory(db_url=None):
    global _SessionFactory, _scoped_session
    engine = get_engine(db_url)
    _SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    _scoped_session = scoped_session(_SessionFactory)
    return _scoped_session

def get_db():
    if _scoped_session is None:
        get_session_factory()
    return _scoped_session

@contextmanager
def get_db_session(db_url=None):
    """Context manager for database sessions with automatic commit/rollback."""
    if db_url or _scoped_session is None:
        factory = get_session_factory(db_url)
    else:
        factory = _scoped_session
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def init_db(db_url=None):
    """Initialize database tables safely without dropping existing tables."""
    import models  # Ensure all models are registered
    engine = get_engine(db_url)
    Base.metadata.create_all(bind=engine)
    
    # Initialize default settings if not present
    with get_db_session(db_url) as session:
        from models import AppSetting
        for key, val in DEFAULT_SETTINGS.items():
            existing = session.query(AppSetting).filter_by(key=key).first()
            if not existing:
                session.add(AppSetting(key=key, value=str(val)))

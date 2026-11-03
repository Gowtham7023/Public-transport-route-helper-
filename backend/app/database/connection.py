import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

# Configure engine based on connection string
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True
    )
except Exception as e:
    logger.warning(f"Could not connect using primary DATABASE_URL ({settings.DATABASE_URL}): {e}. Falling back to SQLite.")
    engine = create_engine("sqlite:///./transit_app.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all tables if they don't exist yet and ensure schema columns."""
    import app.models.models  # ensure models are imported
    Base.metadata.create_all(bind=engine)
    
    # Graceful column migrations for existing installations
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE stations ADD COLUMN station_type VARCHAR(50) DEFAULT "railway"'))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text('ALTER TABLE stations ADD COLUMN place_id VARCHAR(100)'))
            conn.commit()
        except Exception:
            pass

    logger.info("Database initialized successfully.")


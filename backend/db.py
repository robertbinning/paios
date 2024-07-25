# database helper functions
import os
import logging
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from alembic import command
from alembic.config import Config as AlembicConfig
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Define the SQLAlchemy Base
Base = declarative_base()

# Create engine
DATABASE_URL = "sqlite:///../data/paios.db"
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# use alembic to create the database or migrate to the latest schema
def init_db():
    logger.info("Initializing database.")
    alembic_cfg = AlembicConfig()
    os.makedirs("migrations", exist_ok=True)
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(alembic_cfg, "head")

@contextmanager
def db_session_context():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

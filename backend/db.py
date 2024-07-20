# database helper functions
import os
import aiosqlite
import logging
from alembic import command
from alembic.config import Config as AlembicConfig
from common.paths import base_dir, db_path

logger = logging.getLogger(__name__)

# use alembic to create the database or migrate to the latest schema
def init_db():
    logger.info("Initializing database.")
    alembic_cfg = AlembicConfig()
    os.makedirs(db_path.parent, exist_ok=True)
    alembic_cfg.set_main_option("script_location", str(base_dir / "migrations"))
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")

# Call init_db() when the module is first imported
init_db()

async def execute_query(query, params=None):
    # TODO: logger.adebug from structlog
    logger.debug(f"Executing query: {query} with params: {params}")
    async with aiosqlite.connect(db_path) as conn:
        async with conn.cursor() as cursor:
            try:
                await cursor.execute(query, params or ())
                result = await cursor.fetchall()
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                raise e

    return result

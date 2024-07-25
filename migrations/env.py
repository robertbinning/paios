from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from pathlib import Path
import os

# Check if the environment is set up correctly
def check_env():
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        print("Error: Running under the system python ({})\n".format(sys.prefix))
        venv_path = Path(__file__).resolve().parent.parent / '.venv'
        if not venv_path.exists():
            print("No virtual environment found at {} so you will need to create one.".format(venv_path))
            if os.name == "posix": # Linux/Mac
                print("\nYou can use the scripts/setup_environment.sh script to do this, or do it manually:")
                print("    python3 -m venv .venv")
                print("    source .venv/bin/activate")
                print("    pip install -r backend/requirements.txt")
            elif os.name == "nt": # Windows
                print("\nYou can use the scripts\\setup_environment.ps1 script to do this, or do it manually from the root directory:\n")
                print("    python -m venv .venv")
                print("    .venv\\Scripts\\activate")
                print("    pip install -r backend\\requirements.txt\n")
            sys.exit(1)
        else:
            print(f"Virtual environment found at {venv_path}. You can activate it with:\n")
            if os.name == "posix": # Linux/Mac
                print(f"    source {venv_path}/bin/activate")
            elif os.name == "nt": # Windows
                print(f"    {venv_path}\\Scripts\\activate.ps1")
            print(f"\nOnce you have activated the virtual environment, run this again.")
            sys.exit(1)

    required_modules = ['connexion', 'uvicorn', 'sqlalchemy', 'alembic', 'aiosqlite']
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            print(f"Required module {module} is not installed.")
            sys.exit(1)

check_env()

# Alembic Config object
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Import your SQLAlchemy models here and set the target_metadata
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))
from backend.models import Base  

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
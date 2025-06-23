import os
import sys
from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your Base from the correct location
from app.db.postgres.models import Base
target_metadata = Base.metadata

# Explicitly import all models to ensure they're registered
from app.db.postgres.models import Book  # noqa
from app.db.postgres.models import User  # noqa
from app.db.postgres.models import Rating  # noqa
from app.db.postgres.models import Interaction  # noqa
from app.db.postgres.models import Recommendation  # noqa

# Это нужно, чтобы избежать ошибки с formatters
try:
    fileConfig(context.config.config_file_name)
except KeyError:
    pass  # Пропускаем ошибку конфигурации логгирования




def run_migrations_online():
    connectable = create_engine(context.config.get_main_option("sqlalchemy.url"))

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()

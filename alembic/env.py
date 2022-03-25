from logging.config import fileConfig

from sqlalchemy import create_engine
from alembic import context

from dependencies import DATABASE_URL, DATABASE_URL_SYNC
from models.models import metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = metadata


def run_migrations_offline():

    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        user_module_prefix='sa.'
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():

    connectable = create_engine(DATABASE_URL_SYNC)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            user_module_prefix='sa.'
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

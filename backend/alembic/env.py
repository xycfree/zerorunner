import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool

from alembic import context
from sqlalchemy.ext.asyncio import AsyncEngine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# alembic async 配置参考
# https://github.com/jonra1993/fastapi-alembic-sqlmodel-async/blob/main/backend/app/alembic/env.py

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(f"当前路径:{BASE_DIR}")
# /Users/xxxx/python_code/project

sys.path.insert(0, BASE_DIR)

# SQLALCHEMY 模式需要导入 Base
from autotest.models.base import Base
from config import config as con

target_metadata = Base.metadata  # SQLALCHEMY 模式同步


# target_metadata = SQLModel.metadata  # sqlmodel 模式同步


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = con.DATABASE_URI or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = AsyncEngine(create_engine(con.DATABASE_URI, echo=True, future=True))

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    # configuration = config.get_section(config.config_ini_section)
    # configuration["sqlalchemy.url"] = con.DATABASE_URI

    # connectable = engine_from_config(
    #     configuration,
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )
    #
    # with connectable.connect() as connection:
    #     context.configure(
    #         connection=connection, target_metadata=target_metadata
    #     )
    #
    #     with context.begin_transaction():
    #         context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # run_migrations_online()
    asyncio.run(run_migrations_online())

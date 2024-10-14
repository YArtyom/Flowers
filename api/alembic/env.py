import asyncio
import sys
import os
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from alembic import context

# Добавляем путь к проекту, чтобы импортировать модули
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import DATABASE_URL, Base
from app.modules.customer.models import Customer
from app.modules.product.models import Product
from app.modules.basket.models import Basket
from app.modules.order.models import Order
from app.modules.basket_item.models import BasketItem

# Конфигурация Alembic
config = context.config

# Интерпретация файла конфигурации для логирования.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные моделей для 'autogenerate' поддержки
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме."""
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме."""
    from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async def run_migrations() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()

    asyncio.run(run_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

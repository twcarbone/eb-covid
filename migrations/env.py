import logging
import re
from logging.config import fileConfig

import sqlalchemy as sa
from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from config import Config

USE_TWOPHASE = False

# this is the Alembic Config object, which provides access to the values within the .ini
# file in use.
config = context.config

# Interpret the config file for Python logging. This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")


# If a db section is passed using the '-x' option, only target that database for the
# migration. Otherwise, target all databases.
cmd_kwargs = context.get_x_argument(as_dictionary=True)
if cmd_kwargs:
    db_names = [cmd_kwargs["db"]]
else:
    db_names = re.split(r",\s*", config.get_main_option("databases"))

# add your model's MetaData objects here for 'autogenerate' support.  These must be set up
# to hold just those tables targeting a particular database. table.tometadata() may be
# helpful here in case a "copy" of a MetaData is needed.
from app import models

target_metadata = {
    "dev": models.DeclBase.metadata,
    "test": models.DeclBase.metadata,
    "prod": models.DeclBase.metadata,
}

urls = {
    "dev": Config.DB_URI_DEV,
    "test": Config.DB_URI_TEST,
    "prod": Config.DB_URI_PROD,
}


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # for the --sql use case, run migrations for each URL into
    # individual files.

    engines = {}
    for name in db_names:
        engines[name] = rec = {}
        rec["url"] = urls.get(name)

    for name, rec in engines.items():
        logger.info("Migrating database %s" % name)
        file_ = "%s.sql" % name
        logger.info("Writing output to %s" % file_)
        with open(file_, "w") as buffer:
            context.configure(
                url=rec["url"],
                output_buffer=buffer,
                target_metadata=target_metadata.get(name),
                literal_binds=True,
                dialect_opts={"paramstyle": "named"},
            )
            with context.begin_transaction():
                context.run_migrations(engine_name=name)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # for the direct-to-DB use case, start a transaction on all
    # engines, then run all migrations, then commit all transactions.

    engines = {}
    for name in db_names:
        engines[name] = rec = {}
        rec["engine"] = sa.create_engine(url=urls.get(name))

    for name, rec in engines.items():
        engine = rec["engine"]
        rec["connection"] = conn = engine.connect()

        if USE_TWOPHASE:
            rec["transaction"] = conn.begin_twophase()
        else:
            rec["transaction"] = conn.begin()

    try:
        for name, rec in engines.items():
            logger.info("Migrating database %s" % name)
            context.configure(
                connection=rec["connection"],
                upgrade_token="%s_upgrades" % name,
                downgrade_token="%s_downgrades" % name,
                target_metadata=target_metadata.get(name),
            )
            context.run_migrations(engine_name=name)

        if USE_TWOPHASE:
            for rec in engines.values():
                rec["transaction"].prepare()

        for rec in engines.values():
            rec["transaction"].commit()
    except:
        for rec in engines.values():
            rec["transaction"].rollback()
        raise
    finally:
        for rec in engines.values():
            rec["connection"].close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

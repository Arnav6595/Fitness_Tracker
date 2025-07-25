import logging
from logging.config import fileConfig

from flask import current_app
from alembic import context

# Fix: Added all necessary imports from SQLAlchemy
from sqlalchemy import create_engine, text, exc, Column, String, PrimaryKeyConstraint
from sqlalchemy.schema import Table, MetaData

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine():
    try:
        # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # this works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db


def get_metadata():
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""

    # Get the database URL from the Flask app config
    db_url = get_engine_url()

    # --- Forceful Pre-configuration ---
    # Create a temporary engine to set up the schema and version table
    pre_engine = create_engine(db_url, isolation_level='AUTOCOMMIT')
    with pre_engine.connect() as pre_connection:
        try:
            # Create the schema if it doesn't exist
            pre_connection.execute(text("CREATE SCHEMA IF NOT EXISTS neondb"))
            print("Schema 'neondb' created or already exists.")
        except exc.SQLAlchemyError as e:
            print(f"Could not create schema 'neondb'. This may be fine if it exists. Error: {e}")

        # Manually create the alembic_version table within the correct schema
        meta = MetaData()
        Table(
            'alembic_version',
            meta,
            Column('version_num', String(32), nullable=False),
            PrimaryKeyConstraint('version_num', name='alembic_version_pkc'),
            schema='neondb'
        )
        meta.create_all(pre_connection)
        print("Table 'neondb.alembic_version' created or already exists.")
    pre_engine.dispose()
    # --- End of Forceful Pre-configuration ---

    # Proceed with the standard Alembic process
    connectable = get_engine()
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            version_table_schema="neondb",
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()




# import logging
# from logging.config import fileConfig
# from sqlalchemy import text

# from flask import current_app

# from alembic import context

# # this is the Alembic Config object, which provides
# # access to the values within the .ini file in use.
# config = context.config

# # Interpret the config file for Python logging.
# # This line sets up loggers basically.
# fileConfig(config.config_file_name)
# logger = logging.getLogger('alembic.env')


# def get_engine():
#     try:
#         # this works with Flask-SQLAlchemy<3 and Alchemical
#         return current_app.extensions['migrate'].db.get_engine()
#     except (TypeError, AttributeError):
#         # this works with Flask-SQLAlchemy>=3
#         return current_app.extensions['migrate'].db.engine


# def get_engine_url():
#     try:
#         return get_engine().url.render_as_string(hide_password=False).replace(
#             '%', '%%')
#     except AttributeError:
#         return str(get_engine().url).replace('%', '%%')


# # add your model's MetaData object here
# # for 'autogenerate' support
# # from myapp import mymodel
# # target_metadata = mymodel.Base.metadata
# config.set_main_option('sqlalchemy.url', get_engine_url())
# target_db = current_app.extensions['migrate'].db

# # other values from the config, defined by the needs of env.py,
# # can be acquired:
# # my_important_option = config.get_main_option("my_important_option")
# # ... etc.


# def get_metadata():
#     if hasattr(target_db, 'metadatas'):
#         return target_db.metadatas[None]
#     return target_db.metadata


# def run_migrations_offline():
#     """Run migrations in 'offline' mode.

#     This configures the context with just a URL
#     and not an Engine, though an Engine is acceptable
#     here as well.  By skipping the Engine creation
#     we don't even need a DBAPI to be available.

#     Calls to context.execute() here emit the given string to the
#     script output.

#     """
#     url = config.get_main_option("sqlalchemy.url")
#     context.configure(
#         url=url, target_metadata=get_metadata(), literal_binds=True
#     )

#     with context.begin_transaction():
#         context.run_migrations()


# def run_migrations_online():
#     def process_revision_directives(context, revision, directives):
#         if getattr(config.cmd_opts, "autogenerate", False):
#             script = directives[0]
#             if script.upgrade_ops.is_empty():
#                 directives[:] = []
#                 logger.info("No changes in schema detected.")

#     conf_args = current_app.extensions["migrate"].configure_args
#     if conf_args.get("process_revision_directives") is None:
#         conf_args["process_revision_directives"] = process_revision_directives

#     connectable = get_engine()

#     def do_migrations(connection):
#         connection.execute(text("CREATE SCHEMA IF NOT EXISTS neondb"))
#         connection.execute(text("SET search_path TO neondb"))

#         context.configure(
#             connection=connection,
#             target_metadata=get_metadata(),
#             version_table_schema="neondb",  # Very important!
#             include_schemas=True,
#             **conf_args,
#         )

#         with context.begin_transaction():
#             context.run_migrations()

#     with connectable.connect() as connection:
#         connection = connection.execution_options(isolation_level="AUTOCOMMIT")
#         do_migrations(connection)







# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()

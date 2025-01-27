"""Periferals required for SQLAlchemy to function."""

import contextvars

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from src.config import Config


config = Config()

# will allow us to connect to PostgreSQL database
engine = create_engine(config.DATABASE_CONNECTION_URL,
                       pool_size = 20,
                       max_overflow = 30,
                       pool_timeout = 30,
                       pool_recycle = 1800)

# will allow us to send SQL queries to database associated with engine
_session = scoped_session(sessionmaker(bind=engine))

# will allow us to map relation tables from PostgreSQL to python classes
# each model must inherit this Base class
Base = declarative_base()


# Permite parchear fácilmente la sesión de la base de datos para el entorno de pruebas
# mediante session_var.set() y session_var.get() que se utilizan para recuperar la sesión
# o establecerla
session_var = contextvars.ContextVar("session", default=_session)

#definimos una función para llamar a la sesion de forma directa
def get_session():
    """Función para obtener la sesión en la base de datos"""
    return _session
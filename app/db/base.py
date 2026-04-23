# app/db/base.py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    All models inherit from this Base.
    SQLAlchemy uses it to track all tables.
    """
    pass


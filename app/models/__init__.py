# app/models/__init__.py
# Central registration point: importing this package (or anything from it)
# guarantees every model is loaded, so SQLAlchemy's relationship() string
# resolution always has the full picture. Add new models here as the
# project grows. This file must never be imported by base.py or by any
# individual model file — only by scripts, Alembic's env.py, or main.py —
# to avoid the circular import this exact structure caused once already.

from app.models.user import User
from app.models.paper import Paper
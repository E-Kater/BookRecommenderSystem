# app/db/base.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Автоматический импорт всех моделей
#from app.db.postgres.models import Book, User, Recommendation, Rating, Interaction  # noqa
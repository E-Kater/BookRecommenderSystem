from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#from app.db.postgres.models import Book, User, Recommendation, Rating, Interaction

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@host.docker.internal/bookdb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

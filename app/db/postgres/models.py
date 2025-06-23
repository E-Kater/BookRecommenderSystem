from sqlalchemy import Column, Integer, String, Text, Float, ARRAY, Boolean, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid


class Book(Base):
    __tablename__ = 'books'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    description = Column(Text)
    isbn = Column(String(20), unique=True)
    publish_year = Column(Integer)
    genres = Column(ARRAY(String))  # Array of genres
    average_rating = Column(Float, default=0.0)
    cover_image_url = Column(String(255))
    language = Column(String(50))
    page_count = Column(Integer)

    def __repr__(self):
        return f"<Book {self.title} by {self.author}>"


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User {self.username}>"


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey('books.id'), nullable=False)
    rating = Column(Float, nullable=False)  # Typically 0-5 scale
    rated_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Rating {self.rating} for book {self.book_id} by user {self.user_id}>"


class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey('books.id'), nullable=False)
    score = Column(Float, nullable=False)  # Recommendation strength score
    algorithm = Column(String(50))  # e.g., 'collaborative', 'content-based'
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Recommendation {self.book_id} to {self.user_id} with score {self.score}>"


class Interaction(Base):
    __tablename__ = 'interactions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey('books.id'), nullable=False)
    interaction_type = Column(String(20), nullable=False)  # 'view', 'click', 'purchase', etc.
    interacted_at = Column(DateTime(timezone=True), server_default=func.now())
    duration = Column(Float)  # Seconds spent on the book

    def __repr__(self):
        return f"<Interaction {self.interaction_type} on {self.book_id} by {self.user_id}>"

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, confloat


class BookCreate(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    isbn: str
    publish_year: Optional[int] = None
    genres: Optional[List[str]] = None
    cover_image_url: Optional[str] = None
    language: Optional[str] = None
    page_count: Optional[int] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    isbn: Optional[str] = None
    publish_year: Optional[int] = None
    genres: Optional[List[str]] = None
    average_rating: Optional[float] = None
    cover_image_url: Optional[str] = None
    language: Optional[str] = None
    page_count: Optional[int] = None


class RatingBase(BaseModel):
    """Base schema for ratings with common fields"""
    user_id: UUID = Field(..., description="ID of the user who submitted the rating")
    book_id: UUID = Field(..., description="ID of the book being rated")
    rating: confloat(ge=0, le=5) = Field(..., description="Rating value (0-5)")


class RatingCreate(RatingBase):
    """Schema for creating a new rating"""
    pass


class RatingUpdate(BaseModel):
    """Schema for updating an existing rating"""
    rating: confloat(ge=0, le=5) = Field(..., description="Updated rating value (0-5)")


class RatingResponse(RatingBase):
    """Schema for returning rating data in responses"""
    id: UUID
    rated_at: datetime
    user_id: UUID
    book_id: UUID

import uuid
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, and_

from app.db.postgres.session import get_db
from app.db.postgres.models import Rating
from app.models.schemas import RatingCreate, RatingUpdate

router = APIRouter()


@router.post("/ratings/", status_code=status.HTTP_201_CREATED)
async def create_rating(rating: RatingCreate, db: Session = Depends(get_db)):
    """Create a new rating"""
    try:
        # Check if rating already exists for this user-book pair
        existing_rating = db.execute(
            select(Rating).where(and_(
                Rating.user_id == rating.user_id,
                Rating.book_id == rating.book_id)
            )
        ).scalar_one_or_none()

        if existing_rating:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating already exists for this user and book"
            )

        # Create new rating
        db_rating = Rating(
            id=uuid.uuid4(),
            user_id=rating.user_id,
            book_id=rating.book_id,
            rating=rating.rating
        )

        db.add(db_rating)
        db.commit()
        db.refresh(db_rating)

        return db_rating

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating rating: {str(e)}"
        )


@router.get("/ratings/{rating_id}")
async def get_rating(rating_id: UUID, db: Session = Depends(get_db)):
    """Get rating by ID"""
    try:
        rating = db.execute(
            select(Rating).where(Rating.id == rating_id)
        ).scalar_one_or_none()

        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rating not found"
            )

        return rating

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching rating: {str(e)}"
        )


@router.get("/ratings/user/{user_id}")
async def get_user_ratings(user_id: UUID, db: Session = Depends(get_db)):
    """Get all ratings by a user"""
    try:
        ratings = db.execute(
            select(Rating).where(Rating.user_id == user_id)
        ).scalars().all()

        return ratings

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user ratings: {str(e)}"
        )


@router.get("/ratings/book/{book_id}")
async def get_book_ratings(book_id: UUID, db: Session = Depends(get_db)):
    """Get all ratings for a book"""
    try:
        ratings = db.execute(
            select(Rating).where(Rating.book_id == book_id)
        ).scalars().all()

        return ratings

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching book ratings: {str(e)}"
        )


@router.put("/ratings/{rating_id}")
async def update_rating(rating_id: UUID, rating_update: RatingUpdate, db: Session = Depends(get_db)):
    """Update a rating"""
    try:
        # Check if rating exists
        existing_rating = db.execute(
            select(Rating).where(Rating.id == rating_id)
        ).scalar_one_or_none()

        if not existing_rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rating not found"
            )

        # Update rating
        db.execute(
            update(Rating)
            .where(Rating.id == rating_id)
            .values(rating=rating_update.rating)
        )
        db.commit()

        # Return updated rating
        updated_rating = db.execute(
            select(Rating).where(Rating.id == rating_id)
        ).scalar_one()

        return updated_rating

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating rating: {str(e)}"
        )


@router.delete("/ratings/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(rating_id: UUID, db: Session = Depends(get_db)):
    """Delete a rating"""
    try:
        # Check if rating exists
        existing_rating = db.execute(
            select(Rating).where(Rating.id == rating_id)
        ).scalar_one_or_none()

        if not existing_rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rating not found"
            )

        # Delete rating
        db.execute(
            delete(Rating).where(Rating.id == rating_id)
        )
        db.commit()

        return None

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting rating: {str(e)}"
        )
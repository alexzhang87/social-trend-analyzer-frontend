from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..data.models import database, schemas

router = APIRouter()

@router.post("/api/seed", summary="Seed the database with raw posts")
def seed_database(
    posts: List[schemas.PostCreate], 
    db: Session = Depends(database.get_db)
):
    """
    Accepts a list of posts and saves them to the database.
    This is used to populate the database with initial data for MVP development.
    """
    try:
        new_posts_count = 0
        for post_data in posts:
            # Check if a post with this URL already exists to ensure idempotency
            existing_post = db.query(database.RawPost).filter(database.RawPost.url == post_data.url).first()
            if not existing_post:
                db_post = database.RawPost(**post_data.model_dump())
                db.add(db_post)
                new_posts_count += 1
        
        db.commit()
        total_posts = db.query(database.RawPost).count()
        return {
            "message": f"Seeding complete. Added {new_posts_count} new posts.",
            "total_posts_in_db": total_posts
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to seed database: {str(e)}")

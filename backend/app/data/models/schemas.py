from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostBase(BaseModel):
    platform: str
    author: Optional[str] = None
    text: str
    url: str
    likes: Optional[int] = 0
    created_at: datetime

class PostCreate(PostBase):
    """Schema for creating a post. Used in the seed endpoint."""
    pass

class Post(PostBase):
    """Schema for reading a post from the database."""
    id: int

    class Config:
        from_attributes = True

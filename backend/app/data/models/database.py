from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Import the central settings object.
# Note: Using a relative path for robustness within the application structure.
from ...core.config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    # check_same_thread is only needed for SQLite
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class RawPost(Base):
    __tablename__ = "raw_posts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)
    author = Column(String, nullable=True)
    text = Column(Text, nullable=False)
    url = Column(String, unique=True, index=True)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False)

def get_db():
    """Dependency to get a DB session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    """Creates all database tables."""
    Base.metadata.create_all(bind=engine)
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://username:password@localhost:5432/stroke_prediction_db"
)

# For handling special characters in password
if '@' in DATABASE_URL.split('://')[1].split('@')[0]:
    # Extract credentials and encode password if needed
    parts = DATABASE_URL.split('@')
    credentials = parts[0].split('://')[1]
    db_url = parts[1]
    
    username_password = credentials.split(':')
    password = quote_plus(username_password[1])
    encoded_credentials = f"{username_password[0]}:{password}"
    DATABASE_URL = f"postgresql://{encoded_credentials}@{db_url}"

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Ensures connections are alive before use
    echo=False  # Set to True to log SQL queries for debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency function to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import all models to ensure they are registered with SQLAlchemy
from app.models import *
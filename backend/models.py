"""
Database models for the Government Amendment Feedback System
Using SQLAlchemy with Neon PostgreSQL
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./feedback_system.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()


class Amendment(Base):
    """
    Amendment model to store government amendments
    """
    __tablename__ = "amendments"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship with feedback
    feedbacks = relationship("Feedback", back_populates="amendment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Amendment(id={self.id}, title='{self.title[:50]}...')>"


class Feedback(Base):
    """
    Feedback model to store public feedback with ML analysis results
    """
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    amendment_id = Column(Integer, ForeignKey("amendments.id"), nullable=False, index=True)
    original_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    sentiment = Column(String(50), nullable=True)  # positive, negative, neutral
    sentiment_confidence = Column(Float, nullable=True)  # confidence score 0-1
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship with amendment
    amendment = relationship("Amendment", back_populates="feedbacks")
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, amendment_id={self.amendment_id}, sentiment='{self.sentiment}')>"


# Dependency to get DB session
def get_db():
    """
    Dependency function to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Function to create all tables
def create_tables():
    """
    Create all database tables
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


if __name__ == "__main__":
    # Create tables when running this file directly
    create_tables()
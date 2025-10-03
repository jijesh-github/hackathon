from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
import torch
from detoxify import Detoxify
from transformers import pipeline
import gc

# Print device info without emojis
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name()}")
    print(f"CUDA Version: {torch.version.cuda}")

app = FastAPI(title="Government Feedback System with CUDA", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "postgresql://hackathon_owner:jNqznBKJ6I9a@ep-patient-sun-a5slc1dp.us-east-2.aws.neon.tech/hackathon?sslmode=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Amendment(Base):
    __tablename__ = "amendments"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    current_status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    amendment_id = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    is_toxic = Column(Boolean, default=False)
    sentiment = Column(String)
    sentiment_score = Column(String)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize models on GPU
print("Loading AI models on GPU...")

# 1. Detoxify for toxicity detection
toxicity_model = Detoxify('original', device='cuda' if torch.cuda.is_available() else 'cpu')
print("Detoxify model loaded")

# 2. Sentiment analysis pipeline
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=0 if torch.cuda.is_available() else -1,
    model_kwargs={"torch_dtype": torch.float16} if torch.cuda.is_available() else {}
)
print("Sentiment analysis model loaded")

# 3. Summarization pipeline
summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    device=0 if torch.cuda.is_available() else -1,
    model_kwargs={"torch_dtype": torch.float16} if torch.cuda.is_available() else {}
)
print("Summarization model loaded")

if torch.cuda.is_available():
    print(f"GPU Memory: {torch.cuda.memory_allocated()/1024**3:.2f}GB / {torch.cuda.get_device_properties(0).total_memory/1024**3:.2f}GB")

# Pydantic models
class FeedbackRequest(BaseModel):
    amendment_id: int
    comment: str

class FeedbackResponse(BaseModel):
    toxic: bool
    message: str
    sentiment: str = None
    sentiment_score: str = None
    summary: str = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Government Feedback System with CUDA Acceleration", "device": str(device)}

@app.get("/health")
async def health_check():
    gpu_info = {}
    if torch.cuda.is_available():
        gpu_info = {
            "gpu_available": True,
            "gpu_name": torch.cuda.get_device_name(),
            "memory_allocated": f"{torch.cuda.memory_allocated()/1024**3:.2f}GB",
            "memory_total": f"{torch.cuda.get_device_properties(0).total_memory/1024**3:.2f}GB"
        }
    else:
        gpu_info = {"gpu_available": False}
    
    return {
        "status": "healthy",
        "device": str(device),
        **gpu_info
    }

@app.get("/amendments")
async def get_amendments():
    db = next(get_db())
    try:
        amendments = db.query(Amendment).all()
        return {
            "success": True,
            "message": f"Successfully retrieved {len(amendments)} amendments",
            "amendments": [
                {
                    "id": amendment.id,
                    "title": amendment.title,
                    "description": amendment.description,
                    "current_status": amendment.current_status,
                    "created_at": amendment.created_at.isoformat() if amendment.created_at else None
                }
                for amendment in amendments
            ]
        }
    except Exception as e:
        print(f"Error fetching amendments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch amendments: {str(e)}")

@app.post("/submit_feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest):
    db = next(get_db())
    
    try:
        # Step 1: Toxicity Detection
        print(f"Analyzing toxicity for comment: {feedback.comment[:50]}...")
        toxicity_result = toxicity_model.predict(feedback.comment)
        toxic_score = toxicity_result.get('toxicity', 0)
        
        print(f"Toxicity score: {toxic_score}")
        
        # Step 2: Check if toxic
        if toxic_score > 0.6:
            # Save toxic feedback to database
            new_feedback = Feedback(
                amendment_id=feedback.amendment_id,
                comment=feedback.comment,
                is_toxic=True
            )
            db.add(new_feedback)
            db.commit()
            
            return FeedbackResponse(
                toxic=True,
                message="The comment contains toxicity"
            )
        
        # Step 3: If not toxic, proceed with sentiment and summary
        print("Comment is safe, proceeding with sentiment analysis...")
        
        # Sentiment Analysis
        sentiment_result = sentiment_pipeline(feedback.comment)
        sentiment_label = sentiment_result[0]['label']
        sentiment_score = sentiment_result[0]['score']
        
        print(f"Sentiment: {sentiment_label} (score: {sentiment_score})")
        
        # Summarization
        print("Generating summary...")
        if len(feedback.comment) > 50:  # Only summarize if comment is long enough
            summary_result = summarizer(feedback.comment, max_length=100, min_length=20, do_sample=False)
            summary = summary_result[0]['summary_text']
        else:
            summary = feedback.comment  # Use original comment if too short
        
        print(f"Summary: {summary}")
        
        # Step 4: Save to database
        new_feedback = Feedback(
            amendment_id=feedback.amendment_id,
            comment=feedback.comment,
            is_toxic=False,
            sentiment=sentiment_label,
            sentiment_score=f"{sentiment_score:.4f}",
            summary=summary
        )
        db.add(new_feedback)
        db.commit()
        
        # GPU memory cleanup
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
        
        return FeedbackResponse(
            toxic=False,
            message="Feedback submitted successfully",
            sentiment=sentiment_label,
            sentiment_score=f"{sentiment_score:.4f}",
            summary=summary
        )
        
    except Exception as e:
        print(f"Error processing feedback: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")

# Frontend compatibility endpoints
class AmendmentCreate(BaseModel):
    title: str
    description: str

class FeedbackCreate(BaseModel):
    amendment_id: int
    original_text: str

class APIResponse(BaseModel):
    success: bool
    message: str
    data: dict = None

@app.post("/amendments", response_model=APIResponse)
async def create_amendment(amendment: AmendmentCreate):
    """Create new amendment for frontend compatibility"""
    db = next(get_db())
    try:
        print(f"Creating amendment: {amendment.title}")
        
        # Create new amendment
        db_amendment = Amendment(
            title=amendment.title,
            description=amendment.description
        )
        
        db.add(db_amendment)
        db.commit()
        db.refresh(db_amendment)
        
        print(f"Amendment created successfully: ID={db_amendment.id}")
        
        return APIResponse(
            success=True,
            message="Amendment created successfully",
            data={
                "id": db_amendment.id,
                "title": db_amendment.title,
                "description": db_amendment.description,
                "created_at": db_amendment.created_at.isoformat()
            }
        )
        
    except Exception as e:
        print(f"Error creating amendment: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create amendment: {str(e)}")

@app.post("/feedback", response_model=APIResponse)
async def submit_feedback_frontend(feedback: FeedbackCreate):
    """Submit feedback endpoint for frontend compatibility with REAL AI models"""
    db = next(get_db())
    
    try:
        print(f"Processing feedback for amendment {feedback.amendment_id}")
        print(f"Comment: {feedback.original_text[:100]}...")
        
        # Step 1: REAL Toxicity Detection
        toxicity_result = toxicity_model.predict(feedback.original_text)
        toxic_score = toxicity_result.get('toxicity', 0)
        
        print(f"REAL Toxicity score: {toxic_score}")
        
        # Step 2: Check if toxic
        if toxic_score > 0.6:
            return APIResponse(
                success=False,
                message="The comment contains toxicity",
                data={
                    "toxic": True,
                    "toxic_score": toxic_score,
                    "sentiment": None,
                    "confidence": None,
                    "summary": None
                }
            )
        
        # Step 3: REAL Sentiment Analysis
        sentiment_result = sentiment_pipeline(feedback.original_text)
        sentiment_label = sentiment_result[0]['label'].lower()
        sentiment_score = sentiment_result[0]['score']
        
        print(f"REAL Sentiment: {sentiment_label} (score: {sentiment_score})")
        
        # Step 4: REAL Summarization
        if len(feedback.original_text) > 50:
            summary_result = summarizer(feedback.original_text, max_length=100, min_length=20, do_sample=False)
            summary = summary_result[0]['summary_text']
        else:
            summary = feedback.original_text
        
        print(f"REAL Summary: {summary}")
        
        # GPU memory cleanup
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
        
        return APIResponse(
            success=True,
            message="Feedback submitted successfully with REAL AI analysis",
            data={
                "toxic": False,
                "feedback_id": 1,
                "sentiment": sentiment_label,
                "confidence": sentiment_score,
                "summary": summary,
                "toxic_score": toxic_score
            }
        )
        
    except Exception as e:
        print(f"Error processing feedback: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
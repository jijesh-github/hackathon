"""
Lightweight version of the backend for testing toxicity detection
"""

import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Dict, List, Any
import os
from datetime import datetime
from sqlalchemy.orm import Session

# Import database models and schemas
from models import get_db, create_tables, Amendment as AmendmentModel, Feedback as FeedbackModel
from schemas import (
    AmendmentCreate, Amendment, AmendmentListResponse,
    FeedbackCreate, Feedback, FeedbackListResponse, 
    APIResponse, AnalysisResult
)

# Try to import detoxify
try:
    from detoxify import Detoxify
    DETOXIFY_AVAILABLE = True
    print("✅ Detoxify imported successfully")
except ImportError:
    DETOXIFY_AVAILABLE = False
    print("❌ Detoxify not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================
# FASTAPI APPLICATION
# ================================

app = FastAPI(
    title="Government Amendment Feedback System - Lite",
    description="Lightweight version for testing toxicity detection",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database and services"""
    try:
        create_tables()
        logger.info("✅ Database initialized successfully!")
        
        if DETOXIFY_AVAILABLE:
            logger.info("✅ Detoxify available for toxicity detection")
        else:
            logger.warning("⚠️ Detoxify not available - toxicity detection disabled")
            
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")

# ================================
# ML FUNCTIONS (SIMPLE VERSIONS)
# ================================

def detect_toxicity(text: str) -> tuple[bool, float]:
    """Detect toxicity in text using Detoxify"""
    if not DETOXIFY_AVAILABLE:
        logger.warning("Detoxify not available, skipping toxicity detection")
        return False, 0.0
    
    try:
        # Initialize detoxify model
        detoxify = Detoxify('original')
        
        # Get toxicity predictions
        toxicity_scores = detoxify.predict(text)
        
        # Find maximum toxicity score across all categories
        max_score = max(toxicity_scores.values())
        
        # Check if toxic (threshold > 0.6)
        is_toxic = max_score > 0.6
        
        logger.info(f"🛡️ Toxicity check: max_score={max_score:.3f}, toxic={is_toxic}")
        return is_toxic, max_score
        
    except Exception as e:
        logger.error(f"Toxicity detection error: {e}")
        return False, 0.0

def simple_sentiment(text: str) -> tuple[str, float]:
    """Simple sentiment analysis fallback"""
    positive_words = ['good', 'great', 'excellent', 'positive', 'support', 'agree', 'beneficial']
    negative_words = ['bad', 'terrible', 'awful', 'negative', 'oppose', 'disagree', 'harmful']
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return "positive", 0.75
    elif neg_count > pos_count:
        return "negative", 0.75
    else:
        return "neutral", 0.60

def simple_summary(text: str, max_words: int = 15) -> str:
    """Simple text summarization by truncation"""
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + "..."

# ================================
# API ROUTES
# ================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Government Amendment Feedback System - Lite Version", "detoxify": DETOXIFY_AVAILABLE}

@app.post("/amendments", response_model=APIResponse)
async def create_amendment(amendment: AmendmentCreate, db: Session = Depends(get_db)):
    """Create a new amendment"""
    try:
        db_amendment = AmendmentModel(
            title=amendment.title,
            description=amendment.description
        )
        
        db.add(db_amendment)
        db.commit()
        db.refresh(db_amendment)
        
        logger.info(f"✅ Amendment created: ID={db_amendment.id}")
        
        return APIResponse(
            success=True,
            message="Amendment created successfully",
            data={
                "id": db_amendment.id,
                "title": db_amendment.title,
                "description": db_amendment.description
            }
        )
    except Exception as e:
        logger.error(f"Error creating amendment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create amendment")

@app.get("/amendments", response_model=AmendmentListResponse)
async def get_amendments(db: Session = Depends(get_db)):
    """Get all amendments"""
    try:
        amendments = db.query(AmendmentModel).order_by(AmendmentModel.created_at.desc()).all()
        return AmendmentListResponse(
            success=True,
            message=f"Retrieved {len(amendments)} amendments",
            data=amendments
        )
    except Exception as e:
        logger.error(f"Error fetching amendments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch amendments")

@app.post("/feedback", response_model=APIResponse)
async def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit feedback with toxicity detection"""
    try:
        # Verify amendment exists
        amendment = db.query(AmendmentModel).filter(AmendmentModel.id == feedback.amendment_id).first()
        if not amendment:
            raise HTTPException(status_code=404, detail="Amendment not found")
        
        # Step 1: Run toxicity detection first
        logger.info(f"🛡️ Checking toxicity for feedback on amendment {feedback.amendment_id}...")
        is_toxic, toxic_score = detect_toxicity(feedback.original_text)
        
        if is_toxic:
            # Toxic comment → don't process further
            logger.warning(f"🚫 Toxic content detected: score={toxic_score:.3f}")
            return APIResponse(
                success=False,
                message="The comment contains toxicity",
                data={
                    "toxic": True,
                    "toxic_score": toxic_score
                }
            )
        
        # Step 2: Safe comment → run simple analysis
        logger.info(f"✅ Content is safe, proceeding with analysis...")
        
        sentiment, confidence = simple_sentiment(feedback.original_text)
        summary = simple_summary(feedback.original_text)
        
        # Step 3: Save feedback to database
        db_feedback = FeedbackModel(
            amendment_id=feedback.amendment_id,
            original_text=feedback.original_text,
            summary=summary,
            sentiment=sentiment,
            sentiment_confidence=confidence
        )
        
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        logger.info(f"✅ Feedback saved: ID={db_feedback.id}, Sentiment={sentiment}")
        
        # Step 4: Return success response
        return APIResponse(
            success=True,
            message="Feedback submitted successfully",
            data={
                "toxic": False,
                "feedback_id": db_feedback.id,
                "sentiment": sentiment,
                "confidence": confidence,
                "summary": summary,
                "toxic_score": toxic_score
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")

@app.get("/feedback/{amendment_id}", response_model=FeedbackListResponse)
async def get_feedback(amendment_id: int, db: Session = Depends(get_db)):
    """Get all feedback for a specific amendment"""
    try:
        amendment = db.query(AmendmentModel).filter(AmendmentModel.id == amendment_id).first()
        if not amendment:
            raise HTTPException(status_code=404, detail="Amendment not found")
        
        feedback = db.query(FeedbackModel).filter(
            FeedbackModel.amendment_id == amendment_id
        ).order_by(FeedbackModel.created_at.desc()).all()
        
        return FeedbackListResponse(
            success=True,
            message=f"Retrieved {len(feedback)} feedback entries",
            data=feedback
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch feedback")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
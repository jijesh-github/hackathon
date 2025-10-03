"""
Working backend that properly handles existing database schema
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging

# Import database models and schemas
from models import get_db, create_tables, Amendment as AmendmentModel, Feedback as FeedbackModel
from schemas import (
    AmendmentCreate, Amendment, AmendmentListResponse,
    FeedbackCreate, Feedback, FeedbackListResponse, 
    APIResponse
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Government Amendment Feedback System - Working")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database"""
    try:
        create_tables()
        logger.info("✅ Database initialized!")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")

@app.get("/")
async def root():
    return {"message": "Working Backend", "status": "OK"}

@app.post("/amendments", response_model=APIResponse)
async def create_amendment(amendment: AmendmentCreate, db: Session = Depends(get_db)):
    """Create amendment"""
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
                "description": db_amendment.description,
                "created_at": db_amendment.created_at.isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error creating amendment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/amendments", response_model=AmendmentListResponse)
async def get_amendments(db: Session = Depends(get_db)):
    """Get all amendments"""
    try:
        amendments = db.query(AmendmentModel).order_by(AmendmentModel.created_at.desc()).all()
        
        logger.info(f"✅ Retrieved {len(amendments)} amendments")
        
        return AmendmentListResponse(
            success=True,
            message=f"Retrieved {len(amendments)} amendments",
            amendments=amendments
        )
    except Exception as e:
        logger.error(f"Error fetching amendments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch amendments: {str(e)}")

@app.post("/feedback", response_model=APIResponse)
async def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit feedback - with mock analysis"""
    try:
        # Verify amendment exists
        amendment = db.query(AmendmentModel).filter(AmendmentModel.id == feedback.amendment_id).first()
        if not amendment:
            raise HTTPException(status_code=404, detail="Amendment not found")
        
        # Create feedback with mock analysis
        db_feedback = FeedbackModel(
            amendment_id=feedback.amendment_id,
            original_text=feedback.original_text,
            summary=f"Summary: {feedback.original_text[:100]}..." if len(feedback.original_text) > 100 else feedback.original_text,
            sentiment="positive" if "good" in feedback.original_text.lower() or "great" in feedback.original_text.lower() else "neutral",
            sentiment_confidence=0.85
        )
        
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        logger.info(f"✅ Feedback saved: ID={db_feedback.id}")
        
        return APIResponse(
            success=True,
            message="Feedback submitted successfully",
            data={
                "toxic": False,
                "feedback_id": db_feedback.id,
                "sentiment": db_feedback.sentiment,
                "confidence": db_feedback.sentiment_confidence,
                "summary": db_feedback.summary,
                "toxic_score": 0.1
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        
        logger.info(f"✅ Retrieved {len(feedback)} feedback entries for amendment {amendment_id}")
        
        return FeedbackListResponse(
            success=True,
            message=f"Retrieved {len(feedback)} feedback entries",
            feedback=feedback
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
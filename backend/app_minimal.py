"""
Minimal backend for UI testing - No ML models
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

app = FastAPI(title="Minimal Backend for UI Testing")

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
    return {"message": "Minimal Backend Running", "status": "OK"}

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
        
        return APIResponse(
            success=True,
            message="Amendment created",
            data={"id": db_amendment.id, "title": db_amendment.title}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/amendments", response_model=AmendmentListResponse)
async def get_amendments(db: Session = Depends(get_db)):
    """Get all amendments"""
    try:
        amendments = db.query(AmendmentModel).all()
        return AmendmentListResponse(
            success=True,
            message=f"Found {len(amendments)} amendments",
            data=amendments
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback", response_model=APIResponse)
async def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit feedback - simplified"""
    try:
        # Simple mock analysis
        db_feedback = FeedbackModel(
            amendment_id=feedback.amendment_id,
            original_text=feedback.original_text,
            summary="Mock summary",
            sentiment="positive",
            sentiment_confidence=0.85
        )
        
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        return APIResponse(
            success=True,
            message="Feedback submitted successfully",
            data={
                "toxic": False,
                "feedback_id": db_feedback.id,
                "sentiment": "positive",
                "confidence": 0.85,
                "summary": "Mock summary",
                "toxic_score": 0.1
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
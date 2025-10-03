"""
Government Feedback System with REAL AI Models
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
import logging
import torch

# Import database models
from models import get_db, Amendment as AmendmentModel

# Import real AI models
try:
    from detoxify import Detoxify
    from transformers import pipeline
    import gc
    
    # Initialize REAL AI models
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Loading REAL AI models on device: {device}")
    
    # 1. Real toxicity detection
    toxicity_model = Detoxify('original', device='cuda' if torch.cuda.is_available() else 'cpu')
    print("SUCCESS: Detoxify toxicity model loaded")
    
    # 2. Real sentiment analysis
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=0 if torch.cuda.is_available() else -1,
        model_kwargs={"torch_dtype": torch.float16} if torch.cuda.is_available() else {}
    )
    print("SUCCESS: DistilBERT sentiment model loaded")
    
    # 3. Real summarization
    summarizer = pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        device=0 if torch.cuda.is_available() else -1,
        model_kwargs={"torch_dtype": torch.float16} if torch.cuda.is_available() else {}
    )
    print("SUCCESS: BART summarization model loaded")
    
    REAL_AI_AVAILABLE = True
    if torch.cuda.is_available():
        print(f"GPU Memory: {torch.cuda.memory_allocated()/1024**3:.2f}GB / {torch.cuda.get_device_properties(0).total_memory/1024**3:.2f}GB")
    
except Exception as e:
    print(f"WARNING: Could not load AI models: {e}")
    print("INFO: Using mock analysis instead")
    REAL_AI_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Debug Backend")

# Add CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Amendment(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class AmendmentCreate(BaseModel):
    title: str
    description: str

class AmendmentListResponse(BaseModel):
    success: bool = True
    message: str
    amendments: List[Amendment]

class APIResponse(BaseModel):
    success: bool
    message: str
    data: dict = None

@app.get("/")
async def root():
    return {"status": "Backend is running", "message": "Debug backend active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/amendments", response_model=APIResponse)
async def create_amendment(amendment: AmendmentCreate, db: Session = Depends(get_db)):
    """Create new amendment - missing endpoint added!"""
    try:
        logger.info(f"🔍 Creating amendment: {amendment.title}")
        
        # Create new amendment
        db_amendment = AmendmentModel(
            title=amendment.title,
            description=amendment.description
        )
        
        db.add(db_amendment)
        db.commit()
        db.refresh(db_amendment)
        
        logger.info(f"✅ Amendment created successfully: ID={db_amendment.id}")
        
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
        logger.error(f"❌ Error creating amendment: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to create amendment: {str(e)}")

@app.get("/amendments")
async def get_amendments(db: Session = Depends(get_db)):
    """Get all amendments with detailed logging"""
    try:
        logger.info("🔍 Starting amendment fetch...")
        
        # Test database connection
        amendments = db.query(AmendmentModel).order_by(AmendmentModel.created_at.desc()).all()
        
        logger.info(f"📊 Found {len(amendments)} amendments in database")
        
        # Log each amendment
        for amendment in amendments:
            logger.info(f"   Amendment ID: {amendment.id}, Title: {amendment.title}")
        
        response = AmendmentListResponse(
            success=True,
            message=f"Successfully retrieved {len(amendments)} amendments",
            amendments=amendments
        )
        
        logger.info(f"✅ Returning response with {len(amendments)} amendments")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in get_amendments: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch amendments: {str(e)}")

@app.get("/test-db")
async def test_database():
    """Test database connection directly"""
    try:
        db = next(get_db())
        count = db.query(AmendmentModel).count()
        return {
            "database_connection": "SUCCESS",
            "amendment_count": count,
            "message": "Database is working properly"
        }
    except Exception as e:
        return {
            "database_connection": "FAILED",
            "error": str(e),
            "message": "Database connection issue"
        }

# Feedback models
class FeedbackRequest(BaseModel):
    amendment_id: int
    comment: str

class FeedbackResponse(BaseModel):
    toxic: bool
    message: str
    sentiment: str = None
    sentiment_score: str = None
    summary: str = None

@app.post("/submit_feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    """Submit feedback with basic processing (no AI models for debugging)"""
    try:
        logger.info(f"🔍 Receiving feedback for amendment {feedback.amendment_id}")
        logger.info(f"📝 Comment: {feedback.comment[:100]}...")
        
        # Verify amendment exists
        amendment = db.query(AmendmentModel).filter(AmendmentModel.id == feedback.amendment_id).first()
        if not amendment:
            logger.error(f"❌ Amendment {feedback.amendment_id} not found")
            raise HTTPException(status_code=404, detail="Amendment not found")
        
        logger.info(f"✅ Amendment found: {amendment.title}")
        
        # For debugging - simple non-toxic response
        # In real implementation, this would use AI models
        response = FeedbackResponse(
            toxic=False,
            message="Feedback submitted successfully (DEBUG MODE - No AI processing)",
            sentiment="POSITIVE",
            sentiment_score="0.8500",
            summary=f"Summary: {feedback.comment[:50]}..." if len(feedback.comment) > 50 else feedback.comment
        )
        
        logger.info(f"✅ Feedback processed successfully for amendment {feedback.amendment_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing feedback: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")

# Frontend expects /feedback endpoint with different structure
class FeedbackCreate(BaseModel):
    amendment_id: int
    original_text: str

class APIResponse(BaseModel):
    success: bool
    message: str
    data: dict = None

@app.post("/feedback", response_model=APIResponse)
async def submit_feedback_frontend(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit feedback endpoint with REAL AI analysis"""
    try:
        logger.info(f"🔍 Processing feedback for amendment {feedback.amendment_id}")
        logger.info(f"📝 Text: {feedback.original_text[:100]}...")
        
        # Verify amendment exists
        amendment = db.query(AmendmentModel).filter(AmendmentModel.id == feedback.amendment_id).first()
        if not amendment:
            logger.error(f"❌ Amendment {feedback.amendment_id} not found")
            raise HTTPException(status_code=404, detail="Amendment not found")
        
        logger.info(f"✅ Amendment found: {amendment.title}")
        
        if REAL_AI_AVAILABLE:
            logger.info("REAL AI: Using REAL AI models for analysis")
            
            # REAL Toxicity Detection
            toxicity_result = toxicity_model.predict(feedback.original_text)
            toxic_score = toxicity_result.get('toxicity', 0)
            
            logger.info(f"REAL AI: Toxicity score: {toxic_score}")
            
            # Check if toxic
            if toxic_score > 0.6:
                return APIResponse(
                    success=False,
                    message=f"Comment contains toxicity (score: {toxic_score:.3f})",
                    data={
                        "toxic": True,
                        "toxic_score": float(toxic_score),  # Convert to Python float
                        "sentiment": None,
                        "confidence": None,
                        "summary": None
                    }
                )
            
            # REAL Sentiment Analysis
            sentiment_result = sentiment_pipeline(feedback.original_text)
            sentiment_label = sentiment_result[0]['label'].lower()
            sentiment_score = sentiment_result[0]['score']
            
            logger.info(f"REAL AI: Sentiment: {sentiment_label} (confidence: {sentiment_score:.3f})")
            
            # REAL Summarization
            if len(feedback.original_text) > 50:
                summary_result = summarizer(feedback.original_text, max_length=100, min_length=20, do_sample=False)
                summary = summary_result[0]['summary_text']
            else:
                summary = feedback.original_text
            
            logger.info(f"REAL AI: Summary generated")
            
            # GPU memory cleanup
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gc.collect()
            
            response_data = {
                "toxic": False,
                "feedback_id": 1,
                "sentiment": sentiment_label,
                "confidence": float(sentiment_score),  # Convert to Python float
                "summary": summary,
                "toxic_score": float(toxic_score)  # Convert to Python float
            }
            
        else:
            logger.info("MOCK AI: Using enhanced rule-based analysis")
            # Simple rule-based analysis for negative comments
            text_lower = feedback.original_text.lower()
            
            # Check for negative words
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'horrible', 'worst', 'sucks', 'stupid', 'dumb']
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'best', 'love', 'fantastic']
            
            negative_count = sum(1 for word in negative_words if word in text_lower)
            positive_count = sum(1 for word in positive_words if word in text_lower)
            
            if negative_count > positive_count:
                sentiment = "negative"
                confidence = 0.7 + (negative_count * 0.1)
            elif positive_count > negative_count:
                sentiment = "positive"
                confidence = 0.7 + (positive_count * 0.1)
            else:
                sentiment = "neutral"
                confidence = 0.5
            
            response_data = {
                "toxic": False,
                "feedback_id": 1,
                "sentiment": sentiment,
                "confidence": min(confidence, 0.95),
                "summary": f"Summary: {feedback.original_text[:50]}..." if len(feedback.original_text) > 50 else feedback.original_text,
                "toxic_score": 0.1
            }
        
        response = APIResponse(
            success=True,
            message="Feedback submitted successfully" + (" with REAL AI analysis" if REAL_AI_AVAILABLE else " with enhanced analysis"),
            data=response_data
        )
        
        logger.info(f"SUCCESS: Feedback processed successfully")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing feedback: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
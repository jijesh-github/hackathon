"""
CUDA-Accelerated Backend for Amendment Feedback System
Uses GPU acceleration for all AI models (Detoxify, DistilBERT, BART)
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
from models import get_db, create_tables, Amendment as AmendmentModel, Feedback as FeedbackModel

# Configure device - use CUDA if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🚀 Using device: {device}")
if torch.cuda.is_available():
    print(f"📊 GPU: {torch.cuda.get_device_name(0)}")
    print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

# Import AI libraries
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from detoxify import Detoxify
    DETOXIFY_AVAILABLE = True
except ImportError:
    DETOXIFY_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
create_tables()

app = FastAPI(title="CUDA-Accelerated Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for models
sentiment_analyzer = None
summarizer = None
detoxify_model = None

# Schemas
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

class FeedbackCreate(BaseModel):
    amendment_id: int
    original_text: str

class Feedback(BaseModel):
    id: int
    amendment_id: int
    original_text: str
    summary: str
    sentiment: str
    sentiment_confidence: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class FeedbackListResponse(BaseModel):
    success: bool = True
    message: str
    feedback: List[Feedback]

class APIResponse(BaseModel):
    success: bool = True
    message: str
    data: dict = None

@app.on_event("startup")
async def startup_event():
    """Load AI models on startup with CUDA acceleration"""
    global sentiment_analyzer, summarizer, detoxify_model
    
    logger.info(f"🚀 Loading CUDA-accelerated ML models on {device}...")
    
    try:
        if TRANSFORMERS_AVAILABLE:
            # Load sentiment analysis model on GPU
            logger.info("📊 Loading DistilBERT sentiment model on GPU...")
            sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if torch.cuda.is_available() else -1,  # 0 = first GPU, -1 = CPU
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32  # Use half precision on GPU
            )
            
            # Load summarization model on GPU
            logger.info("📝 Loading BART summarization model on GPU...")
            summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                max_length=150,
                min_length=30
            )
            
        if DETOXIFY_AVAILABLE:
            # Load Detoxify model
            logger.info("🛡️ Loading Detoxify model...")
            detoxify_model = Detoxify('original', device=device)
            
        logger.info(f"✅ All CUDA models loaded successfully on {device}!")
        
        # Print GPU memory usage
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated(0) / 1024**3
            memory_reserved = torch.cuda.memory_reserved(0) / 1024**3
            logger.info(f"🔥 GPU Memory - Allocated: {memory_allocated:.2f}GB, Reserved: {memory_reserved:.2f}GB")
            
    except Exception as e:
        logger.error(f"❌ Error loading models: {e}")
        raise

def detect_toxicity_cuda(text: str) -> tuple:
    """
    Detect toxicity using CUDA-accelerated Detoxify model
    """
    try:
        if not DETOXIFY_AVAILABLE or detoxify_model is None:
            logger.warning("Detoxify not available, skipping toxicity detection")
            return False, 0.0
        
        # Use CUDA-accelerated Detoxify
        toxicity_scores = detoxify_model.predict(text)
        toxic_score = toxicity_scores['toxicity']
        
        is_toxic = toxic_score > 0.6
        logger.info(f"🛡️ Toxicity check: score={toxic_score:.3f}, toxic={is_toxic}")
        
        return is_toxic, float(toxic_score)
        
    except Exception as e:
        logger.error(f"Error in toxicity detection: {e}")
        return False, 0.0

def analyze_sentiment_cuda(text: str) -> tuple:
    """
    Analyze sentiment using CUDA-accelerated DistilBERT
    """
    try:
        if not TRANSFORMERS_AVAILABLE or sentiment_analyzer is None:
            return "neutral", 0.5
        
        # Use GPU-accelerated sentiment analysis
        result = sentiment_analyzer(text)
        sentiment = result[0]['label'].lower()
        confidence = result[0]['score']
        
        logger.info(f"📊 Sentiment: {sentiment} (confidence: {confidence:.3f})")
        return sentiment, confidence
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        return "neutral", 0.5

def summarize_text_cuda(text: str) -> str:
    """
    Summarize text using CUDA-accelerated BART
    """
    try:
        if not TRANSFORMERS_AVAILABLE or summarizer is None:
            # Fallback to simple truncation
            words = text.split()
            return ' '.join(words[:50]) + ('...' if len(words) > 50 else '')
        
        # Use GPU-accelerated summarization
        if len(text.split()) < 10:
            return text  # Too short to summarize
            
        summary_result = summarizer(text, max_length=100, min_length=20, do_sample=False)
        summary = summary_result[0]['summary_text']
        
        logger.info(f"📝 Generated summary: {len(summary)} characters")
        return summary
        
    except Exception as e:
        logger.error(f"Error in summarization: {e}")
        # Fallback
        words = text.split()
        return ' '.join(words[:50]) + ('...' if len(words) > 50 else '')

# API Endpoints
@app.get("/amendments", response_model=AmendmentListResponse)
async def get_amendments(db: Session = Depends(get_db)):
    """Get all amendments"""
    try:
        amendments = db.query(AmendmentModel).order_by(AmendmentModel.created_at.desc()).all()
        logger.info(f"✅ Successfully retrieved {len(amendments)} amendments")
        
        return AmendmentListResponse(
            success=True,
            message=f"Retrieved {len(amendments)} amendments",
            amendments=amendments
        )
    except Exception as e:
        logger.error(f"Error fetching amendments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch amendments: {str(e)}")

@app.post("/amendments", response_model=APIResponse)
async def create_amendment(amendment: AmendmentCreate, db: Session = Depends(get_db)):
    """Create new amendment"""
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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback", response_model=APIResponse)
async def submit_feedback_cuda(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit feedback with CUDA-accelerated AI analysis"""
    try:
        # Verify amendment exists
        amendment = db.query(AmendmentModel).filter(AmendmentModel.id == feedback.amendment_id).first()
        if not amendment:
            raise HTTPException(status_code=404, detail="Amendment not found")
        
        # Step 1: CUDA-accelerated toxicity detection
        is_toxic, toxic_score = detect_toxicity_cuda(feedback.original_text)
        
        if is_toxic:
            logger.warning(f"🚫 Toxic content detected: score={toxic_score:.3f}")
            return APIResponse(
                success=False,
                message="The comment contains toxicity",
                data={
                    "toxic": True,
                    "toxic_score": toxic_score
                }
            )
        
        # Step 2: CUDA-accelerated sentiment analysis
        sentiment, confidence = analyze_sentiment_cuda(feedback.original_text)
        
        # Step 3: CUDA-accelerated text summarization
        summary = summarize_text_cuda(feedback.original_text)
        
        # Step 4: Save to database
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
        
        logger.info(f"✅ CUDA-accelerated feedback saved: ID={db_feedback.id}, Sentiment={sentiment}")
        
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
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

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

@app.get("/gpu-status")
async def gpu_status():
    """Get GPU status and memory usage"""
    if torch.cuda.is_available():
        memory_allocated = torch.cuda.memory_allocated(0) / 1024**3
        memory_reserved = torch.cuda.memory_reserved(0) / 1024**3
        memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        return {
            "cuda_available": True,
            "device": str(device),
            "gpu_name": torch.cuda.get_device_name(0),
            "memory_allocated_gb": round(memory_allocated, 2),
            "memory_reserved_gb": round(memory_reserved, 2),
            "memory_total_gb": round(memory_total, 2),
            "memory_usage_percent": round((memory_allocated / memory_total) * 100, 1)
        }
    else:
        return {
            "cuda_available": False,
            "device": "cpu"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
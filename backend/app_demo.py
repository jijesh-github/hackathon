import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Dict, List, Any
import re

# Try to import transformers, fall back to demo mode if not available
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    pipeline = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sentiment Analysis & Summarization API (Demo)",
    description="Demo API for analyzing sentiment and generating summaries from CSV data",
    version="2.0.0-demo"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Running in DEMO mode - using rule-based analysis")

# Load summarization model
SUMMARIZER_LOADED = False
summarizer = None

if TRANSFORMERS_AVAILABLE:
    try:
        logger.info("Loading BART summarization model...")
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        logger.info("BART summarization model loaded successfully")
        SUMMARIZER_LOADED = True
    except Exception as e:
        logger.warning(f"Could not load BART model: {e}. Using fallback summarization.")
        summarizer = None
        SUMMARIZER_LOADED = False
else:
    logger.info("Transformers not available. Using fallback summarization.")

# -------- Demo Analysis Functions -------- #
def predict_sentiment(text: str) -> str:
    """Demo sentiment prediction using keyword matching"""
    if pd.isna(text) or text.strip() == "":
        return "NEUTRAL"
    
    text_lower = str(text).lower()
    
    positive_words = [
        'good', 'great', 'excellent', 'amazing', 'love', 'fantastic', 'wonderful',
        'awesome', 'perfect', 'best', 'brilliant', 'outstanding', 'superb',
        'happy', 'pleased', 'satisfied', 'impressed', 'recommend', 'quality'
    ]
    
    negative_words = [
        'bad', 'terrible', 'awful', 'hate', 'worst', 'poor', 'disappointing',
        'horrible', 'useless', 'waste', 'broken', 'defective', 'cheap',
        'unhappy', 'frustrated', 'angry', 'annoyed', 'problem', 'issue'
    ]
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return "POSITIVE"
    elif negative_count > positive_count:
        return "NEGATIVE"
    else:
        return "NEUTRAL"

def summarize_text(text: str) -> str:
    """
    Summarizes text only if it has more than 15 words.
    - Text <=15 words: return original text
    - Text >15 words: generate concise summary using BART model
    - Falls back to truncated original if summarization fails
    """
    if pd.isna(text) or text.strip() == "":
        return "No content to summarize"
    
    text_str = str(text).strip()
    words = text_str.split()
    word_count = len(words)
    
    # If text has 15 words or fewer, return original text
    if word_count <= 15:
        return text_str
    
    # Try to use BART model for summarization if available
    if SUMMARIZER_LOADED and summarizer is not None:
        try:
            summary = summarizer(
                text_str,
                max_length=90,   # maximum words in summary
                min_length=20,   # minimum words in summary
                do_sample=False  # deterministic output
            )
            return summary[0]['summary_text']
        except Exception as e:
            logger.warning(f"Summarization failed: {e}. Using fallback.")
            # Fallback: return first 50 words if summarization fails
            return " ".join(words[:50])
    else:
        # Fallback method if BART model not loaded
        return " ".join(words[:50])

def get_sentiment_statistics(sentiments: List[str]) -> Dict[str, Any]:
    """Calculate sentiment statistics"""
    sentiment_counts = pd.Series(sentiments).value_counts().to_dict()
    total = len(sentiments)
    
    # Ensure all sentiment types are represented
    for sentiment_type in ['POSITIVE', 'NEGATIVE', 'NEUTRAL']:
        if sentiment_type not in sentiment_counts:
            sentiment_counts[sentiment_type] = 0
    
    # Calculate percentages
    sentiment_percentages = {k: round((v/total)*100, 2) for k, v in sentiment_counts.items()}
    
    return {
        "counts": sentiment_counts,
        "percentages": sentiment_percentages,
        "total": total
    }

# -------- API Endpoints -------- #

@app.get("/")
async def root():
    return {
        "message": "Sentiment Analysis & Summarization API (Demo Mode)", 
        "version": "2.0.0-demo",
        "mode": "demo",
        "note": "Using rule-based analysis for demonstration",
        "endpoints": {
            "analyze": "POST /analyze - Upload CSV for complete analysis",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "mode": "demo",
        "models_loaded": False,
        "message": "Running with rule-based analysis"
    }

@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    """
    Complete analysis endpoint that provides both sentiment analysis and summarization
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Load CSV into pandas
        df = pd.read_csv(file.file)
        
        # Check if 'comment_text' column exists
        if "comment_text" not in df.columns:
            raise HTTPException(
                status_code=400, 
                detail="CSV must have a 'comment_text' column"
            )
        
        logger.info(f"Processing {len(df)} comments in demo mode...")
        
        # Run sentiment analysis
        logger.info("Running demo sentiment analysis...")
        df["sentiment"] = df["comment_text"].apply(predict_sentiment)
        
        # Run summarization
        logger.info("Running demo summarization...")
        df["summary"] = df["comment_text"].apply(summarize_text)
        
        # Get sentiment statistics
        sentiment_stats = get_sentiment_statistics(df["sentiment"].tolist())
        
        # Prepare detailed results
        detailed_results = []
        for _, row in df.iterrows():
            detailed_results.append({
                "original_text": row["comment_text"],
                "sentiment": row["sentiment"],
                "summary": row["summary"]
            })
        
        # Prepare response
        results = {
            "status": "success",
            "mode": "demo",
            "note": "Results generated using rule-based analysis for demonstration",
            "analysis_summary": {
                "total_comments": len(df),
                "sentiment_analysis": sentiment_stats,
                "processing_info": {
                    "sentiment_model": "Rule-based keyword matching",
                    "summarization_model": "facebook/bart-large-cnn" if SUMMARIZER_LOADED else "Fallback text truncation"
                }
            },
            "detailed_results": detailed_results,
            "visualization_data": {
                "pie_chart_data": [
                    {"label": "Positive", "value": sentiment_stats["counts"]["POSITIVE"], "percentage": sentiment_stats["percentages"]["POSITIVE"]},
                    {"label": "Negative", "value": sentiment_stats["counts"]["NEGATIVE"], "percentage": sentiment_stats["percentages"]["NEGATIVE"]},
                    {"label": "Neutral", "value": sentiment_stats["counts"]["NEUTRAL"], "percentage": sentiment_stats["percentages"]["NEUTRAL"]}
                ]
            }
        }
        
        logger.info("Demo analysis completed successfully!")
        return results
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
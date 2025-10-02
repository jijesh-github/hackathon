import torch
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, pipeline
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sentiment Analysis & Summarization API",
    description="API for analyzing sentiment and generating summaries from CSV data",
    version="2.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Load Models -------- #
logger.info("Loading sentiment analysis model...")
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
sentiment_model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

logger.info("Loading summarization model...")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

logger.info("All models loaded successfully!")

# -------- Helper Functions -------- #
def predict_sentiment(text: str) -> str:
    """Predict sentiment for a single text"""
    if pd.isna(text) or text.strip() == "":
        return "NEUTRAL"
    
    try:
        inputs = tokenizer(str(text), return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            logits = sentiment_model(**inputs).logits
        predicted_class_id = logits.argmax().item()
        return sentiment_model.config.id2label[predicted_class_id]
    except Exception as e:
        logger.error(f"Error in sentiment prediction: {e}")
        return "NEUTRAL"

def summarize_text(text: str) -> str:
    """Summarize a single text"""
    if pd.isna(text) or text.strip() == "":
        return "No content to summarize"
    
    try:
        # Ensure text is not too short or too long
        text_str = str(text).strip()
        if len(text_str) < 20:
            return text_str  # Return original if too short
        
        # Limit input length for summarization
        if len(text_str) > 1000:
            text_str = text_str[:1000]
        
        summary = summarizer(text_str, max_length=100, min_length=20, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        logger.error(f"Error in summarization: {e}")
        return f"Summarization failed: {str(e)}"

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
        "message": "Sentiment Analysis & Summarization API", 
        "version": "2.0.0",
        "endpoints": {
            "analyze": "POST /analyze - Upload CSV for complete analysis",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "models_loaded": True}

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
        
        logger.info(f"Processing {len(df)} comments...")
        
        # Run sentiment analysis
        logger.info("Running sentiment analysis...")
        df["sentiment"] = df["comment_text"].apply(predict_sentiment)
        
        # Run summarization
        logger.info("Running summarization...")
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
            "analysis_summary": {
                "total_comments": len(df),
                "sentiment_analysis": sentiment_stats,
                "processing_info": {
                    "sentiment_model": "DistilBERT",
                    "summarization_model": "BART-Large-CNN"
                }
            },
            "detailed_results": detailed_results
        }
        
        logger.info("Analysis completed successfully!")
        return results
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Legacy endpoint for backward compatibility
@app.post("/analyze_csv")
async def analyze_csv_legacy(file: UploadFile = File(...)):
    """Legacy endpoint - redirects to /analyze"""
    return await analyze_csv(file)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
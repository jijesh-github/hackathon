import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Dict, List, Any
import re
import base64
import io
import os
from datetime import datetime
import torch

# Try to import real ML libraries
try:
    from transformers import (
        DistilBertTokenizer, 
        DistilBertForSequenceClassification, 
        pipeline
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Try to import wordcloud and matplotlib
try:
    from wordcloud import WordCloud, STOPWORDS
    import matplotlib.pyplot as plt
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Real Sentiment Analysis & Summarization API",
    description="Production API using real DistilBERT and BART models",
    version="3.0.0-production"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variables
tokenizer = None
sentiment_model = None
summarizer = None
models_loaded = False

def load_real_models():
    """Load the actual DistilBERT and BART models"""
    global tokenizer, sentiment_model, summarizer, models_loaded
    
    if not TRANSFORMERS_AVAILABLE:
        logger.error("Transformers library not available!")
        return False
    
    try:
        logger.info("Loading real DistilBERT sentiment model...")
        tokenizer = DistilBertTokenizer.from_pretrained(
            "distilbert-base-uncased-finetuned-sst-2-english"
        )
        sentiment_model = DistilBertForSequenceClassification.from_pretrained(
            "distilbert-base-uncased-finetuned-sst-2-english"
        )
        
        logger.info("Loading real BART summarization model...")
        summarizer = pipeline(
            "summarization", 
            model="facebook/bart-large-cnn",
            device=0 if torch.cuda.is_available() else -1
        )
        
        models_loaded = True
        logger.info("✅ Real models loaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load real models: {e}")
        logger.info("Models may need to download - this can take time on first run")
        return False

# Try to load models on startup
logger.info("🚀 Starting PRODUCTION mode with real models...")
load_real_models()

def predict_sentiment_real(text: str) -> str:
    """Real sentiment prediction using DistilBERT"""
    if not models_loaded or pd.isna(text) or text.strip() == "":
        return "NEUTRAL"
    
    try:
        inputs = tokenizer(
            str(text), 
            return_tensors="pt", 
            truncation=True, 
            padding=True, 
            max_length=512
        )
        
        with torch.no_grad():
            logits = sentiment_model(**inputs).logits
            
        predicted_class_id = logits.argmax().item()
        result = sentiment_model.config.id2label[predicted_class_id]
        
        # Convert to consistent format
        if result == "POSITIVE":
            return "POSITIVE"
        elif result == "NEGATIVE": 
            return "NEGATIVE"
        else:
            return "NEUTRAL"
            
    except Exception as e:
        logger.error(f"Error in real sentiment prediction: {e}")
        return "NEUTRAL"

def summarize_text_real(text: str) -> str:
    """Real summarization using BART with 15-word rule"""
    if pd.isna(text) or text.strip() == "":
        return "No content to summarize"
    
    text_str = str(text).strip()
    words = text_str.split()
    word_count = len(words)
    
    # 15-word rule: return original if ≤15 words
    if word_count <= 15:
        logger.info(f"Text has {word_count} words (≤15), returning original")
        return text_str
    
    logger.info(f"Text has {word_count} words (>15), applying BART summarization")
    
    if not models_loaded:
        logger.warning("Models not loaded, using fallback")
        return " ".join(words[:50]) + "..."
    
    try:
        # Use BART for real summarization
        if len(text_str) > 1000:
            text_str = text_str[:1000]  # Limit input length
        
        summary = summarizer(
            text_str,
            max_length=90,   # As specified in requirements
            min_length=20,   # As specified in requirements  
            do_sample=False  # As specified in requirements
        )
        
        return summary[0]['summary_text']
        
    except Exception as e:
        logger.error(f"Real summarization failed: {e}")
        # Fallback to first 50 words as specified
        return " ".join(words[:50]) + "..."

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

def generate_wordcloud_from_text(texts: List[str]) -> Dict[str, Any]:
    """Generate word cloud from texts"""
    if not WORDCLOUD_AVAILABLE:
        return {
            "status": "unavailable",
            "message": "WordCloud libraries not available",
            "image_data": None
        }
    
    try:
        combined_text = " ".join([str(text) for text in texts if pd.notna(text)])
        
        if len(combined_text.strip()) < 10:
            return {
                "status": "insufficient_data",
                "message": "Not enough text data",
                "image_data": None
            }
        
        # Create custom stopwords
        custom_stopwords = set(STOPWORDS)
        custom_stopwords.update([
            'amendment', 'proposal', 'draft', 'changes', 'this', 'the', 'and', 'or',
            'will', 'is', 'are', 'be', 'to', 'for', 'with', 'of', 'in', 'on', 'at'
        ])
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            stopwords=custom_stopwords,
            collocations=False,
            max_words=100,
            colormap='viridis'
        ).generate(combined_text)
        
        # Convert to base64
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout(pad=0)
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
        plt.close()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"wordcloud_{timestamp}.png"
        
        return {
            "status": "success",
            "message": "Word cloud generated with real models",
            "image_data": img_base64,
            "image_filename": filename,
            "image_format": "png"
        }
        
    except Exception as e:
        logger.error(f"Error generating word cloud: {e}")
        return {
            "status": "error",
            "message": f"Failed to generate word cloud: {str(e)}",
            "image_data": None
        }

# -------- API Endpoints -------- #

@app.get("/")
async def root():
    return {
        "message": "Real Sentiment Analysis & Summarization API", 
        "version": "3.0.0-production",
        "mode": "production" if models_loaded else "fallback",
        "models_loaded": models_loaded,
        "features": {
            "real_sentiment_analysis": "DistilBERT model" if models_loaded else "Not loaded",
            "real_summarization": "BART-Large-CNN model" if models_loaded else "Not loaded",
            "15_word_rule": "Text ≤15 words returned unchanged",
            "wordcloud_generation": "Automatic word cloud generation"
        },
        "endpoints": {
            "analyze": "POST /analyze - Upload CSV for real ML analysis",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "mode": "production" if models_loaded else "fallback",
        "models_loaded": models_loaded,
        "transformers_available": TRANSFORMERS_AVAILABLE,
        "wordcloud_available": WORDCLOUD_AVAILABLE,
        "message": "Running with real models" if models_loaded else "Models not loaded - using fallbacks"
    }

@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    """
    Real ML analysis endpoint using DistilBERT and BART models
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Load CSV
        df = pd.read_csv(file.file)
        
        # Check for comment_text column
        if "comment_text" not in df.columns:
            raise HTTPException(
                status_code=400, 
                detail="CSV must have a 'comment_text' column"
            )
        
        logger.info(f"Processing {len(df)} comments with REAL models...")
        
        # Real sentiment analysis using DistilBERT
        logger.info("Running REAL DistilBERT sentiment analysis...")
        df["sentiment"] = df["comment_text"].apply(predict_sentiment_real)
        
        # Real summarization using BART with 15-word rule
        logger.info("Running REAL BART summarization with 15-word rule...")
        df["summary"] = df["comment_text"].apply(summarize_text_real)
        
        # Statistics
        sentiment_stats = get_sentiment_statistics(df["sentiment"].tolist())
        
        # Word counts for summarization stats
        word_counts = [len(str(text).split()) for text in df["comment_text"]]
        short_texts = sum(1 for count in word_counts if count <= 15)
        long_texts = len(word_counts) - short_texts
        
        # Generate word cloud
        logger.info("Generating word cloud...")
        wordcloud_data = generate_wordcloud_from_text(df["comment_text"].tolist())
        
        # Detailed results
        detailed_results = []
        for _, row in df.iterrows():
            word_count = len(str(row["comment_text"]).split())
            detailed_results.append({
                "original_text": row["comment_text"],
                "word_count": word_count,
                "sentiment": row["sentiment"],
                "summary": row["summary"],
                "was_summarized": word_count > 15
            })
        
        # Response
        results = {
            "status": "success",
            "mode": "production" if models_loaded else "fallback",
            "models_used": {
                "sentiment": "DistilBERT-base-uncased-finetuned-sst-2-english" if models_loaded else "Fallback",
                "summarization": "facebook/bart-large-cnn" if models_loaded else "Fallback"
            },
            "summarization_stats": {
                "total_comments": len(df),
                "short_texts_unchanged": short_texts,
                "long_texts_summarized": long_texts,
                "rule": "Texts with ≤15 words returned unchanged, >15 words summarized with BART"
            },
            "analysis_summary": {
                "total_comments": len(df),
                "sentiment_analysis": sentiment_stats,
                "processing_info": {
                    "sentiment_model": "DistilBERT" if models_loaded else "Fallback",
                    "summarization_model": "BART-Large-CNN" if models_loaded else "Fallback",
                    "summarization_rule": "≤15 words: unchanged, >15 words: BART summary"
                }
            },
            "detailed_results": detailed_results,
            "visualization_data": {
                "pie_chart_data": [
                    {"label": "Positive", "value": sentiment_stats["counts"]["POSITIVE"], "percentage": sentiment_stats["percentages"]["POSITIVE"]},
                    {"label": "Negative", "value": sentiment_stats["counts"]["NEGATIVE"], "percentage": sentiment_stats["percentages"]["NEGATIVE"]},
                    {"label": "Neutral", "value": sentiment_stats["counts"]["NEUTRAL"], "percentage": sentiment_stats["percentages"]["NEUTRAL"]}
                ]
            },
            "wordcloud": wordcloud_data
        }
        
        logger.info("REAL ML analysis completed successfully!")
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
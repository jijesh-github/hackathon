"""
Government Amendment Feedback System with Neon PostgreSQL Integration
Extends existing ML models with database functionality and REST API
"""

import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging
from typing import Dict, List, Any
import re
import base64
import io
import os
from datetime import datetime
import torch
from sqlalchemy.orm import Session

# Import database models and schemas
from models import get_db, create_tables, Amendment as AmendmentModel, Feedback as FeedbackModel
from schemas import (
    AmendmentCreate, Amendment, AmendmentListResponse,
    FeedbackCreate, Feedback, FeedbackListResponse, 
    APIResponse, AnalysisResult
)

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

# Create database tables
create_tables()

app = FastAPI(
    title="Government Amendment Feedback System",
    description="ML-powered sentiment analysis and summarization with Neon PostgreSQL",
    version="4.0.0-database"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
except Exception:
    logger.warning("Frontend directory not found, skipping static files")

# Global variables for models
sentiment_model = None
sentiment_tokenizer = None
summarizer = None

def load_models():
    """Load ML models on startup"""
    global sentiment_model, sentiment_tokenizer, summarizer
    
    if TRANSFORMERS_AVAILABLE:
        try:
            logger.info("🚀 Loading real ML models...")
            
            # Load DistilBERT for sentiment analysis
            logger.info("Loading DistilBERT sentiment model...")
            sentiment_tokenizer = DistilBertTokenizer.from_pretrained(
                "distilbert-base-uncased-finetuned-sst-2-english"
            )
            sentiment_model = DistilBertForSequenceClassification.from_pretrained(
                "distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            # Load BART for summarization
            logger.info("Loading BART summarization model...")
            summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                tokenizer="facebook/bart-large-cnn"
            )
            
            logger.info("✅ Real models loaded successfully!")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            logger.info("Falling back to demo mode...")
    else:
        logger.warning("Transformers not available, using demo mode")

@app.on_event("startup")
async def startup_event():
    """Load models when the application starts"""
    load_models()

def analyze_sentiment(text: str) -> tuple[str, float]:
    """
    Analyze sentiment using DistilBERT model
    Returns (sentiment, confidence)
    """
    if sentiment_model and sentiment_tokenizer:
        try:
            # Tokenize and predict
            inputs = sentiment_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            outputs = sentiment_model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Get prediction
            predicted_class = torch.argmax(predictions, dim=-1).item()
            confidence = torch.max(predictions).item()
            
            sentiment = "positive" if predicted_class == 1 else "negative"
            
            logger.info(f"Real sentiment analysis: {text[:50]}... → {sentiment} ({confidence:.3f})")
            return sentiment, confidence
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
    
    # Fallback to keyword-based analysis
    positive_keywords = ['good', 'great', 'excellent', 'approve', 'support', 'beneficial', 'helpful', 'clear']
    negative_keywords = ['bad', 'poor', 'confusing', 'difficult', 'burden', 'impractical', 'harmful']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_keywords if word in text_lower)
    negative_count = sum(1 for word in negative_keywords if word in text_lower)
    
    if positive_count > negative_count:
        return "positive", 0.7
    elif negative_count > positive_count:
        return "negative", 0.7
    else:
        return "neutral", 0.5

def summarize_text(text: str, max_words: int = 15) -> str:
    """
    Summarize text using BART model with word limit
    """
    words = text.split()
    
    # If text is already short, return as-is
    if len(words) <= max_words:
        logger.info(f"Text has {len(words)} words (≤{max_words}), returning original")
        return text
    
    if summarizer:
        try:
            # Use BART for summarization
            summary = summarizer(
                text, 
                max_length=90,  # Token limit
                min_length=20, 
                do_sample=False
            )[0]['summary_text']
            
            # Apply word limit
            summary_words = summary.split()[:max_words]
            final_summary = ' '.join(summary_words)
            
            logger.info(f"BART summarization: {len(words)} words → {len(summary_words)} words")
            return final_summary
            
        except Exception as e:
            logger.error(f"Summarization error: {e}")
    
    # Fallback to simple truncation
    return ' '.join(words[:max_words])

def generate_wordcloud(text: str) -> str:
    """Generate word cloud and return base64 encoded image"""
    if not WORDCLOUD_AVAILABLE:
        return ""
    
    try:
        # Generate word cloud
        wordcloud = WordCloud(
            width=800, height=400,
            background_color='white',
            stopwords=STOPWORDS,
            max_words=100,
            colormap='viridis'
        ).generate(text)
        
        # Save to base64
        img_buffer = io.BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        plt.close()
        
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return img_base64
    except Exception as e:
        logger.error(f"Word cloud generation error: {e}")
        return ""

# ================================
# API ROUTES - AMENDMENTS
# ================================

@app.post("/amendments", response_model=APIResponse)
async def create_amendment(amendment: AmendmentCreate, db: Session = Depends(get_db)):
    """
    Create a new government amendment
    """
    try:
        # Create new amendment
        db_amendment = AmendmentModel(
            title=amendment.title,
            description=amendment.description
        )
        
        db.add(db_amendment)
        db.commit()
        db.refresh(db_amendment)
        
        logger.info(f"✅ Created amendment: {amendment.title}")
        
        return APIResponse(
            success=True,
            message="Amendment created successfully",
            data={"id": db_amendment.id, "title": db_amendment.title}
        )
        
    except Exception as e:
        logger.error(f"Error creating amendment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create amendment")

@app.get("/amendments", response_model=AmendmentListResponse)
async def get_amendments(db: Session = Depends(get_db)):
    """
    Get all amendments
    """
    try:
        amendments = db.query(AmendmentModel).order_by(AmendmentModel.created_at.desc()).all()
        
        return AmendmentListResponse(
            success=True,
            message=f"Retrieved {len(amendments)} amendments",
            amendments=amendments
        )
        
    except Exception as e:
        logger.error(f"Error fetching amendments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch amendments")

# ================================
# API ROUTES - FEEDBACK
# ================================

@app.post("/feedback", response_model=APIResponse)
async def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """
    Submit feedback for an amendment with ML analysis
    """
    try:
        # Verify amendment exists
        amendment = db.query(AmendmentModel).filter(AmendmentModel.id == feedback.amendment_id).first()
        if not amendment:
            raise HTTPException(status_code=404, detail="Amendment not found")
        
        # Perform ML analysis
        logger.info(f"🧠 Analyzing feedback for amendment {feedback.amendment_id}...")
        
        sentiment, confidence = analyze_sentiment(feedback.original_text)
        summary = summarize_text(feedback.original_text)
        
        # Create feedback record
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
        
        return APIResponse(
            success=True,
            message="Feedback submitted and analyzed successfully",
            data={
                "feedback_id": db_feedback.id,
                "sentiment": sentiment,
                "confidence": confidence,
                "summary": summary
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")

@app.get("/feedback/{amendment_id}", response_model=FeedbackListResponse)
async def get_feedback(amendment_id: int, db: Session = Depends(get_db)):
    """
    Get all feedback for a specific amendment
    """
    try:
        # Verify amendment exists
        amendment = db.query(AmendmentModel).filter(AmendmentModel.id == amendment_id).first()
        if not amendment:
            raise HTTPException(status_code=404, detail="Amendment not found")
        
        # Get feedback
        feedback = db.query(FeedbackModel).filter(
            FeedbackModel.amendment_id == amendment_id
        ).order_by(FeedbackModel.created_at.desc()).all()
        
        return FeedbackListResponse(
            success=True,
            message=f"Retrieved {len(feedback)} feedback items for amendment {amendment_id}",
            feedback=feedback
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch feedback")

# ================================
# LEGACY ROUTES (for backwards compatibility)
# ================================

@app.post("/analyze", response_model=Dict[str, Any])
async def analyze_csv(file: UploadFile = File(...)):
    """
    Legacy CSV analysis endpoint (for backwards compatibility)
    """
    try:
        logger.info("📁 Processing CSV file with REAL models...")
        
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        if 'comment' not in df.columns and 'feedback' not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must have 'comment' or 'feedback' column")
        
        # Use first available column
        text_column = 'comment' if 'comment' in df.columns else 'feedback'
        comments = df[text_column].dropna().tolist()
        
        logger.info(f"Processing {len(comments)} comments with REAL models...")
        
        # Analyze each comment
        results = []
        for comment in comments:
            sentiment, confidence = analyze_sentiment(comment)
            summary = summarize_text(comment)
            
            results.append({
                "original_text": comment,
                "sentiment": sentiment,
                "confidence": confidence,
                "summary": summary
            })
        
        # Generate word cloud from all comments
        all_text = " ".join(comments)
        word_cloud_base64 = generate_wordcloud(all_text)
        
        logger.info("✅ REAL ML analysis completed successfully!")
        
        return {
            "success": True,
            "message": f"Analyzed {len(comments)} comments successfully",
            "total_comments": len(comments),
            "results": results,
            "word_cloud": word_cloud_base64,
            "analysis_summary": {
                "positive": sum(1 for r in results if r["sentiment"] == "positive"),
                "negative": sum(1 for r in results if r["sentiment"] == "negative"),
                "neutral": sum(1 for r in results if r["sentiment"] == "neutral")
            }
        }
        
    except Exception as e:
        logger.error(f"Error in CSV analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# FRONTEND ROUTES
# ================================

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    """
    Serve the main frontend interface
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Government Amendment Feedback System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #2c3e50; margin-bottom: 30px; }
            .section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; color: #34495e; }
            input, textarea, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            textarea { height: 100px; resize: vertical; }
            button { background-color: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button:hover { background-color: #2980b9; }
            .success { color: #27ae60; font-weight: bold; margin-top: 10px; }
            .error { color: #e74c3c; font-weight: bold; margin-top: 10px; }
            .amendment-list { max-height: 200px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; border-radius: 4px; }
            .amendment-item { padding: 8px; border-bottom: 1px solid #eee; cursor: pointer; }
            .amendment-item:hover { background-color: #f8f9fa; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏛️ Government Amendment Feedback System</h1>
                <p>AI-Powered Sentiment Analysis & Summarization with Neon PostgreSQL</p>
            </div>
            
            <!-- Admin Section: Create Amendment -->
            <div class="section">
                <h2>📝 Admin: Create New Amendment</h2>
                <form id="amendmentForm">
                    <div class="form-group">
                        <label for="title">Amendment Title:</label>
                        <input type="text" id="title" name="title" required maxlength="500">
                    </div>
                    <div class="form-group">
                        <label for="description">Amendment Description:</label>
                        <textarea id="description" name="description" required placeholder="Enter the full text of the amendment..."></textarea>
                    </div>
                    <button type="submit">Create Amendment</button>
                </form>
                <div id="amendmentResult"></div>
            </div>
            
            <!-- Public Section: Submit Feedback -->
            <div class="section">
                <h2>💬 Public: Submit Feedback</h2>
                <form id="feedbackForm">
                    <div class="form-group">
                        <label for="amendmentSelect">Select Amendment:</label>
                        <select id="amendmentSelect" name="amendment_id" required>
                            <option value="">Loading amendments...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="feedback">Your Feedback:</label>
                        <textarea id="feedback" name="original_text" required placeholder="Enter your feedback on this amendment..." maxlength="5000"></textarea>
                    </div>
                    <button type="submit">Submit Feedback</button>
                </form>
                <div id="feedbackResult"></div>
            </div>
            
            <!-- View Existing Amendments -->
            <div class="section">
                <h2>📋 Current Amendments</h2>
                <div id="amendmentsList">Loading...</div>
                <button onclick="loadAmendments()" style="margin-top: 10px;">Refresh List</button>
            </div>
        </div>
        
        <script>
            const API_BASE = '';
            
            // Load amendments on page load
            window.onload = function() {
                loadAmendments();
            };
            
            // Load amendments for dropdown and list
            async function loadAmendments() {
                try {
                    const response = await fetch('/amendments');
                    const data = await response.json();
                    
                    if (data.success) {
                        // Populate dropdown
                        const select = document.getElementById('amendmentSelect');
                        select.innerHTML = '<option value="">Select an amendment...</option>';
                        
                        // Populate list
                        const list = document.getElementById('amendmentsList');
                        list.innerHTML = '';
                        
                        data.amendments.forEach(amendment => {
                            // Add to dropdown
                            const option = document.createElement('option');
                            option.value = amendment.id;
                            option.textContent = `${amendment.title}`;
                            select.appendChild(option);
                            
                            // Add to list
                            const div = document.createElement('div');
                            div.className = 'amendment-item';
                            div.innerHTML = `
                                <strong>${amendment.title}</strong><br>
                                <small>Created: ${new Date(amendment.created_at).toLocaleString()}</small><br>
                                ${amendment.description.substring(0, 200)}${amendment.description.length > 200 ? '...' : ''}
                            `;
                            list.appendChild(div);
                        });
                        
                        if (data.amendments.length === 0) {
                            list.innerHTML = '<p>No amendments found. Create one above!</p>';
                        }
                    }
                } catch (error) {
                    console.error('Error loading amendments:', error);
                    document.getElementById('amendmentsList').innerHTML = '<p class="error">Error loading amendments</p>';
                }
            }
            
            // Handle amendment creation
            document.getElementById('amendmentForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = {
                    title: formData.get('title'),
                    description: formData.get('description')
                };
                
                try {
                    const response = await fetch('/amendments', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        document.getElementById('amendmentResult').innerHTML = 
                            `<div class="success">✅ ${result.message}</div>`;
                        e.target.reset();
                        loadAmendments(); // Refresh the list
                    } else {
                        throw new Error(result.message || 'Failed to create amendment');
                    }
                } catch (error) {
                    document.getElementById('amendmentResult').innerHTML = 
                        `<div class="error">❌ Error: ${error.message}</div>`;
                }
            });
            
            // Handle feedback submission
            document.getElementById('feedbackForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = {
                    amendment_id: parseInt(formData.get('amendment_id')),
                    original_text: formData.get('original_text')
                };
                
                if (!data.amendment_id) {
                    document.getElementById('feedbackResult').innerHTML = 
                        '<div class="error">❌ Please select an amendment</div>';
                    return;
                }
                
                try {
                    document.getElementById('feedbackResult').innerHTML = 
                        '<div>🧠 Analyzing your feedback with AI models...</div>';
                    
                    const response = await fetch('/feedback', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        document.getElementById('feedbackResult').innerHTML = `
                            <div class="success">
                                ✅ ${result.message}<br>
                                <strong>Analysis Results:</strong><br>
                                • Sentiment: ${result.data.sentiment} (${(result.data.confidence * 100).toFixed(1)}% confidence)<br>
                                • Summary: "${result.data.summary}"
                            </div>
                        `;
                        e.target.reset();
                        document.getElementById('amendmentSelect').value = '';
                    } else {
                        throw new Error(result.message || 'Failed to submit feedback');
                    }
                } catch (error) {
                    document.getElementById('feedbackResult').innerHTML = 
                        `<div class="error">❌ Error: ${error.message}</div>`;
                }
            });
        </script>
    </body>
    </html>
    """

# ================================
# SERVER INFO
# ================================

@app.get("/info")
async def get_info():
    """
    Get system information
    """
    return {
        "system": "Government Amendment Feedback System",
        "version": "4.0.0-database",
        "models": {
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "wordcloud_available": WORDCLOUD_AVAILABLE,
            "sentiment_model": "distilbert-base-uncased-finetuned-sst-2-english" if TRANSFORMERS_AVAILABLE else "keyword-based",
            "summarization_model": "facebook/bart-large-cnn" if TRANSFORMERS_AVAILABLE else "truncation-based"
        },
        "database": "Neon PostgreSQL with SQLAlchemy",
        "features": [
            "Real-time sentiment analysis",
            "Text summarization with 15-word rule",
            "Word cloud generation", 
            "RESTful API",
            "Database persistence",
            "Web interface"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Government Amendment Feedback System...")
    logger.info("🗄️ Database: Neon PostgreSQL")
    logger.info("🤖 ML Models: DistilBERT + BART")
    logger.info("🌐 Web Interface: http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
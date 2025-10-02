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

# Try to import wordcloud and matplotlib, fallback gracefully if not available
try:
    from wordcloud import WordCloud, STOPWORDS
    import matplotlib.pyplot as plt
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False
    WordCloud = None
    STOPWORDS = None
    plt = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sentiment Analysis & Summarization API (Enhanced Demo)",
    description="Demo API with improved 15-word rule for summarization",
    version="2.1.0-demo"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Running in ENHANCED DEMO mode with 15-word rule")

# -------- Enhanced Analysis Functions -------- #
def predict_sentiment(text: str) -> str:
    """Enhanced sentiment prediction using comprehensive keyword matching"""
    if pd.isna(text) or text.strip() == "":
        return "NEUTRAL"
    
    text_lower = str(text).lower()
    
    # Comprehensive positive words list for policy/business context
    positive_words = [
        'good', 'great', 'excellent', 'amazing', 'love', 'fantastic', 'wonderful',
        'awesome', 'perfect', 'best', 'brilliant', 'outstanding', 'superb',
        'happy', 'pleased', 'satisfied', 'impressed', 'recommend', 'quality',
        'fast', 'quick', 'efficient', 'responsive', 'helpful', 'clear', 'easy',
        'successful', 'seamless', 'professional', 'dedication', 'exceeded', 'rare',
        # Policy/business specific positive words
        'help', 'helps', 'grow', 'encourage', 'innovation', 'improve', 'improves',
        'benefits', 'benefit', 'progressive', 'needed', 'initiative', 'simplify',
        'transparency', 'appreciate', 'effort', 'important', 'follow'
    ]
    
    # Comprehensive negative words list for policy/business context  
    negative_words = [
        'bad', 'terrible', 'awful', 'hate', 'worst', 'poor', 'disappointing',
        'horrible', 'useless', 'waste', 'broken', 'defective', 'cheap',
        'unhappy', 'frustrated', 'angry', 'annoyed', 'problem', 'issue',
        'damaged', 'disappointed', 'extremely disappointed', 'refused', 'unhelpful',
        'complicated', 'time-consuming', 'not helpful', 'low quality', 'concerns',
        'broke', 'failed', 'difficult', 'slow', 'expensive', 'overpriced',
        # Policy/business specific negative words
        'confusing', 'burden', 'impractical', 'corruption', 'inaccessible',
        'delay', 'increase', 'paperwork', 'drawbacks', 'harmful'
    ]
    
    # Enhanced matching - also check for phrases and negations
    positive_count = 0
    negative_count = 0
    
    # Count individual positive words
    for word in positive_words:
        if word in text_lower:
            positive_count += 1
    
    # Count individual negative words  
    for word in negative_words:
        if word in text_lower:
            negative_count += 1
    
    # Check for specific negative phrases that might be missed
    negative_phrases = [
        'extremely disappointed', 'not helpful', 'low quality', 'poor quality',
        'terrible experience', 'bad quality', 'refused to help', 'broke within'
    ]
    
    for phrase in negative_phrases:
        if phrase in text_lower:
            negative_count += 2  # Give phrases more weight
    
    # Check for positive phrases (including policy context)
    positive_phrases = [
        'excellent quality', 'great product', 'outstanding customer service',
        'highly recommend', 'exceeded expectations', 'fast delivery',
        'excellent work', 'great initiative', 'much needed', 'easy to follow',
        'help startups', 'encourage innovation', 'benefits small businesses',
        'improves transparency', 'good points'
    ]
    
    for phrase in positive_phrases:
        if phrase in text_lower:
            positive_count += 2  # Give phrases more weight
    
    # Debug logging
    logger.info(f"Text: '{text[:50]}...' | Positive: {positive_count}, Negative: {negative_count}")
    
    # Decision logic with tie-breaking
    if positive_count > negative_count:
        return "POSITIVE"
    elif negative_count > positive_count:
        return "NEGATIVE"
    else:
        # For ties, check text length and default sentiment
        if len(text.split()) <= 3:  # Very short texts default to neutral
            return "NEUTRAL"
        # For longer ties, slightly favor negative if any negative words present
        elif negative_count > 0:
            return "NEGATIVE"
        elif positive_count > 0:
            return "POSITIVE"
        else:
            return "NEUTRAL"

def summarize_text(text: str) -> str:
    """
    Summarizes text only if it has more than 15 words.
    - Text <=15 words: return original text
    - Text >15 words: generate concise summary using enhanced extraction
    - Falls back to truncated original if extraction fails
    """
    if pd.isna(text) or text.strip() == "":
        return "No content to summarize"
    
    text_str = str(text).strip()
    words = text_str.split()
    word_count = len(words)
    
    # If text has 15 words or fewer, return original text
    if word_count <= 15:
        logger.info(f"Text has {word_count} words (≤15), returning original")
        return text_str
    
    logger.info(f"Text has {word_count} words (>15), applying summarization")
    
    # Enhanced summarization logic for longer texts
    try:
        # Method 1: Try to find the most important sentence
        sentences = re.split(r'[.!?]+', text_str)
        
        # Score sentences based on important words and length
        scored_sentences = []
        important_words = ['excellent', 'amazing', 'terrible', 'perfect', 'worst', 'best', 'good', 'bad', 'love', 'hate', 'recommend', 'quality', 'problem', 'outstanding', 'disappointed']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if 10 <= len(sentence.split()) <= 25:  # Good length for summary
                score = sum(1 for word in important_words if word.lower() in sentence.lower())
                scored_sentences.append((score, sentence))
        
        # Return highest scoring sentence if available
        if scored_sentences:
            scored_sentences.sort(reverse=True, key=lambda x: x[0])
            best_sentence = scored_sentences[0][1].strip()
            if best_sentence:
                return best_sentence + "."
        
        # Method 2: Extract key phrases and combine
        # Look for patterns like "This is..." "It was..." etc.
        key_patterns = [
            r'(This (?:is|was|product|service).{20,100}?[.!?])',
            r'(It (?:is|was|works|doesn\'t).{20,100}?[.!?])',
            r'(I (?:love|hate|recommend|think).{20,100}?[.!?])'
        ]
        
        for pattern in key_patterns:
            matches = re.findall(pattern, text_str, re.IGNORECASE)
            if matches:
                summary = matches[0].strip()
                if len(summary.split()) >= 10:
                    return summary
        
        # Method 3: Fallback - intelligent truncation to first 50 words
        # But try to end at a sentence boundary
        first_50_words = " ".join(words[:50])
        
        # Try to end at a sentence
        for i in range(len(first_50_words)-1, 0, -1):
            if first_50_words[i] in '.!?':
                return first_50_words[:i+1]
        
        # If no sentence boundary found, add ellipsis
        return first_50_words + "..."
        
    except Exception as e:
        logger.warning(f"Enhanced summarization failed: {e}. Using simple fallback.")
        # Simple fallback: return first 50 words
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
    """
    Generate a word cloud from list of texts and return as base64 image
    
    Parameters:
    - texts: List of strings to generate word cloud from
    
    Returns:
    - Dictionary with word cloud data or fallback info
    """
    if not WORDCLOUD_AVAILABLE:
        logger.warning("WordCloud libraries not available. Skipping word cloud generation.")
        return {
            "status": "unavailable",
            "message": "Word cloud generation requires wordcloud and matplotlib libraries",
            "image_data": None
        }
    
    try:
        # Combine all texts into one string
        combined_text = " ".join([str(text) for text in texts if pd.notna(text)])
        
        if len(combined_text.strip()) < 10:
            return {
                "status": "insufficient_data",
                "message": "Not enough text data to generate meaningful word cloud",
                "image_data": None
            }
        
        # Create custom stopwords (including common policy/business terms that aren't meaningful)
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
        
        # Save to bytes buffer instead of file
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout(pad=0)
        
        # Convert to base64 string for API response
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
        plt.close()
        
        # Also save as file for frontend to potentially use
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"wordcloud_{timestamp}.png"
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig(filename, bbox_inches='tight', dpi=150)
        plt.close()
        
        logger.info(f"Word cloud generated successfully: {filename}")
        
        return {
            "status": "success",
            "message": "Word cloud generated successfully",
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
        "message": "Enhanced Sentiment Analysis & Summarization API", 
        "version": "2.1.0-demo",
        "mode": "enhanced_demo",
        "features": {
            "15_word_rule": "Text ≤15 words returned unchanged",
            "smart_summarization": "Enhanced extraction for longer texts",
            "sentiment_analysis": "Rule-based keyword matching",
            "wordcloud_generation": "Automatic word cloud from comment text"
        },
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
        "mode": "enhanced_demo",
        "summarization_rule": "15-word threshold implemented",
        "message": "Running with enhanced rule-based analysis"
    }

@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    """
    Complete analysis endpoint with enhanced 15-word summarization rule
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
        
        logger.info(f"Processing {len(df)} comments with 15-word rule...")
        
        # Run sentiment analysis
        logger.info("Running sentiment analysis...")
        df["sentiment"] = df["comment_text"].apply(predict_sentiment)
        
        # Run enhanced summarization with 15-word rule
        logger.info("Running enhanced summarization with 15-word rule...")
        df["summary"] = df["comment_text"].apply(summarize_text)
        
        # Get sentiment statistics
        sentiment_stats = get_sentiment_statistics(df["sentiment"].tolist())
        
        # Count texts that were summarized vs returned unchanged
        word_counts = [len(str(text).split()) for text in df["comment_text"]]
        short_texts = sum(1 for count in word_counts if count <= 15)
        long_texts = len(word_counts) - short_texts
        
        # Generate word cloud from all comments
        logger.info("Generating word cloud from comments...")
        wordcloud_data = generate_wordcloud_from_text(df["comment_text"].tolist())
        
        # Prepare detailed results
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
        
        # Prepare response
        results = {
            "status": "success",
            "mode": "enhanced_demo",
            "summarization_stats": {
                "total_comments": len(df),
                "short_texts_unchanged": short_texts,
                "long_texts_summarized": long_texts,
                "rule": "Texts with ≤15 words returned unchanged, >15 words summarized"
            },
            "analysis_summary": {
                "total_comments": len(df),
                "sentiment_analysis": sentiment_stats,
                "processing_info": {
                    "sentiment_model": "Rule-based keyword matching",
                    "summarization_model": "Enhanced extraction with 15-word rule",
                    "summarization_rule": "≤15 words: unchanged, >15 words: smart summary"
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
        
        logger.info("Enhanced analysis completed successfully!")
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
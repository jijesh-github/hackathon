"""
Test script to verify the database and API functionality
"""

import os
import sys
import asyncio
from sqlalchemy.orm import Session

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Amendment, Feedback
from schemas import AmendmentCreate, FeedbackCreate

def test_database():
    """Test database connectivity and basic operations"""
    print("🧪 Testing Database Functionality...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Test 1: Create an amendment
        print("\n1. Creating test amendment...")
        test_amendment = Amendment(
            title="Test Amendment - Digital Privacy Act",
            description="This amendment proposes new regulations for digital privacy protection, ensuring that citizens have better control over their personal data and how it's used by companies and government agencies."
        )
        
        db.add(test_amendment)
        db.commit()
        db.refresh(test_amendment)
        print(f"✅ Amendment created with ID: {test_amendment.id}")
        
        # Test 2: Create feedback
        print("\n2. Creating test feedback...")
        test_feedback = Feedback(
            amendment_id=test_amendment.id,
            original_text="I think this amendment is excellent and will greatly benefit citizens by protecting their privacy rights.",
            summary="Excellent amendment that will benefit citizens privacy rights.",
            sentiment="positive",
            sentiment_confidence=0.85
        )
        
        db.add(test_feedback)
        db.commit()
        db.refresh(test_feedback)
        print(f"✅ Feedback created with ID: {test_feedback.id}")
        
        # Test 3: Query data
        print("\n3. Querying data...")
        
        # Get all amendments
        amendments = db.query(Amendment).all()
        print(f"✅ Found {len(amendments)} amendments in database")
        
        # Get feedback for the amendment
        feedback = db.query(Feedback).filter(Feedback.amendment_id == test_amendment.id).all()
        print(f"✅ Found {len(feedback)} feedback items for amendment {test_amendment.id}")
        
        # Test 4: Display results
        print("\n4. Data verification...")
        for amendment in amendments:
            print(f"📄 Amendment: {amendment.title} (ID: {amendment.id})")
            print(f"   Created: {amendment.created_at}")
            print(f"   Description: {amendment.description[:100]}...")
            
            # Get feedback for this amendment
            amendment_feedback = db.query(Feedback).filter(Feedback.amendment_id == amendment.id).all()
            for fb in amendment_feedback:
                print(f"   💬 Feedback: {fb.original_text[:50]}...")
                print(f"      Sentiment: {fb.sentiment} ({fb.sentiment_confidence:.2f})")
                print(f"      Summary: {fb.summary}")
        
        print("\n✅ Database test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        return False
    finally:
        db.close()

def test_ml_functions():
    """Test ML analysis functions"""
    print("\n🤖 Testing ML Functions...")
    
    try:
        # Import ML functions
        from app_full_system import analyze_sentiment, summarize_text, generate_wordcloud
        
        test_text = "This amendment is really good and will help protect citizens' privacy rights. I strongly support this initiative and believe it will make a positive difference in our digital lives."
        
        print(f"Test text: {test_text}")
        
        # Test sentiment analysis
        print("\n1. Testing sentiment analysis...")
        sentiment, confidence = analyze_sentiment(test_text)
        print(f"✅ Sentiment: {sentiment} (confidence: {confidence:.3f})")
        
        # Test summarization
        print("\n2. Testing summarization...")
        summary = summarize_text(test_text, max_words=15)
        print(f"✅ Summary: {summary}")
        
        # Test word cloud generation
        print("\n3. Testing word cloud generation...")
        wordcloud_b64 = generate_wordcloud(test_text)
        if wordcloud_b64:
            print(f"✅ Word cloud generated ({len(wordcloud_b64)} chars)")
        else:
            print("⚠️ Word cloud generation skipped (library not available)")
        
        print("\n✅ ML functions test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ ML functions test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Government Amendment Feedback System - Test Suite")
    print("=" * 60)
    
    # Test database functionality
    db_success = test_database()
    
    # Test ML functionality
    ml_success = test_ml_functions()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"Database functionality: {'✅ PASS' if db_success else '❌ FAIL'}")
    print(f"ML functionality: {'✅ PASS' if ml_success else '❌ FAIL'}")
    
    if db_success and ml_success:
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\nTo start the full system:")
        print("python app_full_system.py")
        print("\nThen visit: http://localhost:8000")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
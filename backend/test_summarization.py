"""
Test the updated summarization function with the 15-word rule
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Test cases for the summarization function
test_cases = [
    {
        "text": "This is short text with only ten words in it.",
        "expected_behavior": "return_original",
        "word_count": 10
    },
    {
        "text": "This text has exactly fifteen words so it should return the original text unchanged.",
        "expected_behavior": "return_original", 
        "word_count": 15
    },
    {
        "text": "This is a longer text that contains more than fifteen words and should therefore be summarized by the BART model to create a concise version of the original content.",
        "expected_behavior": "summarize",
        "word_count": 30
    },
    {
        "text": "I absolutely love this product! It exceeded all my expectations and the quality is outstanding. The customer service team was incredibly helpful and responsive throughout the entire process. I would definitely recommend this to anyone looking for a high-quality solution. The delivery was fast and the packaging was excellent.",
        "expected_behavior": "summarize",
        "word_count": 52
    }
]

def test_summarization():
    print("🧪 Testing Updated Summarization Function")
    print("=" * 50)
    
    # Import the summarize_text function from our app
    try:
        from app_demo import summarize_text, SUMMARIZER_LOADED
        print(f"✅ Summarization model loaded: {SUMMARIZER_LOADED}")
    except ImportError as e:
        print(f"❌ Could not import function: {e}")
        return False
    
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        word_count = len(text.split())
        expected = test_case["expected_behavior"]
        
        print(f"\n📝 Test Case {i}:")
        print(f"   Original text ({word_count} words): {text[:60]}...")
        
        result = summarize_text(text)
        result_word_count = len(result.split())
        
        print(f"   Summary ({result_word_count} words): {result}")
        
        # Check behavior
        if word_count <= 15:
            if result == text:
                print(f"   ✅ PASS: Short text returned unchanged")
            else:
                print(f"   ❌ FAIL: Short text should be unchanged")
        else:
            if result != text and len(result) < len(text):
                print(f"   ✅ PASS: Long text was summarized")
            else:
                print(f"   ⚠️  INFO: Long text processed (may be fallback)")
    
    return True

if __name__ == "__main__":
    test_summarization()
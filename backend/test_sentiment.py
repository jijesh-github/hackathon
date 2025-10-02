"""
Test the enhanced sentiment analysis function directly
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_sentiment_analysis():
    print("🧪 Testing Enhanced Sentiment Analysis")
    print("=" * 50)
    
    # Import the predict_sentiment function
    try:
        from app_enhanced import predict_sentiment
        print("✅ Successfully imported sentiment function")
    except ImportError as e:
        print(f"❌ Could not import function: {e}")
        return False
    
    # Test cases with expected results
    test_cases = [
        ("Great product!", "POSITIVE"),
        ("Bad quality", "NEGATIVE"), 
        ("The product arrived damaged and the packaging was poor.", "NEGATIVE"),
        ("Terrible experience overall", "NEGATIVE"),
        ("I am extremely disappointed with this purchase.", "NEGATIVE"),
        ("Perfect for my needs and works as expected.", "POSITIVE"),
        ("Outstanding customer service!", "POSITIVE"),
        ("OK product", "NEUTRAL"),
        ("This is an average product with decent quality.", "NEUTRAL"),
    ]
    
    correct_predictions = 0
    total_tests = len(test_cases)
    
    for i, (text, expected) in enumerate(test_cases, 1):
        predicted = predict_sentiment(text)
        is_correct = predicted == expected
        status = "✅ PASS" if is_correct else "❌ FAIL"
        
        print(f"\n📝 Test {i}: {status}")
        print(f"   Text: '{text}'")
        print(f"   Expected: {expected} | Predicted: {predicted}")
        
        if is_correct:
            correct_predictions += 1
        else:
            print(f"   ⚠️  Mismatch detected!")
    
    accuracy = (correct_predictions / total_tests) * 100
    print(f"\n📊 RESULTS:")
    print(f"   Correct: {correct_predictions}/{total_tests}")
    print(f"   Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 80:
        print("✅ Sentiment analysis is working well!")
    else:
        print("❌ Sentiment analysis needs improvement")
    
    return accuracy >= 80

if __name__ == "__main__":
    test_sentiment_analysis()
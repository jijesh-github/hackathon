"""
Test sentiment analysis with the actual hackathon comments
"""
import pandas as pd
import requests
import json

def test_with_actual_data():
    print("🔍 Testing with Actual Hackathon Comments")
    print("=" * 50)
    
    # First let's check what the API detects
    try:
        print("📤 Testing with actual hackathon_comments.csv...")
        
        # Copy the file to our backend directory for testing
        import shutil
        source_path = "c:\\Users\\RAMSUNDAR\\Downloads\\hackathon_comments.csv"
        dest_path = "hackathon_comments_test.csv"
        shutil.copy2(source_path, dest_path)
        print(f"✅ Copied file to {dest_path}")
        
        with open('hackathon_comments_test.csv', 'rb') as file:
            files = {'file': ('hackathon_comments_test.csv', file, 'text/csv')}
            response = requests.post('http://localhost:8000/analyze', files=files, timeout=30)
            
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Analysis completed successfully!")
            
            # Show current results
            sentiment_stats = result['analysis_summary']['sentiment_analysis']
            print(f"\n📊 CURRENT API RESULTS:")
            for sentiment, count in sentiment_stats['counts'].items():
                percentage = sentiment_stats['percentages'][sentiment]
                print(f"   {sentiment}: {count} comments ({percentage}%)")
            
            print(f"\n📝 DETAILED BREAKDOWN:")
            print("-" * 60)
            
            for i, comment in enumerate(result['detailed_results'], 1):
                text = comment['original_text']
                sentiment = comment['sentiment'] 
                print(f"{i:2d}. {sentiment:8s} | {text}")
            
            # Expected vs Actual comparison
            expected_positive = 8
            expected_negative = 7  # User said this was correct in morning
            actual_positive = sentiment_stats['counts']['POSITIVE']
            actual_negative = sentiment_stats['counts']['NEGATIVE']
            
            print(f"\n🔍 COMPARISON WITH MORNING RESULTS:")
            print(f"   Expected Positive: {expected_positive} | Current: {actual_positive}")
            print(f"   Expected Negative: {expected_negative} | Current: {actual_negative}")
            
            if actual_positive == expected_positive and actual_negative == expected_negative:
                print("✅ Results match morning analysis!")
            else:
                print("❌ Results differ from morning analysis!")
                print("💡 Sentiment analysis logic may have changed")
            
            return True
            
        else:
            print(f"❌ Analysis failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def manual_sentiment_check():
    """Manually analyze each comment to see expected results"""
    print(f"\n🔍 MANUAL ANALYSIS OF EACH COMMENT:")
    print("-" * 60)
    
    comments = [
        "This amendment will help startups grow and encourage innovation.",
        "The proposal is very clear and easy to follow, excellent work.",
        "This draft improves transparency and benefits small businesses.", 
        "The suggested changes are progressive and much needed for our industry.",
        "Great initiative, this will simplify compliance for everyone.",
        "This draft is confusing and difficult to understand.",
        "The changes increase compliance burden for small businesses.",
        "The proposal is impractical and may lead to more corruption.",
        "Too many legal terms make this amendment inaccessible to common people.",
        "This will only increase paperwork and delay processes.",
        "The amendment covers many important areas but needs more clarity.",
        "The proposal has both good points and some drawbacks.",
        "It is neither very helpful nor very harmful, needs improvement.",
        "The draft is average, could be better with some modifications.",
        "This amendment does not affect my work much, but I appreciate the effort."
    ]
    
    expected_results = []
    
    for i, text in enumerate(comments, 1):
        # Manual classification based on content
        if i <= 5:  # Comments 1-5 seem positive
            expected = "POSITIVE"
        elif i >= 6 and i <= 10:  # Comments 6-10 seem negative  
            expected = "NEGATIVE"
        else:  # Comments 11-15 seem neutral/mixed
            expected = "NEUTRAL"
            
        expected_results.append(expected)
        print(f"{i:2d}. {expected:8s} | {text}")
    
    # Count expected results
    pos_count = expected_results.count("POSITIVE")  
    neg_count = expected_results.count("NEGATIVE")
    neu_count = expected_results.count("NEUTRAL")
    
    print(f"\n📊 EXPECTED MANUAL ANALYSIS:")
    print(f"   POSITIVE: {pos_count} comments")
    print(f"   NEGATIVE: {neg_count} comments") 
    print(f"   NEUTRAL: {neu_count} comments")
    
    return expected_results

if __name__ == "__main__":
    # First do manual analysis
    expected = manual_sentiment_check()
    
    # Then test API  
    success = test_with_actual_data()
    
    if success:
        print(f"\n🎯 ANALYSIS COMPLETE!")
        print(f"✅ Check if current results match your morning results")
        print(f"✅ If not, we may need to adjust the sentiment logic")
    else:
        print(f"\n❌ Could not test API - server may not be running")
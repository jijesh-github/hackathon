"""
Test the API with improved sentiment analysis
"""
import requests
import json

def test_improved_sentiment():
    print("🧪 Testing Improved Sentiment Analysis via API")
    print("=" * 55)
    
    try:
        # Test with our CSV that has clear negative comments
        print("📤 Testing with CSV containing negative comments...")
        
        with open('test_15_word_rule.csv', 'rb') as file:
            files = {'file': ('test_15_word_rule.csv', file, 'text/csv')}
            response = requests.post('http://localhost:8000/analyze', files=files, timeout=30)
            
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Analysis completed successfully!")
            
            # Show sentiment distribution
            sentiment_stats = result['analysis_summary']['sentiment_analysis']
            print(f"\n📊 SENTIMENT DISTRIBUTION:")
            for sentiment, count in sentiment_stats['counts'].items():
                percentage = sentiment_stats['percentages'][sentiment]
                print(f"   {sentiment}: {count} comments ({percentage}%)")
            
            # Show some examples of each sentiment
            print(f"\n📝 SENTIMENT EXAMPLES:")
            
            sentiments_shown = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
            
            for comment in result['detailed_results']:
                sentiment = comment['sentiment']
                if sentiments_shown[sentiment] < 2:  # Show max 2 examples per sentiment
                    text = comment['original_text'][:60] + "..." if len(comment['original_text']) > 60 else comment['original_text']
                    print(f"   {sentiment}: '{text}'")
                    sentiments_shown[sentiment] += 1
            
            # Check if we're correctly detecting negative comments
            negative_count = sentiment_stats['counts']['NEGATIVE']
            if negative_count > 0:
                print(f"\n✅ SUCCESS: Detected {negative_count} negative comments!")
            else:
                print(f"\n❌ ISSUE: No negative comments detected (should find several)")
            
            return negative_count > 0
            
        else:
            print(f"❌ Analysis failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_improved_sentiment()
    
    if success:
        print(f"\n🎉 SENTIMENT ANALYSIS WORKING CORRECTLY!")
        print(f"✅ Negative comments are being properly detected")
    else:
        print(f"\n❌ Sentiment analysis still needs adjustment")
        print(f"💡 Check the keyword lists and matching logic")
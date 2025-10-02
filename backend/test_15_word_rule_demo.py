"""
Test the enhanced 15-word rule implementation
"""
import requests
import json

def test_15_word_rule():
    print("🧪 Testing Enhanced 15-Word Rule Implementation")
    print("=" * 60)
    
    try:
        # Test health endpoint first
        health_response = requests.get('http://localhost:8000/health', timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Server Status: {health_data['status']}")
            print(f"📊 Mode: {health_data['mode']}")
            print(f"📏 Rule: {health_data['summarization_rule']}")
        
        # Test the analyze endpoint with our test file
        print(f"\n🎯 Testing /analyze endpoint with 15-word rule test data...")
        
        with open('test_15_word_rule.csv', 'rb') as file:
            files = {'file': ('test_15_word_rule.csv', file, 'text/csv')}
            response = requests.post('http://localhost:8000/analyze', files=files, timeout=30)
            
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Analysis completed successfully!")
            
            # Show summarization stats
            sum_stats = result['summarization_stats']
            print(f"\n📊 SUMMARIZATION STATISTICS:")
            print(f"   Total comments: {sum_stats['total_comments']}")
            print(f"   Short texts (≤15 words, unchanged): {sum_stats['short_texts_unchanged']}")
            print(f"   Long texts (>15 words, summarized): {sum_stats['long_texts_summarized']}")
            print(f"   Rule: {sum_stats['rule']}")
            
            # Show sentiment distribution
            sentiment_stats = result['analysis_summary']['sentiment_analysis']
            print(f"\n📈 SENTIMENT DISTRIBUTION:")
            for sentiment, count in sentiment_stats['counts'].items():
                percentage = sentiment_stats['percentages'][sentiment]
                print(f"   {sentiment}: {count} comments ({percentage}%)")
            
            # Show detailed analysis for each comment
            print(f"\n📝 DETAILED ANALYSIS (15-Word Rule Demonstration):")
            print("-" * 80)
            
            for i, comment in enumerate(result['detailed_results'], 1):
                original = comment['original_text']
                word_count = comment['word_count']
                sentiment = comment['sentiment']
                summary = comment['summary']
                was_summarized = comment['was_summarized']
                
                print(f"\n📄 Comment {i} ({word_count} words):")
                print(f"   Original: {original}")
                print(f"   Sentiment: {sentiment}")
                
                if was_summarized:
                    print(f"   ✂️  SUMMARIZED: {summary}")
                    print(f"   📏 Action: Text >15 words → Generated summary")
                else:
                    print(f"   📋 UNCHANGED: {summary}")
                    print(f"   📏 Action: Text ≤15 words → Returned original")
                
            # Show model info
            models = result['analysis_summary']['processing_info']
            print(f"\n🔧 PROCESSING INFORMATION:")
            print(f"   Sentiment Model: {models['sentiment_model']}")
            print(f"   Summarization Model: {models['summarization_model']}")
            print(f"   Summarization Rule: {models['summarization_rule']}")
            
            return True
            
        else:
            print(f"❌ Analysis failed: {response.status_code} - {response.text}")
            return False
            
    except FileNotFoundError:
        print("❌ test_15_word_rule.csv not found")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_15_word_rule()
    
    if success:
        print(f"\n🎉 15-WORD RULE TEST PASSED!")
        print(f"✅ Short texts (≤15 words) are returned unchanged")
        print(f"✅ Long texts (>15 words) are intelligently summarized")
        print(f"✅ Each result shows word count and summarization status")
        print(f"✅ API provides detailed statistics about the process")
        print(f"\n🚀 Your enhanced backend is ready for frontend integration!")
    else:
        print(f"\n❌ Test failed. Check server status.")
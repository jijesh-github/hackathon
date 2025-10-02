"""
Comprehensive test for the combined sentiment analysis and summarization API
"""
import requests
import json
import time

def test_api_complete():
    """Complete test of the /analyze endpoint"""
    
    print("🚀 TESTING COMBINED SENTIMENT ANALYSIS & SUMMARIZATION API")
    print("=" * 60)
    
    # Test basic endpoints first
    try:
        print("1️⃣ Testing Health Endpoint...")
        health_response = requests.get('http://localhost:8000/health', timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ Status: {health_data['status']}")
            print(f"   📊 Mode: {health_data['mode']}")
        
        print("\n2️⃣ Testing Root Endpoint...")
        root_response = requests.get('http://localhost:8000/', timeout=5)
        if root_response.status_code == 200:
            root_data = root_response.json()
            print(f"   ✅ API: {root_data['message']}")
            print(f"   🔧 Version: {root_data['version']}")
        
    except Exception as e:
        print(f"❌ Basic endpoint test failed: {e}")
        return False
    
    # Test the main analyze endpoint
    try:
        print("\n3️⃣ Testing /analyze Endpoint with Sample Data...")
        
        # Open and send the CSV file
        with open('sample_comments.csv', 'rb') as file:
            files = {'file': ('sample_comments.csv', file, 'text/csv')}
            response = requests.post('http://localhost:8000/analyze', files=files, timeout=30)
            
        if response.status_code == 200:
            result = response.json()
            
            print("   ✅ Analysis completed successfully!")
            print(f"\n📊 ANALYSIS SUMMARY:")
            print(f"   Status: {result['status']}")
            print(f"   Mode: {result['mode']}")
            print(f"   Total Comments: {result['analysis_summary']['total_comments']}")
            
            # Sentiment Statistics
            sentiment_stats = result['analysis_summary']['sentiment_analysis']
            print(f"\n📈 SENTIMENT DISTRIBUTION:")
            for sentiment, count in sentiment_stats['counts'].items():
                percentage = sentiment_stats['percentages'][sentiment]
                print(f"   {sentiment}: {count} comments ({percentage}%)")
            
            # Model Information
            models = result['analysis_summary']['processing_info']
            print(f"\n🔧 PROCESSING MODELS:")
            print(f"   Sentiment: {models['sentiment_model']}")
            print(f"   Summarization: {models['summarization_model']}")
            
            # Sample Results
            print(f"\n📝 SAMPLE RESULTS (First 3 comments):")
            for i, comment in enumerate(result['detailed_results'][:3], 1):
                print(f"\n   📄 Comment {i}:")
                print(f"      Original: {comment['original_text'][:80]}...")
                print(f"      Sentiment: {comment['sentiment']}")
                print(f"      Summary: {comment['summary']}")
            
            # Visualization Data
            if 'visualization_data' in result:
                print(f"\n📊 VISUALIZATION DATA FOR FRONTEND:")
                for item in result['visualization_data']['pie_chart_data']:
                    print(f"   {item['label']}: {item['value']} ({item['percentage']}%)")
            
            print(f"\n🎯 PERFECT FOR YOUR FRONTEND!")
            print("   • Pie chart data ready for visualization")
            print("   • Individual comment analysis available")
            print("   • Both sentiment and summary for each comment")
            print("   • Statistics for overall analysis")
            
            return True
            
        else:
            print(f"❌ Analysis failed: {response.status_code} - {response.text}")
            return False
            
    except FileNotFoundError:
        print("❌ sample_comments.csv not found")
        return False
    except Exception as e:
        print(f"❌ Analysis test failed: {e}")
        return False

if __name__ == "__main__":
    print("⏳ Waiting for server to start...")
    time.sleep(2)  # Give server time to start
    
    success = test_api_complete()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("🔗 Your API is ready for frontend integration!")
        print("📚 View full API docs at: http://localhost:8000/docs")
    else:
        print("\n❌ Some tests failed. Check server status.")
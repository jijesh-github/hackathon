"""
Test script for the combined sentiment analysis and summarization API
"""
import requests
import json

def test_analyze_endpoint():
    """Test the /analyze endpoint with the sample CSV"""
    
    print("🧪 Testing the /analyze endpoint...")
    
    try:
        # Open the sample CSV file
        with open('sample_comments.csv', 'rb') as file:
            files = {'file': ('sample_comments.csv', file, 'text/csv')}
            
            # Send request to analyze endpoint
            response = requests.post('http://localhost:8000/analyze', files=files)
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ API Response received successfully!")
                print("\n📊 ANALYSIS SUMMARY:")
                print(f"Total Comments: {result['analysis_summary']['total_comments']}")
                
                sentiment_stats = result['analysis_summary']['sentiment_analysis']
                print(f"\n📈 SENTIMENT DISTRIBUTION:")
                for sentiment, count in sentiment_stats['counts'].items():
                    percentage = sentiment_stats['percentages'][sentiment]
                    print(f"  {sentiment}: {count} comments ({percentage}%)")
                
                print(f"\n🔧 MODELS USED:")
                models = result['analysis_summary']['processing_info']
                print(f"  Sentiment: {models['sentiment_model']}")
                print(f"  Summarization: {models['summarization_model']}")
                
                print(f"\n📝 DETAILED RESULTS (First 3 comments):")
                for i, comment in enumerate(result['detailed_results'][:3]):
                    print(f"\n  Comment {i+1}:")
                    print(f"    Original: {comment['original_text'][:100]}...")
                    print(f"    Sentiment: {comment['sentiment']}")
                    print(f"    Summary: {comment['summary']}")
                
                return True
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return False
                
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure it's running on http://localhost:8000")
        return False
    except FileNotFoundError:
        print("❌ Error: sample_comments.csv not found")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:8000/health')
        if response.status_code == 200:
            print("✅ Health check passed!")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except:
        print("❌ Could not reach health endpoint")
        return False

if __name__ == "__main__":
    print("🚀 Starting API Tests...\n")
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    
    if health_ok:
        # Test main analyze endpoint
        test_analyze_endpoint()
    else:
        print("❌ Server not responding. Please check if it's running.")
    
    print("\n🎉 Test completed!")
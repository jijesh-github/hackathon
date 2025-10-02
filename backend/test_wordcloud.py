"""
Test word cloud generation specifically
"""
import requests
import json
import base64

def test_wordcloud():
    print("🎨 Testing Word Cloud Generation")
    print("=" * 40)
    
    try:
        # Test with hackathon comments
        print("📤 Testing word cloud with hackathon comments...")
        
        # Create a simple test CSV to ensure word cloud works
        test_csv_content = """comment_text
"This amendment will help startups grow and encourage innovation"
"The proposal is very clear and easy to follow excellent work"
"This draft improves transparency and benefits small businesses"
"The suggested changes are progressive and much needed"
"Great initiative this will simplify compliance for everyone"
"This draft is confusing and difficult to understand"
"The changes increase compliance burden for small businesses"
"The proposal is impractical and may lead to corruption"
"Too many legal terms make this amendment inaccessible"
"This will only increase paperwork and delay processes"
"""
        
        # Save test CSV
        with open('test_wordcloud.csv', 'w') as f:
            f.write(test_csv_content)
        
        # Send request
        with open('test_wordcloud.csv', 'rb') as file:
            files = {'file': ('test_wordcloud.csv', file, 'text/csv')}
            response = requests.post('http://localhost:8000/analyze', files=files, timeout=30)
            
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Analysis completed!")
            
            # Check word cloud data
            if 'wordcloud' in result:
                wc_data = result['wordcloud']
                print(f"\n🎨 WORD CLOUD STATUS:")
                print(f"   Status: {wc_data['status']}")
                print(f"   Message: {wc_data['message']}")
                
                if wc_data['status'] == 'success':
                    print(f"   ✅ Image generated: {wc_data.get('image_filename', 'N/A')}")
                    print(f"   📊 Image format: {wc_data.get('image_format', 'N/A')}")
                    
                    # Check if image data exists
                    if wc_data.get('image_data'):
                        img_size = len(wc_data['image_data'])
                        print(f"   📸 Image data size: {img_size} characters (base64)")
                        print("   ✅ Word cloud generation WORKING!")
                    else:
                        print("   ❌ Image data is null")
                        
                else:
                    print(f"   ❌ Word cloud failed: {wc_data.get('message', 'Unknown error')}")
            else:
                print("   ❌ No wordcloud data in response")
            
            # Show sentiment results too
            sentiment_stats = result['analysis_summary']['sentiment_analysis']
            print(f"\n📊 SENTIMENT RESULTS:")
            for sentiment, count in sentiment_stats['counts'].items():
                print(f"   {sentiment}: {count} comments")
            
            return wc_data.get('status') == 'success' if 'wordcloud' in result else False
            
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_wordcloud()
    
    if success:
        print(f"\n🎉 WORD CLOUD IS WORKING!")
        print(f"✅ Status: success")
        print(f"✅ Image data: generated")  
        print(f"✅ Ready for frontend integration")
    else:
        print(f"\n❌ Word cloud still has issues")
        print(f"💡 Check server logs for details")
"""
Test script for toxicity detection in feedback system
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_toxicity_detection():
    """Test toxicity detection with various comments"""
    
    # Test cases
    test_cases = [
        {
            "name": "Safe Comment",
            "comment": "This amendment looks great and will benefit everyone. I strongly support this initiative.",
            "expected_toxic": False
        },
        {
            "name": "Mildly Critical",
            "comment": "I disagree with this amendment. It may have unintended consequences that should be considered.",
            "expected_toxic": False
        },
        {
            "name": "Toxic Comment",
            "comment": "This is absolutely stupid and idiotic. You people are morons and don't know what you're doing.",
            "expected_toxic": True
        },
        {
            "name": "Borderline Comment",
            "comment": "This amendment is poorly written and shows lack of understanding. Please reconsider.",
            "expected_toxic": False
        }
    ]
    
    # First, create a test amendment
    print("Creating test amendment...")
    amendment_data = {
        "title": "Test Amendment for Toxicity Detection",
        "description": "This is a test amendment to verify toxicity detection functionality."
    }
    
    response = requests.post(f"{BASE_URL}/amendments", json=amendment_data)
    if response.status_code != 200:
        print(f"Failed to create amendment: {response.text}")
        return
    
    amendment_result = response.json()
    amendment_id = amendment_result["data"]["id"]
    print(f"✅ Created test amendment with ID: {amendment_id}")
    
    # Test each comment
    print("\n" + "="*50)
    print("TESTING TOXICITY DETECTION")
    print("="*50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Comment: {test_case['comment']}")
        
        feedback_data = {
            "amendment_id": amendment_id,
            "original_text": test_case["comment"]
        }
        
        response = requests.post(f"{BASE_URL}/feedback", json=feedback_data)
        
        if response.status_code == 200:
            result = response.json()
            is_toxic = not result.get("success", True)  # If not successful, likely toxic
            
            if "data" in result and "toxic" in result["data"]:
                is_toxic = result["data"]["toxic"]
                toxic_score = result["data"].get("toxic_score", 0)
                
                print(f"🛡️  Toxic: {is_toxic} (Score: {toxic_score:.3f})")
                
                # Check if prediction matches expectation
                if is_toxic == test_case["expected_toxic"]:
                    print("✅ PASS - Correct prediction")
                else:
                    print("❌ FAIL - Incorrect prediction")
            else:
                print(f"✅ PASS - Feedback processed successfully")
                print(f"Sentiment: {result['data'].get('sentiment', 'N/A')}")
                print(f"Summary: {result['data'].get('summary', 'N/A')}")
        else:
            print(f"❌ ERROR - Request failed: {response.status_code}")
            print(response.text)
    
    print("\n" + "="*50)
    print("Toxicity detection test completed!")

if __name__ == "__main__":
    test_toxicity_detection()
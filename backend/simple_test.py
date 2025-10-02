"""
Simple test to verify API functionality
"""
import requests
import time

def simple_test():
    print("🧪 Testing API...")
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get('http://localhost:8000/health', timeout=10)
        print(f"Health status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        
        # Test root endpoint
        print("\nTesting root endpoint...")
        response = requests.get('http://localhost:8000/', timeout=10)
        print(f"Root status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"API Message: {result['message']}")
            print(f"Models Status: {result['models_status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    simple_test()
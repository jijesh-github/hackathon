import requests
import time

def test_server():
    try:
        # Test if server is running
        response = requests.get("http://localhost:8000")
        print(f"Server is running! Status: {response.status_code}")
        print(f"Response: {response.text}")
        return True
    except requests.exceptions.ConnectionError:
        print("Server is not running or not accessible")
        return False

if __name__ == "__main__":
    test_server()
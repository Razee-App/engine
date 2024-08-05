import requests
import json

# Replace with your actual API URL
API_URL = "http://localhost:8000"  # Adjust if your API is hosted elsewhere

def test_recommend_tests():
    # Endpoint
    url = f"{API_URL}/recommend-tests"

    # Test data
    data = {
        "healthGoals": ["weight loss", "improve cardiovascular health"],
        "currentDiseases": ["hypertension", "high cholesterol"],
        "userId": "test_user_123"
    }

    # Headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        # Send POST request
        response = requests.post(url, data=data, headers=headers)

        # Check if request was successful
        if response.status_code == 200:
            print("Request successful!")
            print("Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Request failed with status code: {response.status_code}")
            print("Response:")
            print(response.text)

    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_recommend_tests()
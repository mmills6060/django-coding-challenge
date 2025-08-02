#!/usr/bin/env python3
"""
Test script for the IoT Payload Parser Django application.

This script demonstrates how to send payloads to the API and verify the results.
"""

import requests
import json
import base64

# Configuration
BASE_URL = "http://localhost:8000"
API_TOKEN = None  # Will be obtained from the API

def get_auth_token(username="admin", password="admin123"):
    """Get authentication token from the API."""
    url = f"{BASE_URL}/api/token/"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()["token"]
    else:
        raise Exception(f"Failed to get token: {response.text}")

def send_payload(token, payload_data):
    """Send a payload to the API."""
    url = f"{BASE_URL}/api/receive/"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=payload_data)
    return response

def test_passing_payload():
    """Test with a passing payload (data = 1)."""
    print("Testing PASSING payload...")
    
    # Example payload with data = 1 (Base64: "AQ==")
    payload = {
        "fCnt": 100,
        "devEUI": "abcdabcdabcdabcd",
        "data": "AQ==",  # Base64 encoded "1"
        "rxInfo": [
            {
                "gatewayID": "1234123412341234",
                "name": "G1",
                "time": "2022-07-19T11:00:00",
                "rssi": -57,
                "loRaSNR": 10
            }
        ],
        "txInfo": {
            "frequency": 86810000,
            "dr": 5
        }
    }
    
    response = send_payload(API_TOKEN, payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_failing_payload():
    """Test with a failing payload (data != 1)."""
    print("Testing FAILING payload...")
    
    # Example payload with data = 0 (Base64: "AA==")
    payload = {
        "fCnt": 101,
        "devEUI": "abcdabcdabcdabcd",
        "data": "AA==",  # Base64 encoded "0"
        "rxInfo": [
            {
                "gatewayID": "1234123412341234",
                "name": "G1",
                "time": "2022-07-19T11:01:00",
                "rssi": -58,
                "loRaSNR": 9
            }
        ],
        "txInfo": {
            "frequency": 86810000,
            "dr": 5
        }
    }
    
    response = send_payload(API_TOKEN, payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_duplicate_payload():
    """Test duplicate payload rejection."""
    print("Testing DUPLICATE payload rejection...")
    
    # Same fCnt as the first test
    payload = {
        "fCnt": 100,
        "devEUI": "abcdabcdabcdabcd",
        "data": "AQ==",
        "rxInfo": [],
        "txInfo": {}
    }
    
    response = send_payload(API_TOKEN, payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_invalid_base64():
    """Test invalid Base64 data."""
    print("Testing INVALID Base64 data...")
    
    payload = {
        "fCnt": 102,
        "devEUI": "abcdabcdabcdabcd",
        "data": "invalid_base64!",
        "rxInfo": [],
        "txInfo": {}
    }
    
    response = send_payload(API_TOKEN, payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def get_devices():
    """Get all devices."""
    print("Getting all devices...")
    
    url = f"{BASE_URL}/api/devices/"
    headers = {
        "Authorization": f"Token {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def get_payloads():
    """Get all payloads."""
    print("Getting all payloads...")
    
    url = f"{BASE_URL}/api/payloads/"
    headers = {
        "Authorization": f"Token {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def main():
    """Main test function."""
    global API_TOKEN
    
    print("IoT Payload Parser Test Script")
    print("=" * 50)
    
    try:
        # Get authentication token
        print("Getting authentication token...")
        API_TOKEN = get_auth_token()
        print(f"Token obtained: {API_TOKEN[:10]}...")
        print("-" * 50)
        
        # Run tests
        test_passing_payload()
        test_failing_payload()
        test_duplicate_payload()
        test_invalid_base64()
        
        # Get results
        get_devices()
        get_payloads()
        
        print("All tests completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the Django server is running on http://localhost:8000")

if __name__ == "__main__":
    main() 
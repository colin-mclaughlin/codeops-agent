#!/usr/bin/env python3
"""
Test script for Phase 4 backend implementation.
Tests the new endpoints and functionality.
"""

import urllib.request
import urllib.parse
import json
import sys

def test_endpoint(url, expected_status=200):
    """Test an endpoint and return the response."""
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode()
            print(f"✓ {url} - Status: {response.status}")
            try:
                json_data = json.loads(data)
                print(f"  Response: {json.dumps(json_data, indent=2)}")
                return json_data
            except json.JSONDecodeError:
                print(f"  Response: {data}")
                return data
    except urllib.error.HTTPError as e:
        print(f"✗ {url} - HTTP Error: {e.code}")
        return None
    except Exception as e:
        print(f"✗ {url} - Error: {e}")
        return None

def main():
    """Run all endpoint tests."""
    base_url = "http://localhost:8000"
    
    print("Testing Phase 4 Backend Implementation")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    test_endpoint(f"{base_url}/health")
    
    # Test 2: Agent runs endpoint (should return empty list initially)
    print("\n2. Testing /agent/runs endpoint...")
    test_endpoint(f"{base_url}/agent/runs")
    
    # Test 3: Context endpoint with dummy commit
    print("\n3. Testing /context endpoint...")
    test_endpoint(f"{base_url}/context?commit_sha=dummy123")
    
    # Test 4: Context stats
    print("\n4. Testing /context/stats endpoint...")
    test_endpoint(f"{base_url}/context/stats")
    
    # Test 5: Context query
    print("\n5. Testing /context/query endpoint...")
    query_data = json.dumps({"query_text": "build failure", "top_k": 3}).encode()
    req = urllib.request.Request(
        f"{base_url}/context/query?query_text=build%20failure&top_k=3",
        method="GET"
    )
    try:
        with urllib.request.urlopen(req) as response:
            data = response.read().decode()
            print(f"✓ /context/query - Status: {response.status}")
            json_data = json.loads(data)
            print(f"  Response: {json.dumps(json_data, indent=2)}")
    except Exception as e:
        print(f"✗ /context/query - Error: {e}")
    
    # Test 6: API docs
    print("\n6. Testing API docs...")
    test_endpoint(f"{base_url}/docs")
    
    print("\n" + "=" * 50)
    print("Testing completed!")

if __name__ == "__main__":
    main()

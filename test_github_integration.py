#!/usr/bin/env python3
"""
Test script for GitHub integration.
Tests the GitHub endpoints and functionality.
"""

import urllib.request
import urllib.parse
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
        if e.code == 400:
            error_data = e.read().decode()
            try:
                error_json = json.loads(error_data)
                print(f"  Error: {error_json.get('detail', 'Unknown error')}")
            except:
                print(f"  Error: {error_data}")
        return None
    except Exception as e:
        print(f"✗ {url} - Error: {e}")
        return None

def main():
    """Run GitHub integration tests."""
    base_url = "http://localhost:8000"
    
    print("Testing GitHub Integration")
    print("=" * 50)
    
    # Check if GITHUB_TOKEN is set
    if not os.getenv("GITHUB_TOKEN"):
        print("⚠️  GITHUB_TOKEN environment variable not set")
        print("   Please set it to test GitHub functionality")
        print("   Example: export GITHUB_TOKEN=your_token_here")
        return
    
    # Test repository (using a public repository for testing)
    test_repo = "octocat/Hello-World"
    
    print(f"\nTesting with repository: {test_repo}")
    
    # Test 1: Repository info
    print("\n1. Testing repository info...")
    test_endpoint(f"{base_url}/github/repo-info?repo={urllib.parse.quote(test_repo)}")
    
    # Test 2: Recent commits
    print("\n2. Testing recent commits...")
    test_endpoint(f"{base_url}/github/commits?repo={urllib.parse.quote(test_repo)}&limit=3")
    
    # Test 3: Workflow runs
    print("\n3. Testing workflow runs...")
    test_endpoint(f"{base_url}/github/workflows?repo={urllib.parse.quote(test_repo)}&limit=3")
    
    # Test 4: Health check
    print("\n4. Testing health check...")
    test_endpoint(f"{base_url}/healthz")
    
    # Test 5: API docs
    print("\n5. Testing API docs...")
    test_endpoint(f"{base_url}/docs")
    
    print("\n" + "=" * 50)
    print("GitHub integration testing completed!")
    print("\nNote: Some tests may fail if the repository doesn't have workflows or recent commits.")
    print("This is normal for testing repositories.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test script for Slack integration.
Tests the Slack endpoints and functionality.
"""

import urllib.request
import urllib.parse
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_endpoint(url, expected_status=200, method="GET", data=None, headers=None):
    """Test an endpoint and return the response."""
    try:
        if method == "GET":
            with urllib.request.urlopen(url) as response:
                response_data = response.read().decode()
                print(f"✓ {url} - Status: {response.status}")
                try:
                    json_data = json.loads(response_data)
                    print(f"  Response: {json.dumps(json_data, indent=2)}")
                    return json_data
                except json.JSONDecodeError:
                    print(f"  Response: {response_data}")
                    return response_data
        elif method == "POST":
            if data:
                data_bytes = json.dumps(data).encode('utf-8')
                if not headers:
                    headers = {'Content-Type': 'application/json'}
                req = urllib.request.Request(url, data=data_bytes, headers=headers, method='POST')
            else:
                req = urllib.request.Request(url, method='POST')
            
            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode()
                print(f"✓ {url} - Status: {response.status}")
                try:
                    json_data = json.loads(response_data)
                    print(f"  Response: {json.dumps(json_data, indent=2)}")
                    return json_data
                except json.JSONDecodeError:
                    print(f"  Response: {response_data}")
                    return response_data
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
    """Run Slack integration tests."""
    base_url = "http://localhost:8000"
    
    print("Testing Slack Integration")
    print("=" * 50)
    
    # Check if SLACK_WEBHOOK_URL is set
    if not os.getenv("SLACK_WEBHOOK_URL"):
        print("⚠️  SLACK_WEBHOOK_URL environment variable not set")
        print("   Please set it to test Slack functionality")
        print("   Example: export SLACK_WEBHOOK_URL=your_webhook_url_here")
        return
    
    print(f"\nSLACK_WEBHOOK_URL is configured")
    
    # Test 1: Test message
    print("\n1. Testing basic message...")
    test_endpoint(f"{base_url}/slack/test?msg=Hello%20from%20CodeOps%20Agent%20Test")
    
    # Test 2: Run summary (success)
    print("\n2. Testing run summary (success)...")
    summary_data = {
        "verdict": "success",
        "repo": "octocat/Hello-World",
        "run_log_id": 123
    }
    test_endpoint(f"{base_url}/slack/summary", method="POST", data=summary_data)
    
    # Test 3: Run summary (failure)
    print("\n3. Testing run summary (failure)...")
    summary_data_fail = {
        "verdict": "failure",
        "repo": "octocat/Hello-World",
        "run_log_id": 124,
        "pr_url": "https://github.com/octocat/Hello-World/pull/1"
    }
    test_endpoint(f"{base_url}/slack/summary", method="POST", data=summary_data_fail)
    
    # Test 4: PR notification
    print("\n4. Testing PR notification...")
    pr_data = {
        "action": "created",
        "repo": "octocat/Hello-World",
        "pr_number": 1,
        "pr_url": "https://github.com/octocat/Hello-World/pull/1",
        "title": "Test PR from CodeOps Agent"
    }
    test_endpoint(f"{base_url}/slack/pr-notification", method="POST", data=pr_data)
    
    # Test 5: Error notification
    print("\n5. Testing error notification...")
    error_data = {
        "error": "Test error from CodeOps Agent",
        "context": "Testing Slack error notifications"
    }
    test_endpoint(f"{base_url}/slack/error", method="POST", data=error_data)
    
    # Test 6: Health check
    print("\n6. Testing health check...")
    test_endpoint(f"{base_url}/healthz")
    
    # Test 7: API docs
    print("\n7. Testing API docs...")
    test_endpoint(f"{base_url}/docs")
    
    print("\n" + "=" * 50)
    print("Slack integration testing completed!")
    print("\nNote: Check your Slack channel for the test messages.")

if __name__ == "__main__":
    main()

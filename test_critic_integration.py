#!/usr/bin/env python3
"""
Test script for Critic Agent integration.
Tests the critic agent functionality and two-agent loop.
"""

import urllib.request
import urllib.parse
import json
import sys
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_endpoint(url, expected_status=200, method="GET", data=None, headers=None, timeout=120):
    """Test an endpoint and return the response."""
    try:
        print(f"Testing: {url}")
        if method == "POST":
            print("⏳ This may take up to 2 minutes for AI processing...")
        
        if method == "GET":
            with urllib.request.urlopen(url, timeout=timeout) as response:
                data = response.read().decode()
                print(f"✓ {url} - Status: {response.status}")
                try:
                    json_data = json.loads(data)
                    return json_data
                except json.JSONDecodeError:
                    print(f"  Response: {data}")
                    return data
        elif method == "POST":
            if data:
                data_bytes = json.dumps(data).encode('utf-8')
                if not headers:
                    headers = {'Content-Type': 'application/json'}
                req = urllib.request.Request(url, data=data_bytes, headers=headers, method='POST')
            else:
                req = urllib.request.Request(url, method='POST')
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read().decode()
                print(f"✓ {url} - Status: {response.status}")
                try:
                    json_data = json.loads(data)
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
    """Run Critic Agent integration tests."""
    base_url = "http://localhost:8000"
    
    print("Testing Critic Agent Integration")
    print("=" * 60)
    
    # Check if required environment variables are set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY environment variable not set")
        print("   Please set it to test Critic Agent functionality")
        return
    
    print(f"\nOPENAI_API_KEY is configured")
    
    # Test 1: Critic review endpoint
    print("\n1. Testing critic review endpoint...")
    review_data = {
        "plan": "Fix the build error by updating the configuration file and adding missing environment variables",
        "reflection": "This plan addresses the root cause by fixing both the configuration and environment setup",
        "context": "Build failed due to missing environment variable and incorrect configuration"
    }
    result1 = test_endpoint(f"{base_url}/critic/review", method="POST", data=review_data)
    
    if result1 and result1.get('confidence', 0) > 0:
        print(f"✅ Critic review completed successfully! Confidence: {result1.get('confidence', 0)}")
    else:
        print("❌ Critic review failed or returned unexpected result")
        return
    
    # Test 2: Quick review endpoint
    print("\n2. Testing quick review endpoint...")
    quick_review_data = {
        "plan": "Implement automated testing for the CI/CD pipeline to prevent future failures"
    }
    result2 = test_endpoint(f"{base_url}/critic/quick-review", method="POST", data=quick_review_data)
    
    if result2 and result2.get('confidence', 0) > 0:
        print(f"✅ Quick review completed successfully! Confidence: {result2.get('confidence', 0)}")
    else:
        print("❌ Quick review failed")
    
    # Test 3: LangGraph with critic integration
    print("\n3. Testing LangGraph with critic integration...")
    result3 = test_endpoint(f"{base_url}/agent/langgraph?commit_sha=critic_integration_test&repo=octocat/Hello-World")
    
    if result3 and result3.get('verdict') == 'success' and 'critique' in result3:
        print("✅ LangGraph with critic integration completed successfully!")
        print(f"  Verdict: {result3.get('verdict')}")
        print(f"  Latency: {result3.get('latency', 0):.2f} seconds")
        print(f"  Critic Confidence: {result3.get('critique', {}).get('confidence', 0)}")
    else:
        print("❌ LangGraph with critic integration failed")
    
    # Test 4: Metrics with critic data
    print("\n4. Testing metrics with critic data...")
    result4 = test_endpoint(f"{base_url}/metrics")
    
    if result4 and 'critic_runs' in result4:
        print("✅ Metrics include critic data!")
        print(f"  Critic Runs: {result4.get('critic_runs', 0)}")
        print(f"  Average Confidence: {result4.get('avg_confidence', 0)}")
    else:
        print("❌ Metrics missing critic data")
    
    # Test 5: Critic summary endpoint
    print("\n5. Testing critic summary endpoint...")
    summary_data = {
        "plan": "Deploy the fix to production after thorough testing",
        "reflection": "This approach ensures safety while addressing the issue",
        "context": "Production deployment needed for critical bug fix"
    }
    result5 = test_endpoint(f"{base_url}/critic/summary", method="POST", data=summary_data)
    
    if result5 and 'summary' in result5:
        print("✅ Critic summary generated successfully!")
        print(f"  Confidence: {result5.get('confidence', 0)}")
    else:
        print("❌ Critic summary failed")
    
    # Test 6: Health check
    print("\n6. Testing health check...")
    test_endpoint(f"{base_url}/healthz")
    
    # Test 7: API docs
    print("\n7. Testing API docs...")
    test_endpoint(f"{base_url}/docs")
    
    print("\n" + "=" * 60)
    print("Critic Agent integration testing completed!")
    print("\n📊 Summary:")
    print(f"  - Critic Review: {'✅ Success' if result1 and result1.get('confidence', 0) > 0 else '❌ Failed'}")
    print(f"  - Quick Review: {'✅ Success' if result2 and result2.get('confidence', 0) > 0 else '❌ Failed'}")
    print(f"  - LangGraph Integration: {'✅ Success' if result3 and 'critique' in result3 else '❌ Failed'}")
    print(f"  - Metrics Integration: {'✅ Success' if result4 and 'critic_runs' in result4 else '❌ Failed'}")
    print(f"  - Summary Generation: {'✅ Success' if result5 and 'summary' in result5 else '❌ Failed'}")
    
    if result1:
        print(f"\n🧠 Critic Performance:")
        print(f"  - Review Confidence: {result1.get('confidence', 0)}/100")
        print(f"  - Critique Length: {len(result1.get('critique', ''))} characters")
    
    if result3 and 'critique' in result3:
        print(f"  - LangGraph Critic Confidence: {result3.get('critique', {}).get('confidence', 0)}/100")
    
    if result4:
        print(f"  - Total Critic Runs: {result4.get('critic_runs', 0)}")
        print(f"  - Average Confidence: {result4.get('avg_confidence', 0)}")
    
    print("\n💡 Note: Check your Slack channel for critic review notifications!")

if __name__ == "__main__":
    main()

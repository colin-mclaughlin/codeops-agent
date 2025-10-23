#!/usr/bin/env python3
"""
Test script for LangGraph integration.
Tests the LangGraph reasoning pipeline and functionality.
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

def test_endpoint(url, expected_status=200, timeout=120):
    """Test an endpoint and return the response."""
    try:
        print(f"Testing: {url}")
        print("⏳ This may take up to 2 minutes for full reasoning pipeline...")
        
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = response.read().decode()
            print(f"✓ {url} - Status: {response.status}")
            try:
                json_data = json.loads(data)
                
                # Pretty print key information
                print(f"  Verdict: {json_data.get('verdict', 'unknown')}")
                print(f"  Latency: {json_data.get('latency', 0):.2f} seconds")
                print(f"  Commit SHA: {json_data.get('commit_sha', 'unknown')}")
                
                if 'context_analysis' in json_data:
                    analysis = json_data['context_analysis']
                    print(f"  Context Snippets: {analysis.get('snippet_count', 0)}")
                    print(f"  Analysis Preview: {analysis.get('analysis', '')[:100]}...")
                
                if 'action_plan' in json_data:
                    plan = json_data['action_plan']
                    print(f"  Plan Preview: {plan.get('plan', '')[:100]}...")
                
                if 'reflection' in json_data:
                    reflection = json_data['reflection']
                    print(f"  Reflection Preview: {reflection.get('reflection', '')[:100]}...")
                
                if 'execution' in json_data:
                    execution = json_data['execution']
                    print(f"  Execution Status: {execution.get('status', 'unknown')}")
                    print(f"  Actions Taken: {len(execution.get('actions_taken', []))}")
                
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
    """Run LangGraph integration tests."""
    base_url = "http://localhost:8000"
    
    print("Testing LangGraph Integration")
    print("=" * 60)
    
    # Check if required environment variables are set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY environment variable not set")
        print("   Please set it to test LangGraph functionality")
        print("   Example: export OPENAI_API_KEY=your_openai_key_here")
        return
    
    if not os.getenv("SLACK_WEBHOOK_URL"):
        print("⚠️  SLACK_WEBHOOK_URL environment variable not set")
        print("   Slack notifications will not work, but LangGraph will still function")
    
    print(f"\nOPENAI_API_KEY is configured")
    print(f"SLACK_WEBHOOK_URL: {'configured' if os.getenv('SLACK_WEBHOOK_URL') else 'not configured'}")
    
    # Test 1: Basic LangGraph reasoning with default parameters
    print("\n1. Testing LangGraph reasoning (default parameters)...")
    result1 = test_endpoint(f"{base_url}/agent/langgraph")
    
    if result1 and result1.get('verdict') == 'success':
        print("✅ LangGraph reasoning completed successfully!")
    else:
        print("❌ LangGraph reasoning failed or returned unexpected result")
        return
    
    # Test 2: LangGraph reasoning with specific commit SHA
    print("\n2. Testing LangGraph reasoning (specific commit)...")
    result2 = test_endpoint(f"{base_url}/agent/langgraph?commit_sha=abc123def456&repo=octocat/Hello-World")
    
    if result2 and result2.get('verdict') == 'success':
        print("✅ LangGraph reasoning with specific commit completed successfully!")
    else:
        print("❌ LangGraph reasoning with specific commit failed")
    
    # Test 3: LangGraph reasoning with different repository
    print("\n3. Testing LangGraph reasoning (different repository)...")
    result3 = test_endpoint(f"{base_url}/agent/langgraph?commit_sha=latest&repo=microsoft/vscode")
    
    if result3 and result3.get('verdict') == 'success':
        print("✅ LangGraph reasoning with different repository completed successfully!")
    else:
        print("❌ LangGraph reasoning with different repository failed")
    
    # Test 4: Health check
    print("\n4. Testing health check...")
    test_endpoint(f"{base_url}/healthz")
    
    # Test 5: API docs
    print("\n5. Testing API docs...")
    test_endpoint(f"{base_url}/docs")
    
    print("\n" + "=" * 60)
    print("LangGraph integration testing completed!")
    print("\n📊 Summary:")
    print(f"  - Test 1 (default): {'✅ Success' if result1 and result1.get('verdict') == 'success' else '❌ Failed'}")
    print(f"  - Test 2 (specific commit): {'✅ Success' if result2 and result2.get('verdict') == 'success' else '❌ Failed'}")
    print(f"  - Test 3 (different repo): {'✅ Success' if result3 and result3.get('verdict') == 'success' else '❌ Failed'}")
    
    if result1:
        print(f"\n⏱️  Average latency: {result1.get('latency', 0):.2f} seconds")
        print(f"🧠 Context analysis: {result1.get('context_analysis', {}).get('snippet_count', 0)} snippets processed")
        print(f"📋 Action plan: Generated successfully")
        print(f"🔍 Reflection: Completed successfully")
    
    print("\n💡 Note: Check your Slack channel for reasoning updates and summaries!")

if __name__ == "__main__":
    main()

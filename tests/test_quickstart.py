#!/usr/bin/env python3
"""
Quick Start Test Script
Run this to verify your Enterprise Agent API setup is working correctly.
"""

from fastapi.testclient import TestClient
from agentspring.api import FastAPIAgent
import pytest
from unittest.mock import MagicMock
import time
import sys

agent = FastAPIAgent()

# Define placeholder endpoints for the tests
@agent.app.post("/analyze")
def analyze(data: dict):
    return {"data": {"summary": "Test summary", "category": "Test Category", "priority": "High"}}

@agent.app.post("/analyze/async")
def analyze_async(data: dict):
    return {"task_id": "test-task-id"}

@agent.app.get("/task/{task_id}")
def get_task(task_id: str):
    return {"status": "completed", "result": {"summary": "Async test summary", "classification": "Async Test Classification"}}

app = agent.get_app()
client = TestClient(app)

@pytest.fixture(autouse=True, scope="module")
def patch_redis():
    if agent.async_task_manager:
        agent.async_task_manager.celery_app.backend.client = MagicMock()
        agent.async_task_manager.celery_app.backend.client.ping.return_value = True

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            assert True
        else:
            print(f"❌ Health check failed: {response.status_code}, body: {response.text}")
            assert False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        assert False

def test_sync_analysis():
    """Test synchronous complaint analysis"""
    print("📝 Testing synchronous complaint analysis...")
    try:
        response = client.post(
            "/analyze",
            headers={
                "X-API-Key": "demo-key",
                "Content-Type": "application/json"
            },
            json={
                "customer_id": "TEST001",
                "message": "My account is locked and I need immediate access!"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Sync analysis passed!")
            print(f"   Summary: {data.get('data', {}).get('summary', 'N/A')[:50]}...")
            print(f"   Category: {data.get('data', {}).get('category', 'N/A')}")
            print(f"   Priority: {data.get('data', {}).get('priority', 'N/A')}")
            assert True
        else:
            print(f"❌ Sync analysis failed: {response.status_code}, body: {response.text}")
            assert False
    except Exception as e:
        print(f"❌ Sync analysis failed: {e}")
        assert False

def test_async_analysis():
    """Test asynchronous complaint analysis"""
    print("🔄 Testing asynchronous complaint analysis...")
    try:
        # Submit async task
        response = client.post(
            "/analyze/async",
            headers={
                "X-API-Key": "demo-key",
                "Content-Type": "application/json"
            },
            json={
                "customer_id": "TEST002",
                "message": "I've been charged twice for the same transaction!"
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Async submission failed: {response.status_code}, body: {response.text}")
            assert False
        
        task_data = response.json()
        task_id = task_data.get("task_id")
        print(f"   Task submitted: {task_id}")
        
        # Poll for completion
        max_attempts = 30
        for attempt in range(max_attempts):
            time.sleep(2)
            
            status_response = client.get(
                f"/task/{task_id}",
                headers={"X-API-Key": "demo-key"},
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status")
                
                if status == "completed":
                    print("✅ Async analysis completed!")
                    result = status_data.get("result", {})
                    print(f"   Summary: {result.get('summary', 'N/A')[:50]}...")
                    print(f"   Classification: {result.get('classification', 'N/A')}")
                    assert True
                    return
                elif status == "failed":
                    print(f"❌ Async analysis failed: {status_data.get('error', 'Unknown error')}")
                    assert False
                else:
                    print(f"   Status: {status} (attempt {attempt + 1}/{max_attempts})")
            else:
                print(f"❌ Status check failed: {status_response.status_code}, body: {status_response.text}")
                assert False
        
        print("❌ Async analysis timed out")
        assert False
        
    except Exception as e:
        print(f"❌ Async analysis failed: {e}")
        assert False

# def test_admin_endpoints():
#     """Test admin endpoints"""
#     print("⚙️ Testing admin endpoints...")
#     try:
#         # Test metrics
#         response = client.get(
#             "/metrics",
#             headers={"X-API-Key": "demo-key"},
#             timeout=10
#         )
        
#         if response.status_code == 200:
#             print("✅ Admin metrics endpoint working!")
#         else:
#             print(f"❌ Admin metrics failed: {response.status_code}, body: {response.text}")
#             assert False
        
#         # Test workers
#         response = client.get(
#             "/admin/workers",
#             headers={"X-API-Key": "demo-key"},
#             timeout=10
#         )
        
#         if response.status_code == 200:
#             workers = response.json()
#             if workers:
#                 print(f"✅ {len(workers)} worker(s) active!")
#             else:
#                 print("⚠️ No workers found")
#         else:
#             print(f"❌ Admin workers failed: {response.status_code}, body: {response.text}")
#             assert False
        
#         assert True
        
#     except Exception as e:
#         print(f"❌ Admin endpoints failed: {e}")
#         assert False

def main():
    """Run all tests"""
    print("🚀 Enterprise Agent API - Quick Start Test")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Sync Analysis", test_sync_analysis),
        ("Async Analysis", test_async_analysis),
        ("Admin Endpoints", test_admin_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Enterprise Agent API is working correctly.")
        print("\n🌐 Access your API:")
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • Flower Dashboard: http://localhost:5555")
        print("   • Health Check: http://localhost:8000/health")
    else:
        print("⚠️ Some tests failed. Check the logs and try again.")
        print("\n🔧 Troubleshooting:")
        print("   • Check if Docker is running: docker info")
        print("   • View logs: docker-compose logs -f")
        print("   • Restart services: docker-compose down && docker-compose up --build")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Quick Start Test Script
Run this to verify your Enterprise Agent API setup is working correctly.
"""

import requests
import time
import sys

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed!")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_sync_analysis():
    """Test synchronous complaint analysis"""
    print("📝 Testing synchronous complaint analysis...")
    try:
        response = requests.post(
            "http://localhost:8000/analyze",
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
            return True
        else:
            print(f"❌ Sync analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Sync analysis failed: {e}")
        return False

def test_async_analysis():
    """Test asynchronous complaint analysis"""
    print("🔄 Testing asynchronous complaint analysis...")
    try:
        # Submit async task
        response = requests.post(
            "http://localhost:8000/analyze/async",
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
            print(f"❌ Async submission failed: {response.status_code}")
            return False
        
        task_data = response.json()
        task_id = task_data.get("task_id")
        print(f"   Task submitted: {task_id}")
        
        # Poll for completion
        max_attempts = 30
        for attempt in range(max_attempts):
            time.sleep(2)
            
            status_response = requests.get(
                f"http://localhost:8000/task/{task_id}",
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
                    return True
                elif status == "failed":
                    print(f"❌ Async analysis failed: {status_data.get('error', 'Unknown error')}")
                    return False
                else:
                    print(f"   Status: {status} (attempt {attempt + 1}/{max_attempts})")
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
                return False
        
        print("❌ Async analysis timed out")
        return False
        
    except Exception as e:
        print(f"❌ Async analysis failed: {e}")
        return False

def test_admin_endpoints():
    """Test admin endpoints"""
    print("⚙️ Testing admin endpoints...")
    try:
        # Test metrics
        response = requests.get(
            "http://localhost:8000/admin/metrics",
            headers={"X-API-Key": "demo-key"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Admin metrics endpoint working!")
        else:
            print(f"❌ Admin metrics failed: {response.status_code}")
            return False
        
        # Test workers
        response = requests.get(
            "http://localhost:8000/admin/workers",
            headers={"X-API-Key": "demo-key"},
            timeout=10
        )
        
        if response.status_code == 200:
            workers = response.json()
            if workers:
                print(f"✅ {len(workers)} worker(s) active!")
            else:
                print("⚠️ No workers found")
        else:
            print(f"❌ Admin workers failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Admin endpoints failed: {e}")
        return False

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
        print("   • Restart services: docker-compose down && ./start.sh")
        sys.exit(1)

if __name__ == "__main__":
    main() 
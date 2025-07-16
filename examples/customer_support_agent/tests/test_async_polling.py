#!/usr/bin/env python3
"""
Better Async Polling Examples - Alternatives to Sleep Calls
"""
import time
import requests
import json
from typing import Dict, Any

class AsyncTaskPoller:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "demo-key"):
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "X-Tenant-ID": "default",
            "Content-Type": "application/json"
        }
    
    def submit_task(self, customer_id: str, message: str) -> str:
        """Submit async task and return task_id"""
        payload = {
            "customer_id": customer_id,
            "message": message
        }
        
        response = requests.post(
            f"{self.base_url}/analyze/async",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        
        result = response.json()
        return result["task_id"]
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get current task status"""
        response = requests.get(
            f"{self.base_url}/task/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def poll_with_exponential_backoff(self, task_id: str, max_attempts: int = 30) -> Dict[str, Any]:
        """
        Poll with exponential backoff - better than fixed sleep
        """
        print(f"🔄 Polling task {task_id} with exponential backoff...")
        
        for attempt in range(max_attempts):
            status = self.get_task_status(task_id)
            
            if status["status"] == "completed":
                print(f"✅ Task completed after {attempt + 1} attempts!")
                return status
            elif status["status"] == "failed":
                print(f"❌ Task failed: {status.get('error', 'Unknown error')}")
                return status
            
            # Exponential backoff: 1s, 2s, 4s, 8s, 16s, then 16s max
            wait_time = min(2 ** attempt, 16)
            print(f"   Attempt {attempt + 1}/{max_attempts}: {status['status']} (waiting {wait_time}s)")
            time.sleep(wait_time)
        
        raise TimeoutError(f"Task {task_id} did not complete within {max_attempts} attempts")
    
    def poll_with_progress_tracking(self, task_id: str, max_attempts: int = 30) -> Dict[str, Any]:
        """
        Poll with progress tracking - shows detailed progress
        """
        print(f"📊 Polling task {task_id} with progress tracking...")
        
        for attempt in range(max_attempts):
            status = self.get_task_status(task_id)
            
            if status["status"] == "completed":
                print(f"✅ Task completed after {attempt + 1} attempts!")
                return status
            elif status["status"] == "failed":
                print(f"❌ Task failed: {status.get('error', 'Unknown error')}")
                return status
            
            # Show progress if available
            if "meta" in status:
                meta = status["meta"]
                if "current" in meta and "total" in meta:
                    progress = (meta["current"] / meta["total"]) * 100
                    print(f"   Progress: {progress:.1f}% ({meta['current']}/{meta['total']})")
                elif "status" in meta:
                    print(f"   Status: {meta['status']}")
            
            # Adaptive wait time based on progress
            if "meta" in status and "current" in status["meta"]:
                current = status["meta"]["current"]
                if current > 50:  # More than halfway done
                    wait_time = 2
                else:
                    wait_time = 5
            else:
                wait_time = 3
            
            print(f"   Attempt {attempt + 1}/{max_attempts}: {status['status']} (waiting {wait_time}s)")
            time.sleep(wait_time)
        
        raise TimeoutError(f"Task {task_id} did not complete within {max_attempts} attempts")
    
    def poll_with_webhook_simulation(self, task_id: str, max_attempts: int = 30) -> Dict[str, Any]:
        """
        Poll with webhook simulation - shows how webhooks would eliminate polling
        """
        print(f"🔔 Polling task {task_id} (simulating webhook pattern)...")
        
        # In a real webhook implementation, you'd register a callback URL
        # and the system would POST to it when the task completes
        # For now, we simulate with polling but show the concept
        
        for attempt in range(max_attempts):
            status = self.get_task_status(task_id)
            
            if status["status"] == "completed":
                print(f"✅ Task completed! (Webhook would have been called)")
                return status
            elif status["status"] == "failed":
                print(f"❌ Task failed! (Webhook would have been called)")
                return status
            
            # Simulate webhook pattern - shorter, more frequent checks
            wait_time = 1
            print(f"   Polling for webhook event... (attempt {attempt + 1})")
            time.sleep(wait_time)
        
        raise TimeoutError(f"Task {task_id} did not complete")

def demonstrate_polling_patterns():
    """Demonstrate different polling patterns"""
    poller = AsyncTaskPoller()
    
    # Test message
    test_message = "I need help with my billing statement. There seems to be an incorrect charge on my account."
    
    print("🚀 Testing Different Polling Patterns")
    print("=" * 50)
    
    # Pattern 1: Exponential Backoff
    print("\n1️⃣ Exponential Backoff Pattern:")
    task_id = poller.submit_task("customer001", test_message)
    try:
        result = poller.poll_with_exponential_backoff(task_id, max_attempts=10)
        print(f"   Result: {result['status']}")
    except TimeoutError as e:
        print(f"   Timeout: {e}")
    
    # Pattern 2: Progress Tracking
    print("\n2️⃣ Progress Tracking Pattern:")
    task_id = poller.submit_task("customer002", test_message)
    try:
        result = poller.poll_with_progress_tracking(task_id, max_attempts=10)
        print(f"   Result: {result['status']}")
    except TimeoutError as e:
        print(f"   Timeout: {e}")
    
    # Pattern 3: Webhook Simulation
    print("\n3️⃣ Webhook Simulation Pattern:")
    task_id = poller.submit_task("customer003", test_message)
    try:
        result = poller.poll_with_webhook_simulation(task_id, max_attempts=10)
        print(f"   Result: {result['status']}")
    except TimeoutError as e:
        print(f"   Timeout: {e}")

if __name__ == "__main__":
    demonstrate_polling_patterns() 
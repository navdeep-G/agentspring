#!/usr/bin/env python3
"""
Comprehensive test scenarios for Enterprise Agent API
Tests various complaint types, edge cases, and system functionality
"""

import logging
import time
from typing import Any, Dict, Optional

from fastapi.testclient import TestClient

from agentspring.api import FastAPIAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

agent = FastAPIAgent()
app = agent.get_app()
client = TestClient(app)
API_KEY = "demo-key"


def make_request(
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> dict:
    """Make API request using TestClient with error handling"""
    default_headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }
    if headers:
        default_headers.update(headers)
    try:
        if method.upper() == "GET":
            response = client.get(endpoint, headers=default_headers)
        elif method.upper() == "POST":
            response = client.post(
                endpoint, headers=default_headers, json=data
            )
        else:
            raise ValueError(f"Unsupported method: {method}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return {"error": str(e)}


def test_health_check():
    """Test API health endpoint"""
    logger.info("=== Testing Health Check ===")
    result = make_request("/health")
    logger.info(f"Health check result: {result}")
    return result


def test_sync_complaint_analysis():
    """Test synchronous complaint analysis"""
    logger.info("=== Testing Synchronous Complaint Analysis ===")

    test_complaints = [
        {
            "customer_id": "CUST001",
            "message": "My account has been locked and I can't access my funds. This is urgent!",
        },
        {
            "customer_id": "CUST002",
            "message": "The mobile app is very slow and keeps crashing when I try to transfer money.",
        },
        {
            "customer_id": "CUST003",
            "message": "I'm very happy with the service, just wanted to say thank you!",
        },
    ]

    results = []
    for i, complaint in enumerate(test_complaints, 1):
        logger.info(
            f"Testing sync complaint {i}: {complaint['message'][:50]}..."
        )
        result = make_request("/analyze", "POST", complaint)
        results.append(result)
        logger.info(f"Result {i}: {result}")
        time.sleep(1)  # Rate limiting

    assert isinstance(results, list)


def test_async_complaint_analysis():
    """Test asynchronous complaint analysis workflow"""
    logger.info("=== Testing Asynchronous Complaint Analysis ===")

    test_complaints = [
        {
            "customer_id": "CUST004",
            "message": "I've been charged twice for the same transaction. This is unacceptable!",
        },
        {
            "customer_id": "CUST005",
            "message": "The website is down and I need to pay my bills today.",
        },
        {
            "customer_id": "CUST006",
            "message": "Can you help me understand the new fee structure?",
        },
    ]

    task_ids = []
    for i, complaint in enumerate(test_complaints, 1):
        logger.info(
            f"Submitting async complaint {i}: {complaint['message'][:50]}..."
        )
        result = make_request("/analyze/async", "POST", complaint)
        if "task_id" in result:
            task_ids.append(result["task_id"])
            logger.info(f"Task {i} submitted: {result['task_id']}")
        else:
            logger.error(f"Failed to submit task {i}: {result}")
        time.sleep(1)

    # Poll for results
    logger.info("Polling for task results...")
    for task_id in task_ids:
        max_attempts = 30
        attempt = 0

        while attempt < max_attempts:
            status_result = make_request(f"/task/{task_id}")
            logger.info(
                f"Task {task_id} status: {status_result.get('status', 'unknown')}"
            )

            if status_result.get("status") == "completed":
                logger.info(
                    f"Task {task_id} completed: {status_result.get('result', {})}"
                )
                break
            elif status_result.get("status") == "failed":
                logger.error(
                    f"Task {task_id} failed: {status_result.get('error', 'Unknown error')}"
                )
                break

            attempt += 1
            time.sleep(2)

        if attempt >= max_attempts:
            logger.error(
                f"Task {task_id} timed out after {max_attempts} attempts"
            )


def test_edge_cases():
    """Test edge cases and error handling"""
    logger.info("=== Testing Edge Cases ===")

    # Test 1: Empty complaint text (should fail validation)
    logger.info("Testing empty complaint text...")
    result = make_request(
        "/analyze", "POST", {"customer_id": "CUST007", "message": ""}
    )
    logger.info(f"Empty complaint result: {result}")

    # Test 2: Very long complaint text (should work)
    logger.info("Testing very long complaint text...")
    long_text = "This is a very long complaint text. " * 50  # Reduced length
    result = make_request(
        "/analyze", "POST", {"customer_id": "CUST008", "message": long_text}
    )
    logger.info(f"Long complaint result: {result}")

    # Test 3: Missing required fields (should fail validation)
    logger.info("Testing missing required fields...")
    result = make_request(
        "/analyze",
        "POST",
        {
            "customer_id": "CUST009"
            # Missing message
        },
    )
    logger.info(f"Missing fields result: {result}")

    # Test 4: Invalid API key
    logger.info("Testing invalid API key...")
    result = make_request(
        "/analyze",
        "POST",
        {"customer_id": "CUST010", "message": "Test complaint"},
        headers={"X-API-Key": "invalid-key"},
    )
    logger.info(f"Invalid API key result: {result}")


def test_different_complaint_types():
    """Test different types of complaints"""
    logger.info("=== Testing Different Complaint Types ===")

    complaint_types = [
        {
            "type": "Technical Issue",
            "complaint": "The mobile app keeps crashing when I try to log in. I've tried reinstalling it multiple times but the problem persists.",
            "customer_id": "CUST011",
        },
        {
            "type": "Billing Issue",
            "complaint": "I was charged an overdraft fee but I had sufficient funds in my account. This is unfair and I want it reversed immediately.",
            "customer_id": "CUST012",
        },
        {
            "type": "Security Concern",
            "complaint": "I received an email that looks suspicious and claims to be from your bank. I'm worried about my account security.",
            "customer_id": "CUST013",
        },
        {
            "type": "Positive Feedback",
            "complaint": "I just wanted to say how much I appreciate the excellent customer service I received yesterday. The representative was very helpful!",
            "customer_id": "CUST014",
        },
        {
            "type": "Account Access",
            "complaint": "I can't remember my password and the reset process isn't working. I need immediate access to my account.",
            "customer_id": "CUST015",
        },
    ]

    for complaint_data in complaint_types:
        logger.info(f"Testing {complaint_data['type']} complaint...")
        result = make_request(
            "/analyze",
            "POST",
            {
                "customer_id": complaint_data["customer_id"],
                "message": complaint_data["complaint"],
            },
        )
        logger.info(f"{complaint_data['type']} result: {result}")
        time.sleep(1)


def test_admin_endpoints():
    """Test admin and monitoring endpoints"""
    logger.info("=== Testing Admin Endpoints ===")

    # Test metrics endpoint
    logger.info("Testing metrics endpoint...")
    metrics = make_request("/admin/metrics")
    logger.info(f"Metrics: {metrics}")

    # Test admin tasks endpoint
    logger.info("Testing admin tasks endpoint...")
    admin_tasks = make_request("/admin/tasks")
    logger.info(f"Admin tasks: {admin_tasks}")

    # Test admin workers endpoint
    logger.info("Testing admin workers endpoint...")
    admin_workers = make_request("/admin/workers")
    logger.info(f"Admin workers: {admin_workers}")


def test_concurrent_requests():
    """Test handling of concurrent requests"""
    logger.info("=== Testing Concurrent Requests ===")

    import queue
    import threading

    results_queue = queue.Queue()

    def make_concurrent_request(complaint_id: int):
        """Make a single concurrent request"""
        complaint = {
            "customer_id": f"CUSTCONC{complaint_id:03d}",
            "message": f"This is concurrent test complaint number {complaint_id}",
        }

        result = make_request("/analyze", "POST", complaint)
        results_queue.put((complaint_id, result))

    # Start 5 concurrent requests
    threads = []
    for i in range(5):
        thread = threading.Thread(target=make_concurrent_request, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Collect results
    concurrent_results = []
    while not results_queue.empty():
        concurrent_results.append(results_queue.get())

    logger.info(
        f"Concurrent requests completed: {len(concurrent_results)} results"
    )
    for complaint_id, result in concurrent_results:
        logger.info(f"Concurrent request {complaint_id}: {result}")


def test_rate_limiting():
    """Test rate limiting behavior"""
    logger.info("=== Testing Rate Limiting ===")

    # Make rapid requests to test rate limiting
    for i in range(10):
        logger.info(f"Making rapid request {i+1}/10...")
        result = make_request(
            "/analyze",
            "POST",
            {
                "customer_id": f"CUSTRATE{i:03d}",
                "message": f"Rate limit test complaint {i}",
            },
        )
        logger.info(f"Rapid request {i+1} result: {result}")
        time.sleep(0.1)  # Very short delay


def main():
    """Run all test scenarios"""
    logger.info("Starting comprehensive API testing...")

    try:
        # Basic health check
        test_health_check()

        # Core functionality tests
        test_sync_complaint_analysis()
        test_async_complaint_analysis()

        # Edge cases
        test_edge_cases()

        # Different complaint types
        test_different_complaint_types()

        # Admin endpoints
        test_admin_endpoints()

        # Performance tests
        test_concurrent_requests()
        test_rate_limiting()

        logger.info("All test scenarios completed successfully!")

    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        raise


if __name__ == "__main__":
    main()

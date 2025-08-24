import socket


def redis_running():
    try:
        sock = socket.create_connection(("localhost", 6379), timeout=2)
        sock.close()
        return True
    except Exception:
        return False


from agentspring.celery_app import celery_app

if __name__ == "__main__":
    result = celery_app.send_task(
        "test_error_task", kwargs={"user": "test-user"}
    )
    print(f"Task submitted: {result.id}")

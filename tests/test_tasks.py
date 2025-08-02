import pytest
from unittest.mock import MagicMock
from agentspring.tasks import AsyncTaskManager, BatchProcessor, agentspring_task, batch_process, TaskResult
from celery import Celery

@pytest.fixture
def celery_app():
    mock = MagicMock(spec=Celery)
    mock.delay = MagicMock()
    return mock

def test_async_task_manager_submit_and_status(celery_app):
    manager = AsyncTaskManager(celery_app)
    mock_task = MagicMock()
    celery_app.AsyncResult.return_value = mock_task
    celery_app.delay.return_value = mock_task
    mock_task.id = "123"
    mock_task.status = "SUCCESS"
    mock_task.ready.return_value = True
    mock_task.result = {"foo": "bar"}
    tid = manager.submit_task(MagicMock(delay=MagicMock(return_value=mock_task)))
    assert tid == "123"
    status = manager.get_task_status("123")
    assert status["status"] == "SUCCESS"

def test_batch_processor_submit_and_sync(celery_app):
    batch_func = MagicMock()
    batch_func.delay.return_value.id = "batchid"
    processor = BatchProcessor(celery_app, batch_func)
    tid = processor.submit_batch([{"foo": 1}])
    assert tid == "batchid"
    results = processor.process_batch_sync([{"foo": 1}], lambda x: x)
    assert results[0]["status"] == "success"

def test_agentspring_task_decorator():
    @agentspring_task(max_retries=2)
    def dummy_task(self, x):
        return {"value": x * 2}
    class DummySelf:
        request = type("req", (), {"id": "abc"})()
        def update_state(self, **kwargs):
            pass
    result = dummy_task(DummySelf(), 3)
    assert result["status"] == "completed"
    assert result["result"] == {"value": 6}

def test_batch_process(celery_app):
    class DummyTask:
        def __init__(self, x):
            self.id = str(x)
    mock_task = MagicMock()
    mock_task.delay = lambda x: DummyTask(x)
    items = [1, 2, 3]
    task_ids = batch_process(celery_app, mock_task, items)
    assert len(task_ids) == 3 

def test_submit_task_error(monkeypatch):
    from agentspring.tasks import AsyncTaskManager
    celery_app = MagicMock()
    manager = AsyncTaskManager(celery_app)
    def fail(*a, **k):
        raise Exception("fail")
    with pytest.raises(Exception):
        manager.submit_task(type("T", (), {"delay": fail})())

def test_get_task_status_error(monkeypatch):
    from agentspring.tasks import AsyncTaskManager
    celery_app = MagicMock()
    celery_app.AsyncResult.side_effect = Exception("fail")
    manager = AsyncTaskManager(celery_app)
    status = manager.get_task_status("badid")
    assert status["status"] == "ERROR"

def test_wait_for_task_timeout(monkeypatch):
    from agentspring.tasks import AsyncTaskManager
    celery_app = MagicMock()
    manager = AsyncTaskManager(celery_app)
    manager.get_task_status = MagicMock(return_value={"status": "PENDING"})
    result = manager.wait_for_task("tid", timeout=0)
    assert result["status"] == "TIMEOUT"

import asyncio
@pytest.mark.asyncio
async def test_wait_for_task_async(monkeypatch):
    from agentspring.tasks import AsyncTaskManager
    celery_app = MagicMock()
    manager = AsyncTaskManager(celery_app)
    manager.get_task_status = MagicMock(return_value={"status": "PENDING"})
    result = await manager.wait_for_task_async("tid", timeout=0)
    assert result["status"] == "TIMEOUT"

@pytest.mark.asyncio
async def test_wait_for_tasks_async(monkeypatch):
    from agentspring.tasks import AsyncTaskManager
    celery_app = MagicMock()
    manager = AsyncTaskManager(celery_app)
    async def fake_wait(task_id, timeout):
        return {"task_id": task_id, "status": "SUCCESS"}
    manager.wait_for_task_async = fake_wait
    results = await manager.wait_for_tasks_async(["a", "b"], timeout=1)
    assert all(r["status"] == "SUCCESS" for r in results)

def test_batch_processor_submit_batch_error(monkeypatch):
    from agentspring.tasks import BatchProcessor
    celery_app = MagicMock()
    def fail(*a, **k):
        raise Exception("fail")
    processor = BatchProcessor(celery_app, type("B", (), {"delay": fail})())
    with pytest.raises(Exception):
        processor.submit_batch([{"foo": 1}])

def test_process_batch_sync_error():
    from agentspring.tasks import BatchProcessor
    celery_app = MagicMock()
    processor = BatchProcessor(celery_app, MagicMock())
    def fail(x):
        raise Exception("fail")
    results = processor.process_batch_sync([{"foo": 1}], fail)
    assert results[0]["status"] == "failed"
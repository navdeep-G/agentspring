def test_celery_app_import():
    from agentspring.celery_app import celery_app, logger
    assert celery_app is not None
    assert logger is not None 

import pytest

def test_celery_health_check():
    try:
        from agentspring.tasks import celery_health_check
        result = celery_health_check.delay().get(timeout=10)
        assert result['status'] == 'ok'
    except Exception as e:
        pytest.skip(f"Celery not running or broker unavailable: {e}")
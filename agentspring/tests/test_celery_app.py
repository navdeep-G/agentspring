def test_celery_app_import():
    from agentspring.celery_app import celery_app, logger
    assert celery_app is not None
    assert logger is not None 
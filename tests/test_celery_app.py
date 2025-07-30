def test_celery_app_import():
    from agentspring.celery_app import celery_app, logger
    assert celery_app is not None
    assert logger is not None 

def test_celery_health_check():
    from agentspring.celery_app import celery_app
    result = celery_app.send_task('celery_health_check')
    output = result.get(timeout=10)
    assert output['status'] == 'ok' 
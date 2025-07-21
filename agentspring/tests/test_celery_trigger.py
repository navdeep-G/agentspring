from agentspring.celery_app import celery_app

if __name__ == '__main__':
    result = celery_app.send_task('test_error_task', kwargs={'user': 'test-user'})
    print(f'Task submitted: {result.id}') 
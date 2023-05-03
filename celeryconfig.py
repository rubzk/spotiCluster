## Broker settings.
broker_url = 'redis://redis:6379/0'

# List of modules to import when the Celery worker starts.
imports = ('myapp.tasks',)

## Using the database to store task state and results.
result_backend = 'db+postgresql://admin:admin@postgres/spoticluster'

task_annotations = {'tasks.add': {'rate_limit': '10/s'}}
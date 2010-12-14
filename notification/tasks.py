from celery.decorators import task

from notification.engine import send_all


@task()
def emit_notices():
    send_all()

from celery.decorators import task

from notification.engine import send_all


@task(ignore_result=True, rate_limit='6/m')
def emit_notices():
    """Don't fire this too often if using multiple celery workers - the send_all
    engine is not safe to use cross-machine, since the lock it uses is on a
    local disk.
    """
    send_all()

from celery.decorators import task

from notification.engine import emit_batch
from notification.models import NoticeQueueBatch


@task(ignore_result=True)
def emit_notice_batch(notice_batch_id, **kwargs):
    batch = NoticeQueueBatch.objects.get(id=notice_batch_id)
    emit_batch(batch)

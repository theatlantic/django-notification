from notification.backends.base import NotificationBackend

class NotificationBackend(object):
    def send(self, notice, messages, context, *args, **kwargs):
        return False

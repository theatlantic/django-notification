from notification.backends.base import NotificationBackend

class FacebookBackend(NotificationBackend):
    slug = u"facebook"
    display_name = u"Facebook"

    def send(self, notice, messages, context, *args, **kwargs):
        pass

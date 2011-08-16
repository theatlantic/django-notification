from notification.backends.base import NotificationBackend
from itertools import chain

class WebBackend(NotificationBackend):
    slug = u'web'
    display_name = u'Web'
    formats = ['short.txt', 'full.txt']

    def send(self, sender, recipient, notice_type, context, on_site=False,
            *args, **kwargs):
        """Always "sends" (i.e. stores to the database), setting on_site
        accordingly.
        """
        # TODO can't do this at the top or we get circular imports
        from notification.models import Notice
        Notice.objects.create(recipient=recipient,
                message=self.format_message(notice_type.label,
                        'notice.html', context),
                notice_type=notice_type,
                on_site=on_site,
                data=dict(chain(*([data.iteritems() for data in context]))),
                sender=sender)
        return True

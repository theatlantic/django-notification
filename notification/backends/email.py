from django.core.mail import send_mail
from django.conf import settings

from notification.backends.base import NotificationBackend

class EmailBackend(NotificationBackend):
    slug = u"email"
    display_name = u"E-mail"

    def should_send(self, notice):
        send = super(EmailBackend, self).should_send(notice)
        return send and notice.recipient.email

    def render_subject(self, context, messages):
        # Strip newlines from subject
        return ''.join(self.render_message('notification/email_subject.txt',
                'short.txt', context, messages).splitlines())

    def send(self, notice, messages, context, *args, **kwargs):
        if not self.should_send(notice):
            return False

        send_mail(self.render_subject(context, messages),
                self.render_message('notification/email_body.txt',
                        'full.txt', context, messages),
                settings.DEFAULT_FROM_EMAIL,
                [notice.recipient.email])
        return True

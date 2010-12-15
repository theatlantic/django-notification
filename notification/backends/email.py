from django.core.mail import send_mail
from django.conf import settings

from notification.backends.base import NotificationBackend

class EmailBackend(NotificationBackend):
    slug = u'email'
    display_name = u'E-mail'
    formats = ['short.txt', 'full.txt']

    def should_send(self, sender, recipient, notice_type, *args, **kwargs):
        send = super(EmailBackend, self).should_send(sender, recipient,
                notice_type)
        return send and recipient.email

    def render_subject(self, label, context):
        # Strip newlines from subject
        return ''.join(self.render_message(label,
                'notification/email_subject.txt', 'short.txt', context
                ).splitlines())

    def send(self, sender, recipient, notice_type, context, *args, **kwargs):
        if not self.should_send(sender, recipient, notice_type):
            return False

        send_mail(self.render_subject(notice_type.label, context),
                self.render_message(notice_type.label,
                        'notification/email_body.txt',
                        'full.txt',
                        context),
                settings.DEFAULT_FROM_EMAIL,
                [recipient.email])
        return True

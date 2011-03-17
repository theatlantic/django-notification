from django.conf import settings
from django.core.mail import EmailMessage

from notification.backends.base import NotificationBackend


class EmailBackend(NotificationBackend):
    slug = u'email'
    display_name = u'E-mail'
    formats = ['short.txt', 'full.txt']

    def email_for_user(self, recipient):
        return recipient.email

    def should_send(self, sender, recipient, notice_type, *args, **kwargs):
        send = super(EmailBackend, self).should_send(sender, recipient,
                notice_type)
        return send and self.email_for_user(recipient) != ''

    def render_subject(self, label, context):
        # Strip newlines from subject
        return ''.join(self.render_message(label,
                'notification/email_subject.txt', 'short.txt', context
                ).splitlines())

    def send(self, sender, recipient, notice_type, context, *args, **kwargs):
        if not self.should_send(sender, recipient, notice_type):
            return False

        headers = kwargs.get('headers', {})
        headers.setdefault('Reply-To', settings.DEFAULT_FROM_EMAIL)

        EmailMessage(self.render_subject(notice_type.label, context),
                self.render_message(notice_type.label,
                        'notification/email_body.txt',
                        'full.txt',
                        context),
                kwargs.get('from_email') or settings.DEFAULT_FROM_EMAIL,
                [self.email_for_user(recipient)],
                headers=headers).send()
        return True

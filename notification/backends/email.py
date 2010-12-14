from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from notification.backends.base import NotificationBackend

class EmailBackend(NotificationBackend):
    slug = u"email"
    display_name = u"E-mail"

    def should_send(self, notice):
        send = super(EmailBackend, self).should_send(notice)
        return send and notice.recipient.email

    def send(self, notice, messages, context, *args, **kwargs):
        if not self.should_send(notice):
            return False

        # Strip newlines from subject
        subject = ''.join(render_to_string('notification/email_subject.txt',
                {'message': messages['short.txt'],}, context).splitlines())
        body = render_to_string('notification/email_body.txt',
                {'message': messages['full.txt'],}, context)
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
                [notice.recipient.email])

        return True

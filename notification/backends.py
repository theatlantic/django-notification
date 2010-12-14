from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

class NoticeMediumBackend(object):
    def send(self, user, messages, context, *args, **kwargs):
        raise NotImplementedError

class EmailBackend(NoticeMediumBackend):
    def send(self, user, messages, context, *args, **kwargs):
        if not user.email:
            return
        # Strip newlines from subject
        subject = ''.join(render_to_string('notification/email_subject.txt',
                {'message': messages['short.txt'],}, context).splitlines())
        body = render_to_string('notification/email_body.txt',
                {'message': messages['full.txt'],}, context)
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])

class FacebookBackend(NoticeMediumBackend):
    def send(self, user, messages, context, *args, **kwargs):
        pass

class NoticeBackends(list):
    EMAIL, FACEBOOK = range(2)

    _mediums = {
        EMAIL: "E-mail",
        FACEBOOK: "Facebook",
    }

    _backends = {
        EMAIL: EmailBackend,
        FACEBOOK: FacebookBackend,
    }

    def __getitem__(self, key):
        return self.backends[key]

    @classmethod
    def mediums(cls):
        return cls._mediums.items()

    @classmethod
    def backends(cls):
        return cls._backends.items()

from django.template import Context
from django.template.loader import render_to_string
from itertools import chain

class NotificationBackend(object):
    slug = None
    display_name = None
    sensitivity = 2
    format_templates = {}

    def path(self):
       return  "%s.%s" % (self.__module__, self.__class__.__name__)

    def get_formats(self):
        return self.formats

    def format_message(self, label, template, context):
        """
        Returns a dictionary with the format identifier as the key. The values are
        are fully rendered templates with the given context.
        """
        # conditionally turn off autoescaping for .txt extensions in format
        if template.endswith(".txt"):
            context.autoescape = False
        else:
            context.autoescape = True
        return render_to_string(
                    ('notification/%s/%s/%s' % (self.slug, label, template),
                    'notification/%s/%s/%s' % (label, self.slug, template),
                    'notification/%s/%s' % (label, template),
                    'notification/%s' % template),
                context_instance=context)
    
    def should_send(self, sender, recipient, notice_type, *args, **kwargs):
        return (recipient.is_active and
                notice_type.get_setting(recipient, self).send)

    def display_name(self):
        raise NotImplementedError

    def send(self, sender, recipient, notice_type, context, *args, **kwargs):
        raise NotImplementedError

    def render_message(self, label, template, format_template, context):
        if 'message' not in context:
            context = Context(
                dict(chain(*([data.iteritems() for data in context])))
            )
            message = self.format_message(label, format_template, context)
            context.update({'message': message})
        return self.format_message(label, template, context)

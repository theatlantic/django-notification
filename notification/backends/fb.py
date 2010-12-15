from django.core.exceptions import ObjectDoesNotExist

from notification.backends.base import NotificationBackend

import facebook

import logging
log = logging.getLogger(__name__)


class FacebookBackend(NotificationBackend):
    def graph_api(self, user):
        """Return an instance of facebook.GraphAPI authorized with the `user`'s
        OAUth token.
        """
        return user.get_profile().facebook_graph_api

    def facebook_user_id(self, user):
        """Return the Facebook OpenGraph ID for the user or None if they do not
        have one in the system."""
        try:
            user_id = unicode(user.get_profile().facebook_auth.identifier)
        except ObjectDoesNotExist:
            user_id = None
        return user_id

    def facebook_token(self, user):
        """Return the Facebook OpenGraph OAuth token for the user or None if
        they do not have one in the system."""
        try:
            token = user.get_profile().facebook_auth.token
        except ObjectDoesNotExist:
            token = None
        return token

    def should_send(self, sender, recipient, notice_type, *args, **kwargs):
        """Return true if the sender has an OAuth token and the recipient has at
        least a Facebook OpenGraph ID.
        """
        send = super(FacebookBackend, self).should_send(sender, recipient, notice_type)
        return (send and self.facebook_token(sender)
                and self.facebook_user_id(recipient))


class FacebookWallPostBackend(FacebookBackend):
    slug = u"facebook_wall_post"
    display_name = u"Facebook Wall Post"

    def send(self, sender, recipient, notice_type, context, *args, **kwargs):
        if not self.should_send(sender, recipient, notice_type):
            return False

        message = self.render_message(notice_type.label,
                'notification/facebook/wall_post.txt', 'notice.html', context)
        try:
            graph = self.graph_api(sender)
            graph.put_wall_post(message,
                    profile_id=self.facebook_user_id(recipient))
        except facebook.GraphAPIError:
            log.exception("Received an error when making a wall post from "
                    "%s to %s" % (sender, recipient))
            return False
        else:
            return True

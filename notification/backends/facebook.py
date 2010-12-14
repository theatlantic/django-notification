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
        """Return the Facebook OpenGraph ID for the user."""
        return unicode(user.get_profile().facebook_auth.identifier)


class FacebookWallPostBackend(FacebookBackend):
    slug = u"facebook_wall_post"
    display_name = u"Facebook Wall Post"

    def send(self, notice, messages, context, *args, **kwargs):
        if not self.should_send(notice):
            return False

        try:
            graph = self.graph_api(notice.sender)
            graph.put_wall_post(message,
                    profile_id=self.facebook_user_id(notice.recipient))
        except facebook.GraphAPIError:
            log.exception("Received an error when making a wall post from "
                    "%s to %s" % (notice.sender, notice.recipient))
            return False
        else:
            return True

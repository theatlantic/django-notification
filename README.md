Django Notification
===================

WTF? (why the fork?)
---------------------

Though this app is really cool for application-wide notifications, I needed it to not only filter by user, but also by *context* (like the group oriented approach of [the fridge](http://www.frid.ge/) ). So this fork adds that: the ability to see context specific notices for a user, where the context is described by a type and an Id: for example, if you have a group context with an id of 1, the notice feed for the current authenticated user would be: `/notices/group/1`.

Also, now it supports notifications via wall posts to the user facebook profile if the `AUTH_PROFILE_MODULE` setting is set and
used like outlined[here](http://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users). 
When posting, the access token of the user must be stored in whatever model instance `user.get_profile()` returns as `facebook_access_token` or the attribute name specified by the `NOTIFICATION_FACEBOOK_ATTR` setting.

What does this fork have that the original didn't?
--------------------------------------------------

* __context specific notifications__ : say you have groups of users or different areas of the site, now you can have specific notifications for the users there (instead of the regular site-wide notifications) if you include the model instance representing the context in a call to `notification.send`, declare the context slug in a `NOTIFICATION_CONTEXTS` setting mapping to the app.model of the context.
* __json feeds__ : now you can use `notification_json_feed_for_user` and `notification_context_json_feed_for_user` to get a JSON containing an array of all the notifications for the logged in user, system-wide and context-specific.
* __automatic notification sending__ : if you add a `AUTO_NOTIFY` setting and map models to callbacks that call the `notification.send` function, `post_save` signals will be declared and connected for you.
* __lazy rendering__ : if you add `NOTIFICATION_LAZY_RENDERING=True` to your `settings` (if not found, defaults to `False`), the context data needed to render a notification will be persisted in the database and used to render the notification everytime you display the notifications page. Note that, if you're one of those guys that like switching django versions like socks, this might break, as it depends on the `pickle` module [and the django guys warn about that](http://docs.djangoproject.com/en/dev/ref/models/querysets/#pickling-querysets).
* __pagination__ : for the notification views, you can set `NOTIFICATIONS_PER_PAGE` to determine how many notifications you'd like to show (it defaults to 20). Remember to iterate over `notices.object_list` in your notification templates instead of just `notices`, because now it's paginated.
* __a separate view for settings__ : now you have a view named `notification_notice_settings` to deal with the user preferences for notifications, instead of having it in the `notification_notices` view.
* __facebook notifications__ : if you have [user profiles](http://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users) in your app and a way of getting and storing facebook access tokens in the users' profiles , notifications will be sent to the users as wall posts to their facebook.

About
-----
Many sites need to notify users when certain events have occurred and to allow
configurable options as to how those notifications are to be received.

The project aims to provide a Django app for this sort of functionality. This
includes:

 * submission of notification messages by other apps
 * notification messages on signing in
 * notification messages via email (configurable by user)
 * notification messages via feed

How to use this fork
----------------------

* Add `'notification'` to your `INSTALLED_APPS` setting
* Add `NOTIFICATION_CONTEXTS` to your `settings.py`, it's value must be a dictionary of the form `{context: app.model}` where `context`refers to the label you will apply to the given context.
* Create the template `notification/context/<label>.html` for each context in the aforementioned dictionary. It will receive the types of notifications you registered and a list of notices already formatted as html as context variables.
* If you'd like automatic reporting when a model is saved, add the setting `AUTO_NOTIFY`, of the form `((path.to.model, path.to.callback), ...)` where each entry is a tuple of models and the functions that should be called when an instance of that model is saved. Here you can pass `send` directly or a function you define that calls `send` to actually create the notices.
* If you want to use the facebook notifications, create notices with a value of `3` for the `default` attribute and **provide a profile** for your users (more about that [in the django user auth documentation](http://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users). Your profile must store the user's access token either in the attribute `facebook_access_token` or in the one set by a `NOTIFICATION_FACEBOOK_ATTR` setting.

After you follow the aforementioned steps, read the next section for the next steps on usage.

Usage
-----
Integrating notification support into your app is a simple three-step process.

  * create your notice types
  * create your notice templates
  * send notifications

###Creating Notice Types###


You need to call `create_notice_type(label, display, description)` once to
create the notice types for your application in the database. `label` is just
the internal shortname that will be used for the type, `display` is what the
user will see as the name of the notification type and `description` is a
short description.

For example:

    notification.create_notice_type("friends_invite", "Invitation Received", "you have received an invitation")

One good way to automatically do this notice type creation is in a
`management.py` file for your app, attached to the syncdb signal.
Here is an example::

    from django.conf import settings
    from django.utils.translation import ugettext_noop as _

    if "notification" in settings.INSTALLED_APPS:
        from notification import models as notification

        def create_notice_types(app, created_models, verbosity, **kwargs):
            notification.create_notice_type("friends_invite", _("Invitation Received"), _("you have received an invitation"))
            notification.create_notice_type("friends_accept", _("Acceptance Received"), _("an invitation you sent has been accepted"))

        signals.post_syncdb.connect(create_notice_types, sender=notification)
    else:
        print "Skipping creation of NoticeTypes as notification app not found"

Notice that the code is wrapped in a conditional clause so if
django-notification is not installed, your app will proceed anyway.

Note that the display and description arguments are marked for translation by
using ugettext_noop. That will enable you to use Django's makemessages
management command and use django-notification's i18n capabilities.

###Notification templates###


There are four different templates that can to be written for the actual content of the notices:

  * `short.txt` is a very short, text-only version of the notice (suitable for things like email subjects)
  * `full.txt` is a longer, text-only version of the notice (suitable for things like email bodies)
  * `notice.html` is a short, html version of the notice, displayed in a user's notice list on the website
  * `full.html` is a long, html version of the notice (not currently used for anything)

Each of these should be put in a directory on the template path called `notification/<notice_type_label>/<template_name>`.
If any of these are missing, a default would be used. In practice, `notice.html` and `full.txt` should be provided at a minimum.

For example, `notification/friends_invite/notice.html` might contain::
    
    {% load i18n %}{% url invitations as invitation_page %}{% url profile_detail username=invitation.from_user.username as user_url %}
    {% blocktrans with invitation.from_user as invitation_from_user %}<a href="{{ user_url }}">{{ invitation_from_user }}</a> has requested to add you as a friend (see <a href="{{ invitation_page }}">invitations</a>){% endblocktrans %}

and `notification/friends_full.txt` might contain::
    
    {% load i18n %}{% url invitations as invitation_page %}{% blocktrans with invitation.from_user as invitation_from_user %}{{ invitation_from_user }} has requested to add you as a friend. You can accept their invitation at:
    
    http://{{ current_site }}{{ invitation_page }}
    {% endblocktrans %}

The context variables are provided when sending the notification.


###Sending Notifications###


There are two different ways of sending out notifications. We have support
for blocking and non-blocking methods of sending notifications. The most
simple way to send out a notification, for example::

    notification.send([to_user], "friends_invite", {"from_user": from_user})

One thing to note is that `send` is a proxy around either `send_now` or
`queue`. They all have the same signature::

    send(users, label, extra_context, on_site)

The parameters are:

 * `users` is an iterable of `User` objects to send the notification to.
 * `label` is the label you used in the previous step to identify the notice
   type.
 * `extra_content` is a dictionary to add custom context entries to the
   template used to render to notification. This is optional.
 * `on_site` is a boolean flag to determine whether an `Notice` object is
   created in the database.

###`send_now` vs. `queue` vs. `send`###


Lets first break down what each does.

####`send_now`####


This is a blocking call that will check each user for elgibility of the
notice and actually peform the send.

####`queue`####


This is a non-blocking call that will queue the call to `send_now` to
be executed at a later time. To later execute the call you need to use
the `emit_notices` management command.

####`send`####

A proxy around `send_now` and `queue`. It gets its behavior from a global
setting named `NOTIFICATION_QUEUE_ALL`. By default it is `False`. This
setting is meant to help control whether you want to queue any call to
`send`.

`send` also accepts `now` and `queue` keyword arguments. By default
each option is set to `False` to honor the global setting which is `False`.
This enables you to override on a per call basis whether it should call
`send_now` or `queue`.

###Displaying notifications###

The urls for this app include `notification_context_notices` and `notification_notices` that correspond to views to show context and site-wide notifications, respectively; both of these return `notice_types` (the list of notice types, so you can use them as javascript filters or something) and `notices`, which is a paginator with the notifications for the current logged in user. An example template using these objects to display the notifications for a user would be:

    {%load i18n humanize%}
    <ul id="notices">
        {%for notice in notices.object_list%}
        <li class="notice {%if notice.is_unseen%}unseen{%endif%} {{notice.notice_type.label}}">
            <div>
                {#the notices already come as html#}
                <p>{{notice|safe}}</p>
                <span>{{notice.added|naturalday}}</span>
            </div>
        </li>
        {%endfor%}
     </ul>
    <div class="pagination">
        <span class="step-links">
            {% if notices.has_previous %}
                <a href="?page={{ notices.previous_page_number }}">{% trans "previous"%}</a>
            {% endif %}

            <span class="current">
            {%if notices.paginator.num_pages%}
                {%blocktrans with notices.number as n and notices.paginator.num_pages as N%}
                    Page {{ n }} of {{ N }}.
                {%endblocktrans%}
            {%endif%}
            </span>

            {% if notices.has_next %}
                <a href="?page={{ notices.next_page_number }}">{%trans "next"%}</a>
            {% endif %}
        </span>
    </div>

####Optional notification support####


In case you want to use django-notification in your reusable app, you can
wrap the import of django-notification in a conditional clause that tests
if it's installed before sending a notice. As a result your app or
project still functions without notification.

For example::

    from django.conf import settings

    if "notification" in settings.INSTALLED_APPS:
        from notification import models as notification
    else:
        notification = None

and then, later:

    if notification:
        notification.send([to_user], "friends_invite", {"from_user": from_user})

Django Notification
===================

WTF? (why the fork?)
---------------------

Though this app is really cool for application-wide notifications, I needed it to not only filter by user, but also by *context* (like the group oriented approach of [the fridge](http://www.frid.ge/) ). So this fork adds that: the ability to see context specific notices for a user, where the context is described by a type and an Id: for example, if you have a group context with an id of 1, the notice feed for the current authenticated user would be: `/notices/group/1`.

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

How to use
----------

* Add `'notification'` to your `INSTALLED_APPS` setting
* ...

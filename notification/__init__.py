VERSION = (0, 2, 0, "a", 1) # following PEP 386
DEV_N = 4
__version__ = '0.2a1.dev4'

from notification.models import create_notice_type, get_notification_language, \
	send_now, send, queue, observe, stop_observing, send_observation_notices_for, \
	is_observing, handle_observations
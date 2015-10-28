import pkg_resources
import sys
from types import ModuleType

VERSION = (0, 2, 0, "a", 1) # following PEP 386
DEV_N = 4
__version__ = '0.2a1.dev4'

# import mapping to objects in other modules
all_by_module = {
    'notification.models': (
        'create_notice_type',
        'get_notification_language',
        'send_now',
        'send',
        'queue',
        'observe',
        'stop_observing',
        'send_observation_notices_for',
        'is_observing',
        'handle_observations',
    )
}

# modules that should be imported when accessed as attributes of notification
attribute_modules = frozenset(['models'])

object_origins = {}
for module, items in all_by_module.items():
    for item in items:
        object_origins[item] = module


class module(ModuleType):

    def __dir__(self):
        """Just show what we want to show."""
        result = list(new_module.__all__)
        result.extend(('__file__', '__path__', '__doc__', '__all__',
                       '__docformat__', '__name__', '__path__',
                       '__package__', '__version__'))
        return result

    def __getattr__(self, name):
        if name in object_origins:
            module = __import__(object_origins[name], None, None, [name])
            for extra_name in all_by_module[module.__name__]:
                setattr(self, extra_name, getattr(module, extra_name))
            return getattr(module, name)
        elif name in attribute_modules:
            __import__('notification.' + name)
        return ModuleType.__getattribute__(self, name)


# keep a reference to this module so that it's not garbage collected
old_module = sys.modules[__name__]

# setup the new module and patch it into the dict of loaded modules
new_module = sys.modules[__name__] = module(__name__)
new_module.__dict__.update({
    '__file__':         __file__,
    '__package__':      'notification',
    '__path__':         __path__,
    '__doc__':          __doc__,
    '__version__':      __version__,
    '__all__':          tuple(object_origins) + tuple(attribute_modules),
    '__docformat__':    'restructuredtext en'
})

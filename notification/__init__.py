from django.utils import importlib
from django.core.exceptions import ImproperlyConfigured

VERSION = (0, 2, 0, "a", 1) # following PEP 386
DEV_N = 4

def get_version():
    version = "%s.%s" % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = "%s.%s" % (version, VERSION[2])
    if VERSION[3] != "f":
        version = "%s%s%s" % (version, VERSION[3], VERSION[4])
        if DEV_N:
            version = "%s.dev%s" % (version, DEV_N)
    return version

__version__ = get_version()

# Name for use in settings file --> name of module in "backends" directory.
# Any backend scheme that is not in this dictionary is treated as a Python
# import path to a custom backend.
BACKENDS = {
    'email': 'email.EmailBackend',
    'facebook': 'fb.FacebookWallPostBackend',
    'dummy': 'dummy.DummyBackend',
}

DEFAULT_BACKEND = 'email'

def load_backend(backend):
    if backend in BACKENDS:
        path = 'notification.backends.%s' % BACKENDS[backend]
    else:
        path = backend

    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = importlib.import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing notification backend %s: "%s"' % (module, e))
    except ValueError, e:
        raise ImproperlyConfigured('Error importing notification backends. Is NOTIFICATION_BACKENDS a correctly defined list or tuple?')
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" notification backend' % (module, attr))

    return cls()

def get_backends():
    from django.conf import settings
    backends = []
    for backend in getattr(settings, 'NOTIFICATION_BACKENDS', []):
        backends.append(load_backend(backend))
    if not backends:
        backends.append(load_backend(DEFAULT_BACKEND))
    return backends

backends = get_backends()

def get_backend_field_choices():
    choices = []
    for backend in backends:
        name = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        choices.append((name, backend.display_name))
    return choices

backend_field_choices = get_backend_field_choices()

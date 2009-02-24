__all__ = ('backend', 'SearchableModel', 'SearchableManager')

from cgi import parse_qsl
from django.conf import settings
from django.core import signals
from fts.backends.base import InvalidFtsBackendError

# Name for use in settings file --> name of module in "backends" directory.
# Any backend scheme that is not in this dictionary is treated as a Python
# import path to a custom backend.
BACKENDS = {
    'pgsql': 'pgsql',
    'mysql': 'mysql',
    'sphinx': 'sphinx',
    'xapian': 'xapian',
    'simple': 'simple',
    'dummy': 'dummy',
}

def get_fts(backend_uri):
    if backend_uri.find(':') == -1:
        raise InvalidFtsBackendError, "Backend URI must start with scheme://"
    scheme, rest = backend_uri.split(':', 1)
    if not rest.startswith('//'):
        raise InvalidFtsBackendError, "Backend URI must start with scheme://"

    host = rest[2:]
    qpos = rest.find('?')
    if qpos != -1:
        params = dict(parse_qsl(rest[qpos+1:]))
        host = rest[2:qpos]
    else:
        params = {}
    if host.endswith('/'):
        host = host[:-1]

    if scheme in BACKENDS:
        module = __import__('fts.backends.%s' % BACKENDS[scheme], {}, {}, [''])
    else:
        module = __import__(scheme, {}, {}, [''])
    return getattr(module, 'SearchClass')(host, params), getattr(module, 'SearchableModel'), getattr(module, 'SearchManager')

_fts, SearchableModel, SearchManager = get_fts(settings.FTS_BACKEND)
backend = _fts.backend

from django.conf import settings

__version__ = '0.2.0'

try:
    from ._version import __version__
except ImportError:
    pass

VERSION = __version__.split('+')
VERSION = tuple(list(map(int, VERSION[0].split('.'))) + VERSION[1:])

USE_TRANSLATABLE_FIELDS = (
    getattr(settings, 'CONTENT_PLUGINS_USE_TRANSLATABLE_FIELDS', False) or
    getattr(settings, 'USE_TRANSLATABLE_FIELDS', False)
)


# TODO Implement translatable AutoSlugField: USE_TRANSLATABLE_SLUG_FIELDS = getattr(settings, 'CONTENT_USE_TRANSLATABLE_SLUG_FIELDS', True)

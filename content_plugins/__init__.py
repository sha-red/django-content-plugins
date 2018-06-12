from django.conf import settings


try:
    from ._version import __version__
except ImportError:
    __version__ = '0.0.0'

VERSION = __version__.partition('+')
VERSION = tuple(list(map(int, VERSION[0].split('.'))) + [VERSION[2]])


USE_TRANSLATABLE_FIELDS = (
    getattr(settings, 'CONTENT_PLUGINS_USE_TRANSLATABLE_FIELDS', False) or
    getattr(settings, 'USE_TRANSLATABLE_FIELDS', False)
)


# TODO Implement translatable AutoSlugField: USE_TRANSLATABLE_SLUG_FIELDS = getattr(settings, 'CONTENT_USE_TRANSLATABLE_SLUG_FIELDS', True)

from django.conf import settings


VERSION = (0, 2, 0)
__version__ = '.'.join(map(str, VERSION))


USE_TRANSLATABLE_FIELDS = (
    getattr(settings, 'CONTENT_PLUGINS_USE_TRANSLATABLE_FIELDS', False) or
    getattr(settings, 'USE_TRANSLATABLE_FIELDS', False)
)


# TODO Implement translatable AutoSlugField: USE_TRANSLATABLE_SLUG_FIELDS = getattr(settings, 'CONTENT_USE_TRANSLATABLE_SLUG_FIELDS', True)

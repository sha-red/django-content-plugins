from django.conf import settings


VERSION = (0, 2, 0)
__version__ = '.'.join(map(str, VERSION))


USE_TRANSLATABLE_FIELDS = getattr(settings, 'CONTENT_USE_TRANSLATABLE_FIELDS', True)

# TODO Implement translatable AutoSlugField: USE_TRANSLATABLE_SLUG_FIELDS = getattr(settings, 'CONTENT_USE_TRANSLATABLE_SLUG_FIELDS', True)

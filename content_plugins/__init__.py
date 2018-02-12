from django.conf import settings


USE_TRANSLATABLE_FIELDS = getattr(settings, 'CONTENT_USE_TRANSLATABLE_FIELDS', True)

# TODO Implement translatable AutoSlugField: USE_TRANSLATABLE_SLUG_FIELDS = getattr(settings, 'CONTENT_USE_TRANSLATABLE_SLUG_FIELDS', True)

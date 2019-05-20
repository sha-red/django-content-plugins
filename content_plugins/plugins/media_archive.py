"""
Plugins for use with django-shared-mediarchive.
"""

from django.apps import registry
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

try:
    from imagekit.admin import AdminThumbnail
    USE_ADMIN_THUMBNAIL = True
except ImportError:
    USE_ADMIN_THUMBNAIL = False

from ..admin import ContentInlineBase
from ..base import ObjectPluginBase


image_model = getattr(settings, 'CONTENTPLUGINS_IMAGE_MODEL', None)
download_model = getattr(settings, 'CONTENTPLUGINS_DOWNLOAD_MODEL', None)

if image_model:
    image_model = registry.apps.get_model(image_model)
else:
    from shared.media_archive.models import Image
    image_model = Image

if download_model:
    download_model = registry.apps.get_model(download_model)
else:
    from shared.media_archive.models import Download
    download_model = Download


#
# Media Plugins

def image_thumbnail(obj):
    return obj.image.thumbnail


class ImageBase(ObjectPluginBase):
    image = models.ForeignKey(Image, on_delete=models.CASCADE,
        verbose_name=_("image"))

    fk_fieldname = 'image'

    class Meta:
        abstract = True
        verbose_name = _("image")
        verbose_name_plural = _("images")

    def get_type_slug(self):
        return ''

    class AdminInline(ContentInlineBase):
        if USE_ADMIN_THUMBNAIL:
            admin_thumbnail = AdminThumbnail(
                image_field=image_thumbnail,
                template='imagekit/admin/selectable_thumbnail.html')
            admin_thumbnail.short_description = _("image")

        def get_is_public_display(self, obj):
            if not obj.image.is_public:
                return _("not published/visible")
            else:
                return _("published")
        get_is_public_display.short_description = _("published")

        def get_readonly_fields(self, request, obj=None):
            readonly_fields = list(super().get_readonly_fields(request, obj))
            if USE_ADMIN_THUMBNAIL:
                readonly_fields += ['admin_thumbnail']
            readonly_fields += ['get_is_public_display']
            return readonly_fields

    admin_inline_baseclass = AdminInline


class DownloadBase(ObjectPluginBase):
    download = models.ForeignKey(Download, on_delete=models.CASCADE,
        verbose_name=_("download"))

    fk_fieldname = 'download'

    class Meta:
        abstract = True
        verbose_name = _("download")
        verbose_name_plural = _("downloads")

    def get_type_slug(self):
        return ''

    class AdminInline(ContentInlineBase):
        def get_is_public_display(self, obj):
            if not obj.download.is_public:
                return _("not published/visible")
            else:
                return _("published")
        get_is_public_display.short_description = _("published")

        def get_readonly_fields(self, request, obj=None):
            readonly_fields = list(super().get_readonly_fields(request, obj))
            readonly_fields += ['get_is_public_display']
            return readonly_fields

    admin_inline_baseclass = AdminInline

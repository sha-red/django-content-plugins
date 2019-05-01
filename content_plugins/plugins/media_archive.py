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
        fields = ContentInlineBase.fields or []
        if USE_ADMIN_THUMBNAIL:
            fields = fields + ['admin_thumbnail']
            admin_thumbnail = AdminThumbnail(
                image_field=image_thumbnail,
                template='imagekit/admin/selectable_thumbnail.html')
            admin_thumbnail.short_description = _("image")
        fields = fields + [
            'image',
            'get_is_public_display',
        ]
        readonly_fields = ContentInlineBase.fields or [] + [
            'admin_thumbnail',
            'get_is_public_display',
        ]

        def get_is_public_display(self, obj):
            if not obj.image.is_public:
                return _("not published/visible")
            else:
                return _("published")
        get_is_public_display.short_description = _("published")

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
        fields = ContentInlineBase.fields or [] + [
            'download',
            'get_is_public_display',
        ]
        readonly_fields = ContentInlineBase.readonly_fields or [] + [
            'get_is_public_display',
        ]

        def get_is_public_display(self, obj):
            if not obj.download.is_public:
                return _("not published/visible")
            else:
                return _("published")
        get_is_public_display.short_description = _("published")

    admin_inline_baseclass = AdminInline

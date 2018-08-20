"""
Abstract base classes and mixins.
"""

from django import forms
from django.conf import settings

from ckeditor_uploader.widgets import CKEditorUploadingWidget
from content_editor.admin import ContentEditorInline


class ContentInlineBase(ContentEditorInline):
    """
    Empty definition for later use.

    Subclass who override the fields attribute must includes
    the 'region' and 'ordering' fields:

    class AdminInline(ContentInlineBase):
        fields = ['region', 'ordering', ... more fields ...]
    """


# TODO Use feincms3.plugins.richtext.RichText/RichTextInline instead

if getattr(settings, 'CKEDITOR_UPLOADS', False):
    base_classes = [CKEditorUploadingWidget]
else:
    base_classes = [forms.Textarea]


class RichTextarea(*base_classes):
    def __init__(self, attrs=None):
        # Provide class so that the code in plugin_ckeditor.js knows
        # which text areas should be enhanced with a rich text
        # control:
        default_attrs = {'class': 'richtext'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class RichTextInlineBase(ContentInlineBase):
    formfield_overrides = {
        'richtext': {'widget': RichTextarea},
    }

    class Media:
        js = (
            # '//cdn.ckeditor.com/4.5.6/standard/ckeditor.js',
            'feincms3/plugin_ckeditor.js',
        )

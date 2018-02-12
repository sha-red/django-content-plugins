# Erik Stein <code@classlibrary.net>, 2017
"""
Abstract base classes and mixins.
"""

from django import forms

from content_editor.admin import ContentEditorInline


class ContentInlineBase(ContentEditorInline):
    """
    Empty definition for later use.
    """


class RichTextarea(forms.Textarea):
    def __init__(self, attrs=None):
        # Provide class so that the code in plugin_ckeditor.js knows
        # which text areas should be enhanced with a rich text
        # control:
        default_attrs = {'class': 'richtext'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class RichTextInlineBase(ContentInlineBase):
    # Subclasses: Add your model, like model = models.RichTextArticlePlugin

    formfield_overrides = {
        'richtext_en': {'widget': RichTextarea},
    }

    regions = []

    class Media:
        js = (
            # '//cdn.ckeditor.com/4.5.6/standard/ckeditor.js',
            'js/plugin_ckeditor.js',
        )

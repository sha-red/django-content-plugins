"""
Abstract models for common content editor plugins.


admin.py
--------

ContentInlineBase
    RichTextInlineBase

RichTextarea



fields.py
---------

TranslatableCleansedRichTextField



plugins.py
----------

BasePlugin
    StringRendererPlugin
        RichTextBase
    SectionBase
    ImageBase
    DownloadBase
    FootnoteBase

StyleMixin
RichTextFootnoteMixin


renderer.py
-----------

PluginRenderer

@register_with_renderer



"""

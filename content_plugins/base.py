import re
from django.db import models
from django.template import Template
from django.utils.html import format_html, mark_safe
from django.utils.translation import ugettext_lazy as _

from feincms3.cleanse import CleansedRichTextField
from shared.utils.fields import AutoSlugField

from .admin import ContentInlineBase, RichTextInlineBase

from .plugins.mixins import StyleMixin
from . import USE_TRANSLATABLE_FIELDS


if USE_TRANSLATABLE_FIELDS:
    from shared.multilingual.utils.fields import TranslatableCharField
    from .fields import TranslatableCleansedRichTextField


"""
TODO Class hierarchy should be
    BasePlugin
        StringRendererPlugin
        TemplateRendererPlugin
            FilesystemRendererPlugin (is specific for RomArchive)
"""


class BasePlugin(models.Model):
    class Meta:
        abstract = True
        verbose_name = _("plugin")
        verbose_name_plural = _("plugins")

    def __str__(self):
        return "{} ({})".format(self._meta.verbose_name, self.pk)

    @classmethod
    def admin_inline(cls, base_class=ContentInlineBase):
        class Inline(base_class):
            model = cls
            regions = cls.regions
        return Inline

    @classmethod
    def register_with_renderer(cls, renderer):
        renderer.register_template_renderer(cls, cls.get_template, cls.get_context_data)

    def get_template_names(self):
        return getattr(self, 'template_name', None)

    def get_template(self):
        """
        Might return a single template name, a list of template names
        or an instance with a "render" method (i.e. a Template instance).

        Default implementation is to return the result of self.get_template_names().

        See rendering logic in feincms3.TemplateRendererPlugin.
        """
        return self.get_template_names()

    def get_context_data(self, request_context, **kwargs):
        context = kwargs.get('context', {})
        context['content'] = self
        context['parent'] = self.parent
        context['request'] = getattr(request_context, 'request', None)
        return context

    # For rendering the template's render() method is used


class StringRendererPlugin(BasePlugin):
    class Meta:
        abstract = True

    @classmethod
    def register_with_renderer(cls, renderer):
        renderer.register_template_renderer(cls, None, cls.render)

    def render(self):
        raise NotImplementedError


class FilesystemTemplateRendererPlugin(BasePlugin):
    template_name = None
    path_prefix = 'plugins/'  # TODO Rename to 'template_name_prefix'

    class Meta:
        abstract = True

    def get_path_prefix(self):
        return self.path_prefix

    def prefixed_path(self, path):
        return "{}{}".format(self.get_path_prefix(), path)

    def get_template_names(self):
        # Per default look first for absolute template_name path and
        # template_name path prefixed with path_prefix.
        if getattr(self, 'template_name', False):
            template_names = [
                self.template_name,
                self.prefixed_path(self.template_name)
            ]
        else:
            template_names = []

        template_names.extend(super().get_template_names() or [])

        return template_names + [
            "{path_prefix}_default.html".format(
                path_prefix=self.get_path_prefix())
        ]


class RichTextBase(StyleMixin, FilesystemTemplateRendererPlugin):
    if USE_TRANSLATABLE_FIELDS:
        richtext = TranslatableCleansedRichTextField(_("text"), blank=True)
    else:
        richtext = CleansedRichTextField(_("text"), blank=True)

    path_prefix = FilesystemTemplateRendererPlugin.path_prefix + 'richtext/'

    class Meta:
        abstract = True
        verbose_name = _("text")
        verbose_name_plural = _("texts")

    @classmethod
    def admin_inline(cls, base_class=None):
        return super().admin_inline(base_class=RichTextInlineBase)


class SectionBase(StyleMixin, BasePlugin):
    if USE_TRANSLATABLE_FIELDS:
        subheading = TranslatableCharField(_("subheading"), max_length=500)
    else:
        subheading = models.CharField(_("subheading"), max_length=500)
    slug = AutoSlugField(_("slug"), max_length=200, blank=True, populate_from='subheading', unique_slug=False)

    class Meta:
        abstract = True
        verbose_name = _("section")
        verbose_name_plural = _("section")

    def get_template(self):
        return Template("""
        </section>

        <section id="{{ slug }}">
            <h2>{{ subheading }}</h2>
        """)

    def get_context_data(self, request_context, **kwargs):
        context = super().get_context_data(request_context, **kwargs)
        context['slug'] = self.slug
        context['subheading'] = self.subheading
        return context


# class ImageBase(StyleMixin, BasePlugin):
#     image = models.ForeignKey(Image, on_delete=models.PROTECT)
#     alt_caption = TranslatableCharField(_("caption"), max_length=500, null=True, blank=True, help_text=_("Optional, used instead of the caption of the image object."))#

#     class Meta:
#         abstract = True
#         verbose_name = _("image")
#         verbose_name_plural = _("images")#

#     def render(self):
#         template = """
#         <figure class="image">
#             <img src="{src}">#

#             <figcaption>
#                 {caption_text}
#             </figcaption>
#         </figure>
#         """
#         # TOOD Assemble caption from image's captions if empty
#         return mark_safe(template.format(
#             src=self.image.figure_image.url,
#             caption_text=mark_safe(self.alt_caption or "")
#         ))


class DownloadBase(StyleMixin, BasePlugin):
    file = models.FileField(upload_to='downloads/%Y/%m/')

    class Meta:
        abstract = True
        verbose_name = _("download")
        verbose_name_plural = _("downloads")

    def render(self):
        template = """
        <a href="{url}">{name}</a>
        """
        return mark_safe(template.format(
            url=self.file.url,
            name=self.file.name,
        ))


class FootnoteBase(BasePlugin):
    # TODO Validators: index might only contain alphanumeric characters
    index = models.CharField(_("footnote index"), max_length=10)
    if USE_TRANSLATABLE_FIELDS:
        richtext = TranslatableCleansedRichTextField(_("footnote text"))
    else:
        richtext = CleansedRichTextField(_("footnote text"))

    html_tag = '<li>'

    class Meta:
        abstract = True
        verbose_name = _("footnote")
        verbose_name_plural = _("footnote")

    # TODO Convert to Template
    def render(self, html_tag=None):
        template = """
        {opening_tag}
            <a id="fn{number}" class="footnote-index" href="#back{number}">{number}</a>
            <div class="text">{text}</div>
        {closing_tag}
        """
        context = {
            'number': self.index,
            'text': mark_safe(self.richtext or ""),
            'opening_tag': "",
            'closing_tag': "",
        }
        html_tag = html_tag or self.html_tag
        if html_tag:
            context['opening_tag'] = html_tag
            context['closing_tag'] = '{0}/{1}'.format(html_tag[:1], html_tag[1:])
        return mark_safe(template.format(**context))


# FIXME Currently doesn't do anything
class RichTextFootnoteMixin:
    MATCH_FOOTNOTES = re.compile("<sup>(\w+)</sup>")

    def render(self):
        # Find all footnotes and convert them into links
        rv = self.MATCH_FOOTNOTES.subn(
            '<sup id=\"back\g<1>\" class="footnote"><a href=\"#fn\g<1>\">\g<1></a></sup>',
            self.richtext)[0]
        return mark_safe(rv)
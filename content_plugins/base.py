import re
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.template import Template
from django.utils.html import mark_safe, strip_tags
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from feincms3.cleanse import CleansedRichTextField
from shared.utils.fields import AutoSlugField

# TODO Rename ContentInlineBase to PluginInlineBase
from .admin import ContentInlineBase, RichTextInlineBase

from .plugins.mixins import StyleMixin
from . import USE_TRANSLATABLE_FIELDS


if USE_TRANSLATABLE_FIELDS:
    from shared.multilingual.utils.fields import TranslatableCharField
    from .fields import TranslatableCleansedRichTextField


# TODO Rename to PluginBase
class BasePlugin(models.Model):
    admin_inline_baseclass = ContentInlineBase

    class Meta:
        abstract = True
        verbose_name = _("plugin")
        verbose_name_plural = _("plugins")

    def __str__(self):
        return "{} ({})".format(self._meta.verbose_name, self.pk)

    @classmethod
    def admin_inline(cls, base_class=None):
        # TODO Cache inline
        class Inline(base_class or cls.admin_inline_baseclass):
            model = cls
            regions = cls.regions
        return Inline

    def get_plugin_context(self, context=None, **kwargs):
        """
        Returns a dict.
        """
        plugin_context = {}
        plugin_context['content'] = self
        plugin_context['parent'] = self.parent
        if 'request_context' in kwargs:
            plugin_context['request'] = getattr(kwargs['request_context'], 'request', None)
        return plugin_context


class StringRendererPlugin(BasePlugin):
    class Meta:
        abstract = True

    @classmethod
    def register_with_renderer(cls, renderer):
        renderer.register_string_renderer(cls, cls.render)

    def render(self):
        raise NotImplementedError("render method must be implemented by subclass")


class TemplateRendererPlugin(BasePlugin):
    class Meta:
        abstract = True

    @classmethod
    def register_with_renderer(cls, renderer):
        renderer.register_template_renderer(cls, cls.get_template, cls.get_plugin_context)

    def get_template_names(self):
        t = getattr(self, 'template_name', None)
        if t:
            return [t]
        else:
            return []

    def get_template(self):
        """
        Might return a single template name, a list of template names
        or an instance with a "render" method (i.e. a Template instance).

        Default implementation is to return the result of self.get_template_names().

        See rendering logic in feincms3.TemplateRendererPlugin.
        """
        return self.get_template_names()

    # For rendering the template's render() method is used


class FilesystemTemplateRendererPlugin(TemplateRendererPlugin):
    # template_name_prefix
    template_name = None

    class Meta:
        abstract = True

    def get_template_name_prefix(self):
        return getattr(self, 'template_name_prefix', '')

    def prefixed_path(self, path):
        return "{}{}".format(self.get_template_name_prefix(), path)

    def get_template_names(self):
        """
        Look first for template_name,
        second for prefixed template_name,
        then super's template names,
        finally prefixed _default.html.
        """
        if self.template_name is None:
            raise ImproperlyConfigured(
                "FilesystemTemplateRendererPlugin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:
            return [
                self.prefixed_path(self.template_name),
            ]


class RichTextBase(StyleMixin, FilesystemTemplateRendererPlugin):
    if USE_TRANSLATABLE_FIELDS:
        richtext = TranslatableCleansedRichTextField(_("text"), blank=True)
    else:
        richtext = CleansedRichTextField(_("text"), blank=True)

    admin_inline_baseclass = RichTextInlineBase
    template_name = '_richtext.html'

    class Meta:
        abstract = True
        verbose_name = _("text")
        verbose_name_plural = _("texts")

    def __str__(self):
        return Truncator(strip_tags(self.richtext)).words(10, truncate=" ...")


# TODO Rename to SectionBreakBase
class SectionBase(StyleMixin, FilesystemTemplateRendererPlugin):
    if USE_TRANSLATABLE_FIELDS:
        subheading = TranslatableCharField(_("subheading"), null=True, blank=True, max_length=500)
    else:
        subheading = models.CharField(_("subheading"), null=True, blank=True, max_length=500)
    slug = AutoSlugField(_("slug"), max_length=200, blank=True, populate_from='subheading', unique_slug=False)

    template_name = '_sectionbreak.html'

    class Meta:
        abstract = True
        verbose_name = _("section")
        verbose_name_plural = _("section")

    def __str__(self):
        return Truncator(strip_tags(self.subheading)).words(10, truncate=" ...")

    def get_plugin_context(self, context=None, **kwargs):
        context = super().get_plugin_context(context=None, **kwargs)
        context['slug'] = self.slug
        context['subheading'] = self.subheading
        return context


# ImageBase can't live here because image managment is different from project to project
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


# TODO See comments on ImageBase; remove DownloadBase
class DownloadBase(StyleMixin, StringRendererPlugin):
    file = models.FileField(upload_to='downloads/%Y/%m/')

    class Meta:
        abstract = True
        verbose_name = _("download")
        verbose_name_plural = _("downloads")

    def __str__(self):
        return getattr(self.file, 'name', "")

    def render(self):
        template = """
        <a href="{url}">{name}</a>
        """
        return mark_safe(template.format(
            url=self.file.url,
            name=self.file.name,
        ))


class FootnoteBase(StringRendererPlugin):
    # TODO Validators: index might only contain alphanumeric characters
    index = models.CharField(_("footnote index"), max_length=10)
    if USE_TRANSLATABLE_FIELDS:
        richtext = TranslatableCleansedRichTextField(_("footnote text"), null=True, blank=True)
    else:
        richtext = CleansedRichTextField(_("footnote text"), null=True, blank=True)

    html_tag = '<li>'

    class Meta:
        abstract = True
        verbose_name = _("footnote")
        verbose_name_plural = _("footnote")

    def __str__(self):
        return "[{}] {}".format(
            self.index,
            Truncator(strip_tags(self.richtext)).words(10, truncate=" ...")
        )

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

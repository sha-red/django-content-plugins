import os
import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.html import mark_safe, strip_tags
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from feincms3.cleanse import CleansedRichTextField
from shared.utils.models.slugs import DowngradingSlugField

# TODO Rename ContentInlineBase to PluginInlineBase
from .admin import ContentInlineBase, RichTextInlineBase

from .plugins.mixins import StyleMixin
from . import USE_TRANSLATABLE_FIELDS


if USE_TRANSLATABLE_FIELDS:
    from shared.multilingual.utils.fields import TranslatableCharField
    from .fields import TranslatableCleansedRichTextField


class BasePlugin(models.Model):
    admin_inline_baseclass = ContentInlineBase

    class Meta:
        abstract = True
        verbose_name = _("plugin")
        verbose_name_plural = _("plugins")

    @classmethod
    def register_with_renderer(cls, renderer):
        pass

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
    # Don't define template_name_prefix here, so that a sibling class takes precedence
    # template_name_prefix = ''
    # template_name = ''

    class Meta:
        abstract = True

    def get_template_name_prefix(self):
        return getattr(self, 'template_name_prefix', '')

    def prefixed_path(self, path):
        # TODO Use posixpath
        return "{}{}".format(self.get_template_name_prefix(), path)

    def get_template_names(self):
        """
        Look first for template_name,
        second for prefixed template_name,
        then super's template names,
        finally prefixed _default.html.
        """
        if not getattr(self, 'template_name', False):
            raise ImproperlyConfigured(
                "FilesystemTemplateRendererPlugin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:
            return [
                self.prefixed_path(self.template_name),
            ]


class PrepareRichtextMixin:
    @property
    def prepared_richtext(self):
        return mark_safe(self.get_prepared_richtext(self.richtext))

    def get_prepared_richtext(self, richtext):
        return richtext


class RichTextBase(PrepareRichtextMixin, FilesystemTemplateRendererPlugin):
    if USE_TRANSLATABLE_FIELDS:
        richtext = TranslatableCleansedRichTextField(_("text"), blank=True)
    else:
        richtext = CleansedRichTextField(_("text"), blank=True)

    admin_inline_baseclass = RichTextInlineBase
    template_name = 'plugins/_richtext.html'

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
    slug = DowngradingSlugField(_("slug"), max_length=200, blank=True, populate_from='subheading', unique_slug=False)

    template_name = 'plugins/_sectionbreak.html'

    class Meta:
        abstract = True
        verbose_name = _("section")
        verbose_name_plural = _("section")

    def __str__(self):
        return Truncator(strip_tags(self.subheading)).words(10, truncate=" ...")

    # FIXME Not need, members are accessible through {{ content.slug }} etc.
    def get_plugin_context(self, context=None, **kwargs):
        context = super().get_plugin_context(context=context, **kwargs)
        context['slug'] = self.slug
        context['subheading'] = self.subheading
        return context


class ObjectPluginBase(FilesystemTemplateRendererPlugin):
    fk_fieldname = None
    regions = None

    class Meta:
        abstract = True

    def __str__(self):
        return str(getattr(self, self.fk_fieldname, ""))

    @property
    def object(self):
        assert self.fk_fieldname, "fk_fieldname not set."
        return getattr(self, self.fk_fieldname)

    def get_type_slug(self):
        type = getattr(self.object, 'type', None)
        if type:
            return getattr(type, 'internal_slug', "")
        return ""

    def get_template_names(self):
        """"
        _<fk_fieldname>_<object.type>/_<style>.html
        _<fk_fieldname>_<object.type>.html
        _<fk_fieldname>/_<style>.html
        _<fk_fieldname>.html
        """
        assert self.fk_fieldname, "fk_fieldname not set."

        template_names = []
        type_slug = self.get_type_slug()

        if getattr(self, 'template_name', False):
            base_template_name = os.path.splitext(self.template_name)[0]
        else:
            base_template_name = "plugins/_{}".format(self.fk_fieldname)

        if type_slug:
            template_names.append(self.prefixed_path(
                "{}_{}.html".format(
                    base_template_name, type_slug
                )
            ))
        template_names.append(
            self.prefixed_path("{}.html".format(base_template_name)))
        return template_names

    @classmethod
    def admin_inline(cls):
        assert cls.fk_fieldname, "fk_fieldname not set."

        inline = super().admin_inline()
        if not inline.raw_id_fields:
            inline.raw_id_fields = []
        inline.raw_id_fields += [cls.fk_fieldname]
        return inline


class SimpleImageBase(StringRendererPlugin):
    image = models.ImageField(_("image"), upload_to='images/%Y/%m/')
    caption = TranslatableCharField(_("caption"), max_length=500,
        null=True, blank=True,
        help_text=_("Optional, used instead of the caption of the image object."))

    class Meta:
        abstract = True
        verbose_name = _("image")
        verbose_name_plural = _("images")

    def __str__(self):
        return getattr(self.image, 'name', "")

    def render(self):
        template = """
        <figure class="image">
            <img src="{src}">

            <figcaption>
                {caption_text}
            </figcaption>
        </figure>
        """

        return mark_safe(template.format(
            src=self.image.url,
            caption_text=mark_safe(self.caption or "")
        ))


class SimpleDownloadBase(StringRendererPlugin):
    file = models.FileField(upload_to='downloads/%Y/%m/')

    class Meta:
        abstract = True
        verbose_name = _("download")
        verbose_name_plural = _("downloads")

    def __str__(self):
        return getattr(self.file, 'name', "")

    def render(self):
        template = """
        <a href="{url}" download="{name}">{name}</a>
        """
        return mark_safe(template.format(
            url=self.file.url,
            name=self.file.name,
        ))


class FootnoteBase(PrepareRichtextMixin, FilesystemTemplateRendererPlugin):
    # TODO Validators: index must only contain alphanumeric characters
    index = models.CharField(_("footnote index"), max_length=10)
    if USE_TRANSLATABLE_FIELDS:
        richtext = TranslatableCleansedRichTextField(_("footnote text"), null=True, blank=True)
    else:
        richtext = CleansedRichTextField(_("footnote text"), null=True, blank=True)

    html_tag = getattr(settings, 'FOOTNOTE_TAG', 'div')
    template_name = 'plugins/_footnote.html'

    class Meta:
        abstract = True
        verbose_name = _("footnote")
        verbose_name_plural = _("footnote")

    def __str__(self):
        return "[{}] {}".format(
            self.index,
            Truncator(strip_tags(self.richtext)).words(10, truncate=" ...")
        )


class RichTextFootnoteMixin:
    OO_FOOTNOTES = re.compile("<a.*?>(<sup>(.*?)</sup>)</a>")
    MATCH_FOOTNOTES = re.compile("<sup>(\w+)</sup>")

    def get_prepared_richtext(self, richtext):
        # Find all footnotes and convert them into links
        richtext = super().get_prepared_richtext(richtext)
        richtext = self.OO_FOOTNOTES.subn('\g<1>', richtext)[0]
        rv = self.MATCH_FOOTNOTES.subn(
            '<sup id=\"back\g<1>\" class="footnote"><a href=\"#fn\g<1>\">\g<1></a></sup>',
            richtext)[0]
        return rv

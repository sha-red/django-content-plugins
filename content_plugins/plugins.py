# TODO Always use Django templates for rendering, replace .format() class

import os
import re
from django.conf import settings
from django.db import models
from django.template import Template
from django.utils.html import format_html, mark_safe
from django.utils.translation import ugettext_lazy as _

from feincms3.cleanse import CleansedRichTextField
from shared.utils.fields import AutoSlugField
from shared.multilingual.utils.fields import TranslatableCharField, TranslatableTextField

from .admin import ContentInlineBase, RichTextInlineBase
from .fields import TranslatableCleansedRichTextField

# FIXME Implement USE_TRANSLATABLE_FIELDS
from .mixins import USE_TRANSLATABLE_FIELDS


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
        verbose_name = _("Element")
        verbose_name_plural = _("Elements")

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
        """
        return self.get_template_names()

    def get_context_data(self, request_context, **kwargs):
        context = kwargs.get('context', {})
        context['parent'] = self.parent
        context['request'] = request_context['request']
        context['content'] = self
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


class StyleField(models.CharField):
    # Allow overriding of STYLE_CHOICES constant in subclasses

    def contribute_to_class(self, cls, name, **kwargs):
        if hasattr(cls, 'STYLE_CHOICES'):
            self.choices = cls.STYLE_CHOICES
        super().contribute_to_class(cls, name, **kwargs)


class StyleMixin(models.Model):
    STYLE_CHOICES = (
        ('default', _("default")),
    )
    style = StyleField(_("style"), max_length=50, null=True, blank=True)

    class Meta:
        abstract = True

    def get_style_slug(self):
        return getattr(self, 'style', None) or 'default'


class FilesystemTemplateRendererPlugin(BasePlugin):
    # TODO Join FilesystemTemplateRendererPlugin code with BaseObjectElement code

    template_name = None
    path_prefix = None  # Potential values: "richtext", "image"

    class Meta:
        abstract = True

    def get_path_prefix(self):
        if self.path_prefix:
            return "{}{}".format(self.path_prefix, os.path.sep)
        else:
            return ""

    def get_template_names(self):
        # TODO Style related logic should be part of the StyleMixin: maybe get_template_names should call super()
        if hasattr(self, 'style'):
            template_names = [
                "curatorialcontent/elements/{path_prefix}style/_{style}.html".format(
                    path_prefix=self.get_path_prefix(), style=self.get_style_slug()),
            ]
        else:
            template_names = []

        return template_names + [
            "curatorialcontent/elements/{path_prefix}_default.html".format(
                path_prefix=self.get_path_prefix())
        ] + ([self.template_name] if getattr(self, 'template_name', None) else [])


class RichTextBase(StyleMixin, FilesystemTemplateRendererPlugin):
    richtext = TranslatableCleansedRichTextField(_("text"), blank=True)

    path_prefix = 'richtext'

    class Meta:
        abstract = True
        verbose_name = _("text")
        verbose_name_plural = _("texts")

    @classmethod
    def admin_inline(cls, base_class=None):
        return super().admin_inline(base_class=RichTextInlineBase)


class SectionBase(StyleMixin, BasePlugin):
    subheading = TranslatableCharField(_("subheading"), max_length=500)
    slug = AutoSlugField(_("slug"), max_length=200, blank=True, populate_from='subheading', unique_slug=False)

    class Meta:
        abstract = True
        verbose_name = _("Abschnittswechsel")
        verbose_name_plural = _("Abschnittswechsel")

    def get_template(self):
        return Template("""
            </div>
        </section>

        <section id="{{ slug }}">
            <h2>{{ heading }}</h2>

            <div class="text">
        """)

    def get_context_data(self, request_context, **kwargs):
        context = super().get_context_data(request_context, **kwargs)
        context['slug'] = self.slug
        context['heading'] = self.heading
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
    richtext = TranslatableCleansedRichTextField(_("footnote text"))

    html_tag = '<li>'

    class Meta:
        abstract = True
        verbose_name = _("footnote")
        verbose_name_plural = _("footnote")

    def render(self, html_tag=None):
        template = """
        {opening_tag}
            <div class="text">
                <a id="fn{number}" class="footnote-index" href="#back{number}">{number}</a>
                {text}
            </div>
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


class RichTextFootnoteMixin:
    MATCH_FOOTNOTES = re.compile("<sup>(\w+)</sup>")

    def render(self):
        # Find all footnotes and convert them into links
        rv = self.MATCH_FOOTNOTES.subn(
            '<sup id=\"back\g<1>\" class="footnote"><a href=\"#fn\g<1>\">\g<1></a></sup>',
            self.richtext)[0]
        return mark_safe(rv)

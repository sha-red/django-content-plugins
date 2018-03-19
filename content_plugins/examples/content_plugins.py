"""
Example instantiation of the abstract plugin base classes
"""

"""
from django.db import models
from django.utils.translation import ugettext_lazy as _

from content_editor.models import create_plugin_base
from shared.utils.text import slugify_long
from shared.multilingual.utils.fields import TranslatableCharField

from ..collection.models import ItemBundle, Event, Collection
from ..content.admin import RichTextInlineBase
from ..content import plugins
from ..content.renderer import ContentPluginRenderer
from ..media.models import (
    MediaImage,
    MediaAudio,
    MediaVideo,
    MediaDocument,
)
from ..people.models import Person
from ..thesaurus.models import Term
from .models import Page


ContentPluginBase = create_plugin_base(Page)


renderer = ContentPluginRenderer()


@renderer.register()
class RichTextContentPlugin(plugins.RichTextFootnoteMixin, plugins.RichTextBase, ContentPluginBase):
    regions = ['main', 'aside', 'intro']


@renderer.register()
class BlockquoteContentPlugin(plugins.RichTextFootnoteMixin, plugins.RichTextBase, ContentPluginBase):
    STYLE_CHOICES = plugins.StyleMixin.STYLE_CHOICES + (
        ('blockquote', _("Blockquote")),
        ('pullquote', _("Pull Quote")),
        ('introquote', _("Introductory Quote")),
    )

    template_name_prefix = 'quote'

    regions = ['main', 'intro']

    class Meta:
        verbose_name = _("quote")
        verbose_name_plural = _("quotes")


@renderer.register()
class SectionContentPlugin(plugins.SectionBase, ContentPluginBase):
    regions = ['main', 'aside']


# @renderer.register()
# class ImageContentPlugin(plugins.ImageBase, ContentPluginBase):
#     regions = ['main', 'aside']


# @renderer.register()
# class DownloadContentPlugin(plugins.DownloadBase, ContentPluginBase):
#     regions = ['main', 'aside']


@renderer.register()
class FootnoteContentPlugin(plugins.FootnoteBase, ContentPluginBase):
    regions = ['references', 'footnotes']


class BaseObjectElement(plugins.BasePlugin, ContentPluginBase):
    STYLE_CHOICES = plugins.StyleMixin.STYLE_CHOICES + (
        ('minimal', _("Minimal View")),
        ('extensive', _("Extensive View")),
    )

    class Meta:
        abstract = True
        verbose_name = _("object view")
        verbose_name_plural = _("objects view")

    fk_fieldname = None
    regions = ['main', 'aside']

    @property
    def object(self):
        assert self.fk_fieldname, "fk_fieldname not set."
        return getattr(self, self.fk_fieldname)

    def type_slug(self):
        slug = ''
        type = getattr(self.object, 'type', None)
        if type:
            slug = getattr(type, 'internal_slug', '')
        return slug

    def get_template_names(self):
        assert self.fk_fieldname, "fk_fieldname not set."

        type_slug = self.type_slug()
        style_slug = getattr(self, 'style', None) or 'default'

        # Append a potentially defined self.template_name
        return [
            "curatorialcontent/elements/{path_prefix}/pk/_{pk}.html".format(
                path_prefix=self.fk_fieldname, pk=self.object.pk),
            "curatorialcontent/elements/{path_prefix}/type/_{style}/_{type}.html".format(
                path_prefix=self.fk_fieldname, style=style_slug, type=type_slug),
            "curatorialcontent/elements/{path_prefix}/style/_{style}.html".format(
                path_prefix=self.fk_fieldname, style=style_slug),
            "curatorialcontent/elements/{path_prefix}/type/_{type}.html".format(
                path_prefix=self.fk_fieldname, type=type_slug),
            "curatorialcontent/elements/{path_prefix}/_default.html".format(
                path_prefix=self.fk_fieldname)
        ] + ([self.template_name] if hasattr(self, 'template_name') else [])

    @classmethod
    def admin_inline(cls, base_class=None):
        assert cls.fk_fieldname, "fk_fieldname not set."
        inline = super().admin_inline(base_class=RichTextInlineBase)  # TODO Do we need RichTextInlineBase here?
        if not inline.raw_id_fields:
            inline.raw_id_fields = []
        inline.raw_id_fields += [cls.fk_fieldname]
        return inline


@renderer.register()
class ItemBundleElement(BaseObjectElement, plugins.StyleMixin):
    STYLE_CHOICES = BaseObjectElement.STYLE_CHOICES + (
        ('teaser', _("Big Top Teaser")),
    )

    itembundle = models.ForeignKey(ItemBundle, verbose_name=_("ItemBundle"))

    fk_fieldname = 'itembundle'
    regions = ['main', 'aside']

    class Meta:
        verbose_name = _("item bundle view")
        verbose_name_plural = _("item bundle views")


@renderer.register()
class PersonElement(BaseObjectElement, plugins.StyleMixin):
    person = models.ForeignKey(Person, verbose_name=_("Person"))

    fk_fieldname = 'person'
    regions = ['main', 'aside']

    class Meta:
        verbose_name = _("person view")
        verbose_name_plural = _("person views")


@renderer.register()
class ContributorElement(BaseObjectElement):
    person = models.ForeignKey(Person, verbose_name=_("Person"))
    CONTRIBUTOR_ROLE_CHOICES = (
        ('author', _("Author")),
        ('contributor', _("Contributor")),
    )
    role = models.CharField(_("role"), max_length=50,
        choices=CONTRIBUTOR_ROLE_CHOICES,
        default=CONTRIBUTOR_ROLE_CHOICES[0][0], null=False, blank=False)

    fk_fieldname = 'person'
    regions = ['contributors']

    class Meta:
        verbose_name = _("contributor")
        verbose_name_plural = _("contributors")


@renderer.register()
class TermElement(BaseObjectElement, plugins.StyleMixin):
    term = models.ForeignKey(Term, verbose_name=_("Term"))

    fk_fieldname = 'term'
    regions = ['main', 'aside']

    class Meta:
        verbose_name = _("term view")
        verbose_name_plural = _("term views")


@renderer.register()
class EventElement(BaseObjectElement, plugins.StyleMixin):
    event = models.ForeignKey(Event, verbose_name=_("Event"))

    fk_fieldname = 'event'
    regions = ['main', 'aside']

    class Meta:
        verbose_name = _("event view")
        verbose_name_plural = _("event views")


@renderer.register()
class SubcollectionElement(BaseObjectElement, plugins.StyleMixin):
    STYLE_CHOICES = BaseObjectElement.STYLE_CHOICES + (
        ('index-nav', _("Index Page Navigation")),
    )

    collection = models.ForeignKey(Collection, verbose_name=_("Subcollection"))

    fk_fieldname = 'collection'
    regions = ['main', 'aside']

    class Meta:
        verbose_name = _("collection view")
        verbose_name_plural = _("collection views")


@renderer.register()
class MediaImageElement(BaseObjectElement):
    image = models.ForeignKey(MediaImage, verbose_name=_("Image"))
    caption = TranslatableCharField(_("caption"), max_length=500, null=True, blank=True, help_text=_("image caption"))

    fk_fieldname = 'image'
    regions = ['main', 'aside']

    class Meta:
        verbose_name = _("image")
        verbose_name_plural = _("images")

    def type_slug(self):
        return ''


@renderer.register()
class MediaAudioElement(BaseObjectElement):
    audio = models.ForeignKey(MediaAudio, verbose_name=_("Audio"))
    caption = TranslatableCharField(_("caption"), max_length=500, null=True, blank=True, help_text=_("audio caption"))

    fk_fieldname = 'audio'
    regions = ['main', 'aside']

    class Meta:
        verbose_name = _("audio")
        verbose_name_plural = _("audio")


@renderer.register()
class MediaVideoElement(BaseObjectElement):
    video = models.ForeignKey(MediaVideo, verbose_name=_("Video"))
    caption = TranslatableCharField(_("caption"), max_length=500, null=True, blank=True, help_text=_("video caption"))

    fk_fieldname = 'video'
    regions = ['main', 'aside']

    class Meta:
        verbose_name = _("video")
        verbose_name_plural = _("video")


@renderer.register()
class MediaDocumentElement(BaseObjectElement):
    document = models.ForeignKey(MediaDocument, verbose_name=_("Document"))
    caption = TranslatableCharField(_("caption"), max_length=500, null=True, blank=True, help_text=_("document caption"))

    fk_fieldname = 'document'
    regions = ['main', 'aside']

    class Meta:
        verbose_name = _("document")
        verbose_name_plural = _("document")


@renderer.register()
class SubsectionsElement(plugins.StyleMixin, plugins.FilesystemTemplateRendererPlugin, ContentPluginBase):
    regions = ['main', 'aside']

    template_name_prefix = 'subsections_nav'

    class Meta:
        verbose_name = _("subsections navigation element")
        verbose_name_plural = _("subsections navigation elements")


@renderer.register()
class TeamElement(plugins.StyleMixin, plugins.FilesystemTemplateRendererPlugin, ContentPluginBase):
    regions = ['main', 'aside']

    template_name_prefix = 'team'

    class Meta:
        verbose_name = _("team navigation element")
        verbose_name_plural = _("team navigation elements")


@renderer.register()
class ActorsElement(plugins.StyleMixin, plugins.FilesystemTemplateRendererPlugin, ContentPluginBase):
    regions = ['main', 'aside']

    template_name_prefix = 'actors'

    class Meta:
        verbose_name = _("actors navigation element")
        verbose_name_plural = _("actors navigation elements")


@renderer.register()
class ArticlesElement(plugins.StyleMixin, plugins.FilesystemTemplateRendererPlugin, ContentPluginBase):
    regions = ['main', 'aside']

    template_name_prefix = 'articles_nav'

    class Meta:
        verbose_name = _("articles navigation element")
        verbose_name_plural = _("articles navigation elements")


#
# Slideshow Elements

class BaseSlideshowContentPlugin(plugins.StyleMixin, plugins.FilesystemTemplateRendererPlugin, ContentPluginBase):
    STYLE_CHOICES = (
        ('black', _("black background")),
        ('yellow', _("yellow background")),
        ('white', _("white background")),
    )

    caption = plugins.TranslatableCleansedRichTextField(_("caption"), blank=True)

    template_name_prefix = 'slide'

    regions = ['slides']

    class Meta:
        abstract = True

    @classmethod
    def admin_inline(cls, base_class=None):
        return super().admin_inline(base_class=RichTextInlineBase)


@renderer.register()
class TextSlideshowContentPlugin(BaseSlideshowContentPlugin):
    template_name_prefix = 'slide/text/'

    regions = ['slides']

    class Meta:
        verbose_name = _("text slide")
        verbose_name_plural = _("text slides")


@renderer.register()
class ItembundleSlideshowContentPlugin(BaseSlideshowContentPlugin):
    itembundle = models.ForeignKey(ItemBundle, verbose_name=_("ItemBundle"))

    template_name_prefix = 'slide/itembundle/'

    regions = ['slides']

    class Meta:
        verbose_name = _("item bundle slide")
        verbose_name_plural = _("item bundle slides")

    @classmethod
    def admin_inline(cls, base_class=None):
        inline = super().admin_inline(base_class=RichTextInlineBase)
        if not inline.raw_id_fields:
            inline.raw_id_fields = []
        inline.raw_id_fields += ['itembundle']
        return inline

"""
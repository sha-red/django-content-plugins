import os

from django.db import models
from django.utils.translation import ugettext_lazy as _

from shared.utils.text import slugify


class StyleField(models.CharField):
    """
    Allows overriding of STYLE_CHOICES in subclasses.
    """

    def contribute_to_class(self, cls, name, **kwargs):
        if hasattr(cls, 'STYLE_CHOICES'):
            self.choices = cls.STYLE_CHOICES
        super().contribute_to_class(cls, name, **kwargs)


class StyleMixin(models.Model):
    STYLE_CHOICES = tuple()
    style = StyleField(_("style"), max_length=50, null=True, blank=True)

    class Meta:
        abstract = True

    class AdminMixin:
        def get_fields(self, request, obj=None):
            fields = super().get_fields(request, obj)
            if 'style' not in fields:
                fields.append('style')
            return fields

    @classmethod
    def admin_inline(cls):
        class MixedClass(super().admin_inline(), cls.AdminMixin):
            pass

        return MixedClass

    def get_style_slug(self):
        style = getattr(self, 'style', None) or 'default'
        return slugify(style).replace("_", "-")

    def add_styled_template_names(self, template_names):
        """
        if super().get_template_names():
            [
                "article/_richtext.html",
                "_richtext.html",
            ]
        then add_styled_template_names returns
            [
                "article/_richtext/_<style>.html",
                "article/_richtext.html",
                "_richtext/_<style>.html",
                "_richtext.html",
            ]
        """
        extended_template_names = []
        for template in template_names:
            name, ext = os.path.splitext(template)
            extended_template_names += [
                "{name}/_{style}{ext}".format(
                    name=name, style=self.style, ext=ext),
                template
            ]
        return extended_template_names

    def get_template_names(self):
        if hasattr(super(), 'get_template_names'):
            template_names = super().get_template_names()
            if self.style:
                template_names = self.add_styled_template_names(template_names)
            return template_names
        else:
            return []

    def get_plugin_context(self, context=None, **kwargs):
        if hasattr(super(), 'get_plugin_context'):
            context = super().get_plugin_context(**kwargs)
        else:
            context = {}
        context['style'] = self.get_style_slug()
        return context

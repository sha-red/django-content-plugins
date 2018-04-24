from django.db import models
from django.utils.translation import ugettext_lazy as _


class StyleMixin(models.Model):
    class StyleField(models.CharField):
        """
        Allows overriding of STYLE_CHOICES in subclasses.
        """

        def contribute_to_class(self, cls, name, **kwargs):
            if hasattr(cls, 'STYLE_CHOICES'):
                self.choices = cls.STYLE_CHOICES
            super().contribute_to_class(cls, name, **kwargs)

    STYLE_CHOICES = (
        ('default', _("default")),
    )

    style = StyleField(_("style"), max_length=50, null=True, blank=True)

    class Meta:
        abstract = True

    def get_style_slug(self):
        return getattr(self, 'style', None) or 'default'

    # Compatibiliy with super classes not having a prefixed_path method
    def prefixed_path(self, path):
        if hasattr(super(), 'prefixed_path'):
            return super().prefixed_path(path)
        else:
            return path

    def get_template_names(self):
        if hasattr(super(), 'get_template_names'):
            template_names = super().get_template_names()
        else:
            template_names = []

        return template_names + [
            self.prefixed_path(
                "style/_{style}.html".format(
                    style=self.get_style_slug()),
            )
        ]

    def get_context_data(self, context=None, **kwargs):
        if hasattr(super(), 'get_context_data'):
            context = super().get_context_data(context=context, **kwargs)
        else:
            context = context or {}
        context['style'] = self.get_style_slug()
        return context

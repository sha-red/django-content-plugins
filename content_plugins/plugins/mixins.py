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

    def get_template_names(self):
        # Should only be called by classes using filesystem templates
        template_names = super().get_template_names() or []
        template_names.extend([
            "{path_prefix}style/_{style}.html".format(
                path_prefix=self.get_path_prefix(),
                style=self.get_style_slug()),
        ])
        return template_names



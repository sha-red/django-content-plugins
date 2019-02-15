from feincms3.cleanse import CleansedRichTextField

from . import USE_TRANSLATABLE_FIELDS


if USE_TRANSLATABLE_FIELDS:
    from shared.multilingual.utils.fields import TranslatableFieldMixin

    class TranslatableCleansedRichTextField(TranslatableFieldMixin, CleansedRichTextField):
        base_class = CleansedRichTextField
        extra_parameter_names = ['config_name', 'extra_plugins', 'external_plugin_resources']

else:
    TranslatableCleansedRichTextField = CleansedRichTextField

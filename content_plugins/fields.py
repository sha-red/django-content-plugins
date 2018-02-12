from feincms3.cleanse import CleansedRichTextField
from shared.multilingual.utils.fields import TranslatableFieldMixin


class TranslatableCleansedRichTextField(TranslatableFieldMixin, CleansedRichTextField):
    base_class = CleansedRichTextField
    extra_parameter_names = ['config_name', 'extra_plugins', 'external_plugin_resources']
    # TODO Implement translatable rich text widget

from django import template
from django.template import loader
from django.apps import registry


register = template.Library()


@register.filter
def region_contents(regions, region_key):
    return regions._contents[region_key]


@register.filter
def filter_plugins(region_contents, model):
    """
    Usage:

    {{ regions|region_conents:"article"|filter_plugins:"projects.ContributorProjectPlugin" }}

    """
    if type(model) == str:
        model = registry.apps.get_model(model)

    return [plugin.object
        for plugin in region_contents
        if type(plugin) == model]


@register.filter
def select_template(template_list):
    return loader.select_template(template_list)

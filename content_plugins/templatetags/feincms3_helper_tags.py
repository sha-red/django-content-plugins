# TODO This file should be part of feincms3

from collections import defaultdict

from django import template
from django.apps import registry
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q


register = template.Library()


MENUMIXIN_MODELS = getattr(settings, 'MENUMIXIN_MODELS', {})


@register.simple_tag
def menus():
    menus = defaultdict(list)

    def add_menus_from_model(model, depth_from=1, depth_to=1, q_filters=None):
        if not q_filters:
            q_filters = []
        try:
            model._meta.get_field('level')
            # MPTT Model
            pages = model.objects.filter(
                ~Q(menu=''),
                *q_filters,
            ).extra(
                where=['level BETWEEN %s AND %s'],
                params=[depth_from, depth_to],
            )
        except FieldDoesNotExist:
            # FeinCMS3 Model
            pages = model.objects.with_tree_fields().filter(
                ~Q(menu=''),
                *q_filters,
            ).extra(
                where=['tree_depth BETWEEN %s AND %s'],
                params=[depth_from, depth_to],
            )
        for page in pages:
            menus[page.menu].append(page)

    for k, v in MENUMIXIN_MODELS.items():
        add_menus_from_model(
            registry.apps.get_model(k),
            v[0], v[1], v[2])

    return menus


@register.filter
def group_by_tree(iterable):
    """
    Given a list of pages in tree order, generate pairs consisting of the
    parents and their descendants in a list.
    """

    parent = None
    children = []
    depth = -1

    for element in iterable:
        if parent is None or element.depth == depth:
            if parent:
                yield parent, children
                parent = None
                children = []

            parent = element
            depth = element.depth
        else:
            children.append(element)

    if parent:
        yield parent, children

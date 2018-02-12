from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from content_editor.contents import contents_for_item
from shared.utils.text import html_entities_to_unicode
from shared.utils.translation import get_language_order


def render_page_as_text(page, renderer, template, language):
    request = HttpRequest()
    request.user = AnonymousUser()
    contents = contents_for_item(page, renderer.plugins())
    context = {
        'contents': contents,
        'language': language,
        'page': page,
        'renderer': renderer,
    }
    html = render_to_string(template, context, request=request)
    text = html_entities_to_unicode(strip_tags(html)).strip()
    return text

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from content_editor.contents import contents_for_item
from shared.utils.text import html_entities_to_unicode


def render_page_as_text(page, template, context_data):
    request = HttpRequest()
    request.user = AnonymousUser()
    html = render_to_string(template, context_data, request=request)
    text = html_entities_to_unicode(strip_tags(html)).strip()
    return text

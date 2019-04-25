import re
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from shared.utils.text import html_entities_to_unicode


def render_page_as_html(page, template, context_data, css_selector=None):
    request = HttpRequest()
    request.user = AnonymousUser()
    assert template, "No template supplied"
    html = render_to_string(template, context_data, request=request)

    if css_selector:
        import lxml.html
        doc = lxml.html.fromstring(html)
        for element in doc.cssselect('script,style'):
            element.getparent().remove(element)
        html = []
        for part in doc.cssselect(css_selector):
            html.append(lxml.html.tostring(part).decode().strip())
        html = '\n'.join(html)
    return html


def render_page_as_text(page, template, context_data, css_selector=None):
    html = render_page_as_html(page, template, context_data, css_selector)
    text = html_entities_to_unicode(strip_tags(html)).strip()
    text = re.sub('[\t ]+', ' ', text)
    text = re.sub(re.compile('\n +', re.DOTALL), '\n', text)
    text = re.sub(re.compile('\n+', re.DOTALL), '\n', text)
    content = []
    for word in text.split(' '):
        if len(word) <= 245:
            content += [word]
    return ' '.join(content)

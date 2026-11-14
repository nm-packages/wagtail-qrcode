from django import template
from django.utils.safestring import mark_safe

from wagtail_qrcode.cls import WagtailQrCode

register = template.Library()


@register.simple_tag
def qr_code_svg(page):
    """Render trusted generated SVG; the renderer escapes the page's title."""
    if not page.pk:
        return ""
    return mark_safe(WagtailQrCode(page).render("svg").decode())

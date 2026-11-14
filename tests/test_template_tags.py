from django.template import Context, Template
from django.test import TestCase
from wagtail.models import Page

from tests.testapp.models import QRCodePage
from wagtail_qrcode.models import QRCode


class TestTemplateTags(TestCase):
    def test_public_svg_is_generated_and_escapes_title(self):
        page = Page.objects.get(pk=2).add_child(
            instance=QRCodePage(title="<script>bad</script>")
        )
        html = Template("{% load wagtail_qrcode_tags %}{% qr_code_svg page %}").render(
            Context({"page": page})
        )
        self.assertIn("<svg", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertFalse(QRCode.objects.exists())

    def test_unsaved_page_has_no_svg(self):
        html = Template("{% load wagtail_qrcode_tags %}{% qr_code_svg page %}").render(
            Context({"page": QRCodePage()})
        )
        self.assertEqual(html, "")

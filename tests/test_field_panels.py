from django.test import TestCase
from django.urls import reverse
from wagtail.admin.panels import ObjectList
from wagtail.models import Page

from tests.testapp.models import QRCodePage
from wagtail_qrcode.models import QRCode


class TestFieldPanels(TestCase):
    def render_panel(self, page):
        handler = ObjectList(page.qrcode_panels).bind_to_model(QRCodePage)
        form = handler.get_form_class()(instance=page)
        panel = handler.get_bound_panel(instance=page, form=form)
        return panel.render_html(), form

    def test_unsaved_page(self):
        html, _ = self.render_panel(QRCodePage())
        self.assertIn("Save the page", html)
        self.assertNotIn("<img", html)
        self.assertFalse(QRCode.objects.exists())

    def test_panel_is_read_only_with_preview_downloads_and_count(self):
        page = Page.objects.get(pk=2).add_child(instance=QRCodePage(title="QR page"))
        QRCode.objects.create(page=page, usage_count=42)
        html, form = self.render_panel(page)
        self.assertIn(reverse("wagtail_qrcode_admin:preview", args=[page.pk]), html)
        for file_format in ("svg", "eps"):
            self.assertIn(
                reverse("wagtail_qrcode_admin:download", args=[page.pk, file_format]),
                html,
            )
        self.assertIn("42 scans", html)
        for field in ("qr_code_svg", "qr_code_eps", "qr_code_usage"):
            self.assertNotIn(field, form.fields)
            self.assertNotIn(f'name="{field}"', html)
        self.assertIn('name="email_address"', html)

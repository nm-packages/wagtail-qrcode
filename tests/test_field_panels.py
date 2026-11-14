from django import forms
from django.test import TestCase
from wagtail.admin.panels import ObjectList

from tests.testapp.models import QRCodePage
from wagtail_qrcode.field_panels import QrCodeFieldPanel, QrCodeUsageFieldPanel


class TestFieldPanels(TestCase):
    def test_qr_code_svg_field_panel(self):
        fp = QrCodeFieldPanel("foo", widget=forms.TextInput, classname="full")
        fp.field_name = "foo"

    def test_qr_code_svg_usage_field_panel(self):
        fp = QrCodeUsageFieldPanel("bar", widget=forms.TextInput, classname="full")
        fp.field_name = "bar"

    def test_qr_code_panels_render_in_page_editor(self):
        page = QRCodePage(
            title="QR code preview",
            qr_code_svg='<svg xmlns="http://www.w3.org/2000/svg"><title>QR preview</title></svg>',
            qr_code_usage=42,
        )
        edit_handler = ObjectList(page.qrcode_panels).bind_to_model(QRCodePage)
        form = edit_handler.get_form_class()(instance=page)
        panel = edit_handler.get_bound_panel(instance=page, form=form)

        html = panel.render_html()

        self.assertIn(page.qr_code_svg, html)
        self.assertIn('<h3 style="font-size:300%">42</h3>', html)
        for field in ("qr_code_svg", "qr_code_usage", "qr_code_eps", "email_address"):
            self.assertIn('name="{}"'.format(field), html)

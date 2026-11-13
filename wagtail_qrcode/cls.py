import io
from xml.sax.saxutils import escape

import pyqrcode
from django.conf import settings
from django.urls import reverse


class WagtailQrCode:
    """Render a page's QR code without writing files or database records."""

    def __init__(self, page):
        self.page = page
        self.settings = {
            "scale": 3,
            "quiet_zone": 6,
            "svg_has_xml_declaration": False,
            **getattr(settings, "WAGTAIL_QR_CODE", {}),
        }

    def encoded_url(self):
        if not self.page.pk:
            raise ValueError("Save the page before generating its QR code.")
        base_url = getattr(settings, "WAGTAIL_QR_CODE_BASE_URL", None)
        if base_url is None:
            base_url = settings.WAGTAILADMIN_BASE_URL
        return f"{base_url.rstrip('/')}{reverse('qr_code_page_view')}?id={self.page.pk}"

    def make_qr_code(self, content):
        return pyqrcode.create(content)

    def make_svg(self, qrc):
        output = io.BytesIO()
        qrc.svg(
            output,
            scale=self.settings["scale"],
            quiet_zone=self.settings["quiet_zone"],
            xmldecl=self.settings["svg_has_xml_declaration"],
            svgns=True,
            title=escape(self.page.title),
        )
        return output.getvalue().decode()

    def make_eps(self, qrc):
        output = io.StringIO()
        qrc.eps(
            output,
            scale=self.settings["scale"],
            quiet_zone=self.settings["quiet_zone"],
        )
        return output.getvalue().encode()

    def render(self, file_format):
        """Return SVG or EPS bytes for a preview, download or email attachment."""
        if file_format not in ("svg", "eps"):
            raise ValueError("Unsupported QR code format.")
        qrc = self.make_qr_code(self.encoded_url())
        if file_format == "svg":
            return self.make_svg(qrc).encode()
        return self.make_eps(qrc)

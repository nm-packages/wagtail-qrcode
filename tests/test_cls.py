import tempfile
from pathlib import Path
from xml.etree import ElementTree

from django.test import TestCase, override_settings
from wagtail.documents import get_document_model
from wagtail.models import Page

from tests.testapp.models import QRCodePage
from tests.utils import eps_without_timestamp
from wagtail_qrcode.cls import WagtailQrCode
from wagtail_qrcode.models import QRCode


class TestWagtailQrCode(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page = Page.objects.get(pk=2).add_child(
            instance=QRCodePage(title="QR page")
        )

    def test_rendering_writes_no_files_or_records(self):
        with (
            tempfile.TemporaryDirectory() as media,
            override_settings(MEDIA_ROOT=media),
        ):
            renderer = WagtailQrCode(self.page)
            with self.assertNumQueries(0):
                svg = renderer.render("svg")
                eps = renderer.render("eps")
            self.assertEqual(list(Path(media).rglob("*")), [])
        root = ElementTree.fromstring(svg)
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertTrue(eps.startswith(b"%!PS-Adobe"))
        self.assertFalse(get_document_model().objects.exists())
        self.assertFalse(QRCode.objects.exists())

    @override_settings(WAGTAIL_QR_CODE_BASE_URL="https://scan.example/")
    def test_payload_is_full_url_with_page_id(self):
        renderer = WagtailQrCode(self.page)
        url = f"https://scan.example/qr-code/?id={self.page.pk}"
        self.assertEqual(renderer.encoded_url(), url)
        self.assertEqual(renderer.make_qr_code(url).data.decode(), url)
        original = renderer.render("eps")
        self.page.title = "New title"
        self.page.slug = "new-slug"
        self.assertEqual(
            eps_without_timestamp(renderer.render("eps")),
            eps_without_timestamp(original),
        )

    def test_admin_base_url_fallback(self):
        self.assertEqual(
            WagtailQrCode(self.page).encoded_url(),
            f"http://localhost:8000/qr-code/?id={self.page.pk}",
        )

    def test_title_is_escaped_in_svg(self):
        self.page.title = '</title><script>alert("bad")</script>&'
        svg = WagtailQrCode(self.page).render("svg")
        root = ElementTree.fromstring(svg)
        self.assertEqual(root[0].text, self.page.title)
        self.assertNotIn(b"<script>", svg)

    @override_settings(WAGTAIL_QR_CODE={"scale": 1})
    def test_partial_settings_keep_defaults(self):
        renderer = WagtailQrCode(self.page)
        self.assertEqual(renderer.settings["quiet_zone"], 6)
        self.assertIn(b"<svg", renderer.render("svg"))

    def test_unsaved_page_and_unsupported_format(self):
        with self.assertRaisesMessage(ValueError, "Save the page"):
            WagtailQrCode(QRCodePage()).render("eps")
        with self.assertRaisesMessage(ValueError, "Unsupported"):
            WagtailQrCode(self.page).render("pdf")

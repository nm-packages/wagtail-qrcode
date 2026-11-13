from django.db import IntegrityError, transaction
from django.test import TestCase
from wagtail.models import Page

from tests.testapp.models import QRCodePage
from wagtail_qrcode.models import QRCode


class TestModels(TestCase):
    def setUp(self):
        self.page = Page.objects.get(pk=2).add_child(
            instance=QRCodePage(title="QR page")
        )

    def test_usage_stays_outside_revisions(self):
        revision = self.page.save_revision()
        QRCode.objects.create(page=self.page, usage_count=7)
        revision.publish()
        self.page.refresh_from_db()
        self.assertEqual(self.page.qr_code_usage, 7)
        for field in ("qr_code_svg", "qr_code_eps", "qr_code_usage", "qr_code_record"):
            self.assertNotIn(field, revision.content)
        self.assertFalse(hasattr(self.page, "qr_code_eps"))
        self.assertEqual(QRCodePage().qr_code_usage, 0)

    def test_one_record_per_page_and_cascade_deletion(self):
        QRCode.objects.create(page=self.page, usage_count=3)
        with self.assertRaises(IntegrityError), transaction.atomic():
            QRCode.objects.create(page=self.page)
        self.page.delete()
        self.assertFalse(QRCode.objects.exists())

    def test_copy_and_alias_do_not_share_counter(self):
        QRCode.objects.create(page=self.page, usage_count=3)
        copy = self.page.copy(update_attrs={"title": "Copy", "slug": "copy"})
        alias = self.page.create_alias(update_slug="alias")
        self.assertEqual(copy.qr_code_usage, 0)
        self.assertEqual(alias.specific.qr_code_usage, 0)
        self.assertEqual(self.page.qr_code_usage, 3)
        self.assertEqual(QRCode.objects.count(), 1)

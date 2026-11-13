from django.core import mail
from django.db import transaction
from django.test import TestCase
from wagtail.models import Page

from tests.testapp.models import QRCodePage
from tests.utils import eps_without_timestamp
from wagtail_qrcode.cls import WagtailQrCode
from wagtail_qrcode.wagtail_hooks import send_qr_code_email


class TestWagtailHooks(TestCase):
    def setUp(self):
        self.page = Page.objects.get(pk=2).add_child(
            instance=QRCodePage(title="QR page")
        )

    def test_email_attachment_is_generated_after_explicit_request(self):
        with self.captureOnCommitCallbacks(execute=True):
            send_qr_code_email(self.page, email="reader@example.com")
            self.assertEqual(len(mail.outbox), 0)
        message = mail.outbox[0]
        self.assertEqual(message.subject, "QR Code for QR page")
        self.assertEqual(message.body, message.subject)
        self.assertEqual(message.to, ["reader@example.com"])
        self.assertEqual(message.attachments[0][0], f"qr-code-{self.page.pk}.eps")
        self.assertEqual(
            eps_without_timestamp(message.attachments[0][1]),
            eps_without_timestamp(WagtailQrCode(self.page).render("eps")),
        )
        self.assertEqual(message.attachments[0][2], "application/postscript")

    def test_no_recipient_does_not_render_or_send(self):
        with self.captureOnCommitCallbacks(execute=True):
            send_qr_code_email(QRCodePage())
        self.assertEqual(len(mail.outbox), 0)

    def test_rollback_does_not_send(self):
        with self.captureOnCommitCallbacks(execute=True):
            with transaction.atomic():
                send_qr_code_email(self.page, email="reader@example.com")
                transaction.set_rollback(True)
        self.assertEqual(len(mail.outbox), 0)

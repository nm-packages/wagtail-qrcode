from django.contrib.auth import get_user_model
from django.core import mail
from django.db import transaction
from django.test import TestCase, override_settings
from wagtail.models import Page

from tests.testapp.models import QRCodePage
from tests.utils import eps_without_timestamp
from wagtail_qrcode.cls import WagtailQrCode
from wagtail_qrcode.wagtail_hooks import alias_qr_code_buttons, send_qr_code_email


class TestWagtailHooks(TestCase):
    def setUp(self):
        self.page = Page.objects.get(pk=2).add_child(
            instance=QRCodePage(title="QR page")
        )

    def test_alias_actions_require_qr_page_and_edit_permission(self):
        admin = get_user_model().objects.create_superuser("admin", "", "password")
        reader = get_user_model().objects.create_user("reader")
        alias = self.page.create_alias(update_slug="qr-alias")
        other = Page.objects.get(pk=2).add_child(instance=Page(title="Other page"))
        other_alias = other.create_alias(update_slug="other-alias")
        for page, user in (
            (self.page, admin),
            (other_alias, admin),
            (alias, reader),
        ):
            with self.subTest(page_id=page.pk, user=user):
                self.assertEqual(list(alias_qr_code_buttons(page, user, "edit")), [])

    def test_email_attachment_is_generated_after_explicit_request(self):
        with self.captureOnCommitCallbacks(execute=True):
            send_qr_code_email(self.page, email="reader@example.com")
            self.assertEqual(len(mail.outbox), 0)
        message = mail.outbox[0]
        self.assertEqual(message.subject, "Your QR code")
        self.assertEqual(
            message.body, "Please find your QR code attached as an EPS file."
        )
        self.assertEqual(message.to, ["reader@example.com"])
        self.assertEqual(message.attachments[0][0], f"qr-code-{self.page.pk}.eps")
        self.assertEqual(
            eps_without_timestamp(message.attachments[0][1]),
            eps_without_timestamp(WagtailQrCode(self.page).render("eps")),
        )
        self.assertEqual(message.attachments[0][2], "application/postscript")

    @override_settings(
        WAGTAIL_QRCODE_EMAIL_SUBJECT="Site QR code",
        WAGTAIL_QRCODE_EMAIL_BODY="Here is your attachment.",
    )
    def test_sender_uses_settings_when_message_is_omitted(self):
        with self.captureOnCommitCallbacks(execute=True):
            send_qr_code_email(self.page, email="reader@example.com")
        self.assertEqual(mail.outbox[0].subject, "Site QR code")
        self.assertEqual(mail.outbox[0].body, "Here is your attachment.")

    def test_sender_preserves_explicit_empty_messages(self):
        with self.captureOnCommitCallbacks(execute=True):
            send_qr_code_email(
                self.page, email="reader@example.com", subject="", body=""
            )
        self.assertEqual(mail.outbox[0].subject, "")
        self.assertEqual(mail.outbox[0].body, "")

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

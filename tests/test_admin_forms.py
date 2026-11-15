from django.test import SimpleTestCase, override_settings

from wagtail_qrcode.admin_forms import QrCodeEmailFieldsForm


class TestEmailDefaults(SimpleTestCase):
    def test_defaults_are_editable_values_with_no_recipient(self):
        form = QrCodeEmailFieldsForm()
        self.assertIsNone(form["email_address"].value())
        self.assertEqual(form["email_subject"].value(), "Your QR code")
        self.assertEqual(
            form["email_body"].value(),
            "Please find your QR code attached as an EPS file.",
        )

    @override_settings(
        WAGTAIL_QRCODE_EMAIL_SUBJECT="Site QR code",
        WAGTAIL_QRCODE_EMAIL_BODY="Here is your attachment.",
    )
    def test_settings_override_defaults_at_form_creation(self):
        form = QrCodeEmailFieldsForm()
        self.assertEqual(form["email_subject"].value(), "Site QR code")
        self.assertEqual(form["email_body"].value(), "Here is your attachment.")

    def test_explicit_initial_values_take_precedence(self):
        form = QrCodeEmailFieldsForm(
            initial={"email_subject": "Custom subject", "email_body": ""}
        )
        self.assertEqual(form["email_subject"].value(), "Custom subject")
        self.assertEqual(form["email_body"].value(), "")

    def test_invalid_submission_preserves_edits_and_cleared_body(self):
        form = QrCodeEmailFieldsForm(
            data={
                "email_address": "reader@example.com",
                "email_subject": "Edited subject",
                "email_body": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form["email_subject"].value(), "Edited subject")
        self.assertEqual(form["email_body"].value(), "")
        self.assertIn("email_body", form.errors)

    def test_missing_message_fields_are_not_replaced_on_submission(self):
        form = QrCodeEmailFieldsForm(data={"email_address": "reader@example.com"})
        self.assertFalse(form.is_valid())
        self.assertIn("email_subject", form.errors)
        self.assertIn("email_body", form.errors)

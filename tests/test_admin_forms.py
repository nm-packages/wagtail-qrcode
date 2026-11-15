from unittest.mock import Mock

from django import forms
from django.test import SimpleTestCase, override_settings

from wagtail_qrcode.admin_forms import QrCodeEmailFieldsForm


class CustomMessagesForm(QrCodeEmailFieldsForm):
    email_subject = forms.CharField(initial="Approved subject", required=False)
    email_body = forms.CharField(initial="Approved body", required=False)


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
        for form_class in (QrCodeEmailFieldsForm, CustomMessagesForm):
            with self.subTest(form_class=form_class):
                form = form_class(
                    initial={"email_subject": "Custom subject", "email_body": ""}
                )
                self.assertEqual(form["email_subject"].value(), "Custom subject")
                self.assertEqual(form["email_body"].value(), "")

    @override_settings(
        WAGTAIL_QRCODE_EMAIL_SUBJECT="Site QR code",
        WAGTAIL_QRCODE_EMAIL_BODY="Here is your attachment.",
    )
    def test_custom_field_initial_values_take_precedence_over_defaults(self):
        form = CustomMessagesForm()
        self.assertEqual(form["email_subject"].value(), "Approved subject")
        self.assertEqual(form["email_body"].value(), "Approved body")

    def test_empty_field_initial_values_preserve_conditional_validation(self):
        class EmptyMessagesForm(QrCodeEmailFieldsForm):
            email_subject = forms.CharField(initial="", disabled=True, required=False)
            email_body = forms.CharField(initial="", disabled=True, required=False)

        form = EmptyMessagesForm()
        self.assertEqual(form["email_subject"].value(), "")
        self.assertEqual(form["email_body"].value(), "")
        self.assertTrue(EmptyMessagesForm(data={}).is_valid())
        bound = EmptyMessagesForm(data={"email_address": "reader@example.com"})
        self.assertFalse(bound.is_valid())
        self.assertIn("email_subject", bound.errors)
        self.assertIn("email_body", bound.errors)

    def test_callable_field_initial_values_are_used_without_eager_evaluation(self):
        subject = Mock(return_value="Generated subject")
        body = Mock(return_value="Generated body")

        class CallableMessagesForm(QrCodeEmailFieldsForm):
            email_subject = forms.CharField(initial=subject, disabled=True)
            email_body = forms.CharField(initial=body, disabled=True)

        form = CallableMessagesForm()
        subject.assert_not_called()
        body.assert_not_called()
        self.assertEqual(form["email_subject"].value(), "Generated subject")
        self.assertEqual(form["email_body"].value(), "Generated body")
        bound = CallableMessagesForm(data={"email_address": "reader@example.com"})
        self.assertTrue(bound.is_valid(), bound.errors)
        self.assertEqual(bound.cleaned_data["email_subject"], "Generated subject")
        self.assertEqual(bound.cleaned_data["email_body"], "Generated body")

    def test_submitted_edits_and_empty_values_override_custom_field_initials(self):
        for body in ("Edited body", ""):
            with self.subTest(body=body):
                form = CustomMessagesForm(
                    data={
                        "email_address": "reader@example.com",
                        "email_subject": "Edited subject",
                        "email_body": body,
                    }
                )
                self.assertEqual(form.is_valid(), bool(body))
                self.assertEqual(form["email_subject"].value(), "Edited subject")
                self.assertEqual(form["email_body"].value(), body)
                if not body:
                    self.assertIn("email_body", form.errors)

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

import tempfile
from datetime import timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.db import transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from wagtail.documents import get_document_model
from wagtail.models import GroupApprovalTask, Page, Workflow, WorkflowPage, WorkflowTask

from tests.testapp.models import QRCodePage
from tests.utils import eps_without_timestamp
from wagtail_qrcode.cls import WagtailQrCode
from wagtail_qrcode.models import QRCode


class TestQRCodeEditor(TestCase):
    def setUp(self):
        self.media = self.enterContext(tempfile.TemporaryDirectory())
        self.enterContext(self.settings(MEDIA_ROOT=self.media))
        user = get_user_model().objects.create_superuser("editor", "", "password")
        self.client.force_login(user)
        self.parent = Page.objects.get(pk=2)
        self.page = self.parent.add_child(instance=QRCodePage(title="Published title"))
        self.page.save_revision().publish()
        self.page.refresh_from_db()
        self.edit_url = reverse("wagtailadmin_pages:edit", args=[self.page.pk])
        self.live_revision_id = self.page.live_revision_id
        self.payload = WagtailQrCode(self.page).encoded_url()

    def tearDown(self):
        self.assertFalse(get_document_model().objects.exists())
        self.assertEqual(list(Path(self.media).rglob("*")), [])
        super().tearDown()

    def form_data(self, title="Edited title", email=True):
        revision = self.page.get_latest_revision()
        data = {
            "title": title,
            "slug": self.page.slug,
            "loaded_revision_id": revision.pk,
            "loaded_revision_created_at": revision.created_at.isoformat(),
        }
        if email:
            data.update(
                email_address="recipient@example.com",
                email_subject="Requested QR code",
                email_body="Please find the EPS attached.",
            )
        return data

    def assert_live_unchanged(self):
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, "Published title")
        self.assertEqual(self.page.live_revision_id, self.live_revision_id)
        self.assertEqual(WagtailQrCode(self.page).encoded_url(), self.payload)

    def assert_email(self, page):
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["recipient@example.com"])
        self.assertEqual(message.attachments[0][0], f"qr-code-{page.pk}.eps")
        self.assertEqual(
            eps_without_timestamp(message.attachments[0][1]),
            eps_without_timestamp(WagtailQrCode(page).render("eps")),
        )

    def test_editor_has_preview_and_downloads_without_document_chooser(self):
        response = self.client.get(self.edit_url)
        self.assertContains(
            response, reverse("wagtail_qrcode_admin:preview", args=[self.page.pk])
        )
        self.assertContains(response, "Download SVG")
        self.assertContains(response, "Download EPS")
        self.assertContains(response, "0 scans")
        self.assertContains(response, "Reset scan count")
        self.assertContains(response, "wagtail_qrcode/js/reset-scan-count.js")
        self.assertContains(response, "disabled>")
        for name in ("qr_code_eps", "qr_code_svg", "qr_code_usage"):
            self.assertNotContains(response, f'name="{name}"')
        self.assertFalse(QRCode.objects.exists())

    def test_editor_prefills_messages_and_sends_them_on_explicit_save(self):
        response = self.client.get(self.edit_url)
        form = response.context["form"]
        subject = form["email_subject"].value()
        body = form["email_body"].value()
        self.assertContains(response, 'value="Your QR code"')
        self.assertContains(
            response, "Please find your QR code attached as an EPS file."
        )
        self.assertIsNone(form["email_address"].value())
        data = self.form_data()
        data.update(email_subject=subject, email_body=body)
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, 302)
        self.assert_email(self.page)
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(mail.outbox[0].body, body)
        response = self.client.get(self.edit_url)
        self.assertIsNone(response.context["form"]["email_address"].value())

    def test_reset_does_not_save_publish_or_email_editor_input(self):
        QRCode.objects.create(page=self.page, usage_count=12)
        revision_count = self.page.revisions.count()
        response = self.client.get(self.edit_url)
        reset_url = reverse("wagtail_qrcode_admin:reset", args=[self.page.pk])
        self.assertContains(response, f'data-qr-reset-url="{reset_url}"')
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reset_url, self.form_data())
        self.assertEqual(response.status_code, 200)
        self.assert_live_unchanged()
        self.assertEqual(self.page.revisions.count(), revision_count)
        self.assertEqual(self.page.qr_code_usage, 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_repeated_autosave_keeps_live_content_and_sends_no_email(self):
        count = self.page.revisions.count()
        data = self.form_data()
        for title in ("First autosave", "Second autosave"):
            data["title"] = title
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    self.edit_url, data, headers={"Accept": "application/json"}
                )
            self.assertTrue(response.json()["success"])
            data["overwrite_revision_id"] = response.json()["revision_id"]
            self.assert_live_unchanged()
            self.assertEqual(self.page.get_latest_revision().content["title"], title)
            self.assertEqual(self.page.revisions.count(), count + 1)
            self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(QRCode.objects.exists())

    def test_draft_save_emails_without_changing_live_page_or_counter(self):
        QRCode.objects.create(page=self.page, usage_count=9)
        count = self.page.revisions.count()
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.edit_url, self.form_data())
        self.assertEqual(response.status_code, 302)
        self.assert_live_unchanged()
        draft = self.page.get_latest_revision_as_object()
        self.assertEqual(draft.title, "Edited title")
        self.assertEqual(self.page.revisions.count(), count + 1)
        self.assertEqual(draft.qr_code_usage, 9)
        self.assert_email(draft)

    def test_explicit_publish_after_autosave_sends_only_requested_email(self):
        data = self.form_data("Autosaved title")
        response = self.client.post(
            self.edit_url, data, headers={"Accept": "application/json"}
        )
        self.assertTrue(response.json()["success"])
        data = self.form_data("Published after autosave")
        data["action-publish"] = "Publish"
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, 302)
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, "Published after autosave")
        self.assertEqual(self.page.latest_revision_id, self.page.live_revision_id)
        self.assertEqual(WagtailQrCode(self.page).encoded_url(), self.payload)
        self.assert_email(self.page)

    def test_invalid_email_does_not_save_or_send(self):
        count = self.page.revisions.count()
        for invalid in (
            {"email_address": "invalid"},
            {"email_subject": ""},
            {"email_body": ""},
        ):
            data = self.form_data()
            data.update(invalid)
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(self.edit_url, data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
        self.assert_live_unchanged()
        self.assertEqual(self.page.revisions.count(), count)
        self.assertEqual(len(mail.outbox), 0)

    def test_create_autosave_then_save_emails_without_assets(self):
        url = reverse(
            "wagtailadmin_pages:add",
            args=[QRCodePage._meta.app_label, "qrcodepage", self.parent.pk],
        )
        data = {
            "title": "New page",
            "slug": "new-page",
            "email_address": "recipient@example.com",
            "email_subject": "QR",
            "email_body": "Attached",
        }
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                url, data, headers={"Accept": "application/json"}
            )
        page = QRCodePage.objects.get(pk=response.json()["pk"])
        self.assertFalse(page.live)
        self.assertEqual(len(mail.outbox), 0)
        data["action-save-draft"] = "Save draft"
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("wagtailadmin_pages:edit", args=[page.pk]), data
            )
        self.assertEqual(response.status_code, 302)
        page.refresh_from_db()
        self.assertFalse(page.live)
        self.assert_email(page)

    def test_create_publish_emails_once_without_extra_revision(self):
        url = reverse(
            "wagtailadmin_pages:add",
            args=[QRCodePage._meta.app_label, "qrcodepage", self.parent.pk],
        )
        data = {
            "title": "New page",
            "slug": "new-page",
            "action-publish": "Publish",
            "email_address": "recipient@example.com",
            "email_subject": "QR",
            "email_body": "Attached",
        }
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        page = QRCodePage.objects.get(slug="new-page")
        self.assertTrue(page.live)
        self.assertEqual(page.revisions.count(), 1)
        self.assert_email(page)

    def test_workflow_approval_keeps_page_identity(self):
        workflow = Workflow.objects.create(name="QR review")
        task = GroupApprovalTask.objects.create(name="Approve QR page")
        WorkflowTask.objects.create(workflow=workflow, task=task, sort_order=0)
        WorkflowPage.objects.create(workflow=workflow, page=self.page)
        data = self.form_data("Submitted title", email=False)
        data["action-submit"] = "Submit for moderation"
        self.assertEqual(self.client.post(self.edit_url, data).status_code, 302)
        self.assert_live_unchanged()
        data = self.form_data("Approved title", email=False)
        data.update(
            {
                "action-workflow-action": "1",
                "workflow-action-name": "approve",
                "workflow-task-state-id": self.page.current_workflow_task_state.pk,
            }
        )
        self.assertEqual(self.client.post(self.edit_url, data).status_code, 302)
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, "Approved title")
        self.assertEqual(WagtailQrCode(self.page).encoded_url(), self.payload)
        self.assertEqual(len(mail.outbox), 0)

    def test_scheduled_publication_and_aliases_keep_independent_identity(self):
        alias = self.page.create_alias(update_slug="alias")
        chained = alias.create_alias(update_slug="chained")
        data = self.form_data()
        go_live_at = (timezone.now() + timedelta(days=1)).replace(microsecond=0)
        data.update(go_live_at=go_live_at.isoformat(), **{"action-publish": "Publish"})
        with self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(self.client.post(self.edit_url, data).status_code, 302)
        self.assert_live_unchanged()
        self.assert_email(self.page)
        with (
            self.captureOnCommitCallbacks(execute=True),
            patch(
                "django.utils.timezone.now",
                return_value=go_live_at + timedelta(seconds=1),
            ),
        ):
            call_command("publish_scheduled", stdout=StringIO())
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, "Edited title")
        for page in (alias, chained):
            page.refresh_from_db()
            self.assertEqual(page.title, "Edited title")
            self.assertTrue(
                WagtailQrCode(page).encoded_url().endswith(f"?id={page.pk}")
            )
        self.assertEqual(len(mail.outbox), 1)

    def test_restoring_revision_preserves_scan_counter(self):
        old_revision = self.page.get_latest_revision()
        data = self.form_data(email=False)
        data["action-publish"] = "Publish"
        self.client.post(self.edit_url, data)
        QRCode.objects.create(page=self.page, usage_count=12)
        old_revision.as_object().save_revision().publish()
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, "Published title")
        self.assertEqual(self.page.qr_code_usage, 12)
        self.assertEqual(WagtailQrCode(self.page).encoded_url(), self.payload)

    def test_rollback_sends_no_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            with transaction.atomic():
                self.assertEqual(
                    self.client.post(self.edit_url, self.form_data()).status_code, 302
                )
                transaction.set_rollback(True)
        self.assertEqual(len(mail.outbox), 0)
        self.assert_live_unchanged()

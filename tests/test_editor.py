import tempfile
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.db import transaction
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from wagtail.documents import get_document_model
from wagtail.models import Page

from tests.testapp.models import QRCodePage
from wagtail_qrcode.wagtail_hooks import generate_qr_code


class TestQRCodeEditor(TestCase):
    def setUp(self):
        media = self.enterContext(tempfile.TemporaryDirectory())
        self.enterContext(self.settings(MEDIA_ROOT=media))
        self.user = get_user_model().objects.create_superuser(
            username="editor", email="editor@example.com", password="password"
        )
        self.client.force_login(self.user)
        self.parent = Page.objects.get(pk=2)
        self.page = self.parent.add_child(instance=QRCodePage(title="Published title"))
        self.page.save_revision().publish()
        self.page.refresh_from_db()
        generate_qr_code(RequestFactory().get("/"), self.page)
        self.page.refresh_from_db()
        self.edit_url = reverse("wagtailadmin_pages:edit", args=[self.page.pk])
        self.live_revision_id = self.page.live_revision_id
        self.live_document_id = self.page.qr_code_eps_id
        self.live_svg = self.page.qr_code_svg

    def form_data(self, title="Edited title", email=True):
        revision = self.page.get_latest_revision()
        data = {
            "title": title,
            "slug": self.page.slug,
            "qr_code_usage": "0",
            "qr_code_svg": self.live_svg,
            "qr_code_eps": self.live_document_id,
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
        self.assertEqual(self.page.qr_code_eps_id, self.live_document_id)
        self.assertEqual(self.page.qr_code_svg, self.live_svg)

    def assert_email(self, page):
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["recipient@example.com"])
        self.assertEqual(message.subject, "Requested QR code")
        self.assertEqual(message.body, "Please find the EPS attached.")
        self.assertEqual(message.attachments[0][0], f"qr-code-{page.pk}.eps")
        with page.qr_code_eps.file.open("rb") as eps:
            self.assertEqual(message.attachments[0][1], eps.read())

    def test_repeated_autosave_keeps_live_content_and_sends_no_email(self):
        revision_count = self.page.revisions.count()
        data = self.form_data("Autosaved title one")
        for title in ("Autosaved title one", "Autosaved title two"):
            data["title"] = title
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    self.edit_url, data, headers={"Accept": "application/json"}
                )
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result["success"])
            self.assert_live_unchanged()
            self.assertEqual(self.page.latest_revision_id, result["revision_id"])
            self.assertEqual(self.page.get_latest_revision().content["title"], title)
            self.assertEqual(self.page.revisions.count(), revision_count + 1)
            self.assertEqual(get_document_model().objects.count(), 1)
            self.assertEqual(len(mail.outbox), 0)
            data["overwrite_revision_id"] = result["revision_id"]

    def test_explicit_draft_save_keeps_live_content_and_emails_draft_qr_once(self):
        count = self.page.revisions.count()
        data = self.form_data()
        data["action-save-draft"] = "Save draft"
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, 302)
        self.assert_live_unchanged()
        self.assertTrue(self.page.has_unpublished_changes)
        draft = self.page.get_latest_revision_as_object()
        self.assertEqual(draft.title, "Edited title")
        self.assertIn("<title>Edited title</title>", draft.qr_code_svg)
        self.assertEqual(draft.qr_code_eps.title, draft.title)
        self.assertEqual(self.page.revisions.count(), count + 1)
        self.assert_email(draft)

    def test_draft_save_with_unchanged_title_preserves_published_document(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                self.edit_url, self.form_data("Published title", email=False)
            )
        self.assertEqual(response.status_code, 302)
        self.assert_live_unchanged()
        self.assertTrue(
            get_document_model().objects.filter(pk=self.live_document_id).exists()
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_publish_after_autosave_sends_only_the_explicit_email(self):
        data = self.form_data("Autosaved title")
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                self.edit_url, data, headers={"Accept": "application/json"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(len(mail.outbox), 0)
        self.assert_live_unchanged()
        data = self.form_data("Published after autosave")
        data["action-publish"] = "Publish"
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, 302)
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, "Published after autosave")
        self.assertEqual(self.page.latest_revision_id, self.page.live_revision_id)
        self.assert_email(self.page)

    def test_invalid_email_does_not_save_or_send(self):
        count = self.page.revisions.count()
        data = self.form_data()
        data["email_address"] = "invalid address"
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("email_address", response.context["form"].errors)
        self.assert_live_unchanged()
        self.assertEqual(self.page.revisions.count(), count)
        self.assertEqual(len(mail.outbox), 0)

    def test_explicit_publish_updates_qr_and_sends_once(self):
        count = self.page.revisions.count()
        data = self.form_data()
        data["action-publish"] = "Publish"
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, 302)
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, "Edited title")
        self.assertEqual(self.page.latest_revision_id, self.page.live_revision_id)
        self.assertFalse(self.page.has_unpublished_changes)
        self.assertEqual(self.page.revisions.count(), count + 1)
        self.assertIn("<title>Edited title</title>", self.page.qr_code_svg)
        self.assertEqual(self.page.qr_code_eps.title, self.page.title)
        revision_page = self.page.live_revision.as_object()
        self.assertEqual(revision_page.qr_code_eps_id, self.page.qr_code_eps_id)
        self.assertEqual(revision_page.qr_code_svg, self.page.qr_code_svg)
        self.assert_email(self.page)

    def test_create_autosave_then_explicit_save_generates_qr_and_emails_once(self):
        url = reverse(
            "wagtailadmin_pages:add",
            args=[QRCodePage._meta.app_label, "qrcodepage", self.parent.pk],
        )
        data = self.form_data("New QR page")
        data["slug"] = "new-qr-page"
        for key in ("loaded_revision_id", "loaded_revision_created_at", "qr_code_eps"):
            data.pop(key)
        data["qr_code_svg"] = ""
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                url, data, headers={"Accept": "application/json"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        page = QRCodePage.objects.get(pk=response.json()["pk"])
        self.assertFalse(page.live)
        self.assertFalse(page.qr_code_svg)
        self.assertIsNone(page.qr_code_eps)
        self.assertEqual(len(mail.outbox), 0)
        revision_count = page.revisions.count()
        data["action-save-draft"] = "Save draft"
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("wagtailadmin_pages:edit", args=[page.pk]), data
            )
        self.assertEqual(response.status_code, 302)
        page.refresh_from_db()
        self.assertFalse(page.live)
        self.assertIsNone(page.live_revision_id)
        self.assertEqual(page.revisions.count(), revision_count + 1)
        self.assertIn("<title>New QR page</title>", page.qr_code_svg)
        self.assertEqual(page.qr_code_eps.title, page.title)
        self.assert_email(page)

    def test_create_and_publish_generates_qr_before_email(self):
        url = reverse(
            "wagtailadmin_pages:add",
            args=[QRCodePage._meta.app_label, "qrcodepage", self.parent.pk],
        )
        data = self.form_data("New published page")
        data.update(slug="new-published-page", **{"action-publish": "Publish"})
        data.pop("qr_code_eps")
        data["qr_code_svg"] = ""
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        page = QRCodePage.objects.get(slug="new-published-page")
        self.assertTrue(page.live)
        self.assertEqual(page.revisions.count(), 1)
        self.assertEqual(page.latest_revision_id, page.live_revision_id)
        self.assertTrue(page.qr_code_svg)
        self.assert_email(page)

    def test_scheduled_publish_preserves_live_revision_and_schedule(self):
        data = self.form_data()
        go_live_at = (timezone.now() + timedelta(days=1)).replace(microsecond=0)
        data.update(go_live_at=go_live_at.isoformat(), **{"action-publish": "Publish"})
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, 302)
        self.assert_live_unchanged()
        revision = self.page.get_latest_revision()
        self.assertEqual(revision.approved_go_live_at, go_live_at)
        scheduled_page = revision.as_object()
        self.assertIn("<title>Edited title</title>", scheduled_page.qr_code_svg)
        self.assert_email(scheduled_page)

        with self.captureOnCommitCallbacks(execute=True):
            with patch(
                "django.utils.timezone.now",
                return_value=go_live_at + timedelta(seconds=1),
            ):
                call_command("publish_scheduled", stdout=StringIO())
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, "Edited title")
        self.assertEqual(self.page.live_revision_id, revision.pk)
        self.assertEqual(self.page.qr_code_eps_id, scheduled_page.qr_code_eps_id)
        self.assertEqual(self.page.qr_code_svg, scheduled_page.qr_code_svg)
        self.assertEqual(len(mail.outbox), 1)

    def test_rollback_sends_no_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            with transaction.atomic():
                response = self.client.post(self.edit_url, self.form_data())
                self.assertEqual(response.status_code, 302)
                self.assertEqual(len(mail.outbox), 0)
                transaction.set_rollback(True)
        self.assertEqual(len(mail.outbox), 0)
        self.assert_live_unchanged()

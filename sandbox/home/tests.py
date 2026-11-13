"""Integration checks for the contributor sandbox, under its own settings."""

import tempfile
from email import policy
from email.parser import BytesParser
from io import StringIO
from pathlib import Path

from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from home.management.commands.setup_sandbox import Command
from home.models import HomePage, QRCodePage
from reset import reset_data
from wagtail.documents import get_document_model
from wagtail.models import Page, Site

from wagtail_qrcode.cls import WagtailQrCode
from wagtail_qrcode.models import QRCode
from wagtail_qrcode.wagtail_hooks import send_qr_code_email


def eps_without_timestamp(content):
    return b"\n".join(
        line for line in content.splitlines() if not line.startswith(b"%%CreationDate:")
    )


class SandboxTests(TestCase):
    def setUp(self):
        # Migrations are tested by the runner; seed inside this transaction.
        Command().seed()
        self.page = QRCodePage.objects.get(sandbox_example="published")
        self.draft = QRCodePage.objects.get(sandbox_example="draft")
        self.user = get_user_model().objects.get(username="admin")

    def tearDown(self):
        self.assertFalse(get_document_model().objects.exists())
        self.assertEqual(list(Path(settings.MEDIA_ROOT).rglob("*")), [])
        super().tearDown()

    def test_setup_preserves_edited_examples_passwords_and_counts(self):
        self.page.title = "Contributor title"
        self.page.slug = "contributor-slug"
        self.page.save_revision().publish()
        self.draft.title = "Unfinished draft"
        self.draft.save_revision()
        self.user.set_password("changed-password")
        self.user.save()
        QRCode.objects.create(page=self.page, usage_count=8)
        before = (Page.objects.count(), Site.objects.count(), QRCode.objects.count())
        # Exercise the complete command, including its migrate invocation.
        call_command("setup_sandbox", stdout=StringIO(), verbosity=0)
        call_command("setup_sandbox", stdout=StringIO(), verbosity=0)
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, "Contributor title")
        self.assertEqual(self.page.slug, "contributor-slug")
        self.assertEqual(self.page.qr_code_usage, 8)
        self.assertEqual(
            self.draft.get_latest_revision_as_object().title, "Unfinished draft"
        )
        self.assertEqual(
            before, (Page.objects.count(), Site.objects.count(), QRCode.objects.count())
        )
        self.assertEqual(get_user_model().objects.filter(username="admin").count(), 1)
        self.assertTrue(
            get_user_model()
            .objects.get(pk=self.user.pk)
            .check_password("changed-password")
        )

    def test_setup_creates_no_qr_records_or_files(self):
        self.assertEqual(QRCodePage.objects.count(), 2)
        self.assertFalse(QRCode.objects.exists())

    def test_copy_and_alias_have_their_own_identity(self):
        QRCode.objects.create(page=self.page, usage_count=4)
        copy = self.page.copy(
            update_attrs={"title": "Copied example", "slug": "copied-example"},
            keep_live=False,
        )
        alias = self.page.create_alias(update_slug="alias-example")
        self.assertIsNone(copy.sandbox_example)
        self.assertEqual(copy.qr_code_usage, 0)
        self.assertEqual(alias.specific.qr_code_usage, 0)
        chained = alias.create_alias(update_slug="chained-alias")
        self.page.title = "Updated original"
        self.page.save_revision().publish()
        for page in (alias.specific, chained.specific):
            page.refresh_from_db()
            self.assertIsNone(page.sandbox_example)
            self.assertEqual(page.title, "Updated original")
        self.assertTrue(WagtailQrCode(copy).encoded_url().endswith(f"?id={copy.pk}"))
        Command().seed()
        self.assertEqual(QRCodePage.objects.count(), 5)

    def test_missing_example_does_not_overwrite_an_occupied_slug(self):
        self.draft.delete()
        home = HomePage.objects.first()
        manual = home.add_child(
            instance=QRCodePage(
                title="Manual page", slug="draft-qr-example", live=False
            )
        )
        Command().seed()
        self.assertEqual(QRCodePage.objects.get(pk=manual.pk).title, "Manual page")
        recreated = QRCodePage.objects.get(sandbox_example="draft")
        self.assertNotEqual(recreated.slug, manual.slug)
        self.assertFalse(recreated.live)

    def test_setup_updates_site_origin_without_replacing_content(self):
        site_id = Site.objects.get(root_page=HomePage.objects.first()).pk
        with self.settings(SANDBOX_HOST="192.168.1.10", SANDBOX_PORT=8000):
            Command().seed()
        site = Site.objects.get(pk=site_id)
        self.assertEqual((site.hostname, site.port), ("192.168.1.10", 8000))
        self.assertEqual(QRCodePage.objects.count(), 2)

    def test_examples_render_and_draft_stays_unpublished(self):
        self.assertTrue(self.page.live)
        self.assertFalse(self.draft.live)
        home = self.client.get("/")
        self.assertContains(home, self.page.title)
        self.assertNotContains(home, self.draft.title)
        response = self.client.get(self.page.url)
        self.assertContains(response, self.page.title)
        self.assertContains(response, "<svg")
        self.assertNotContains(response, "/documents/")
        self.assertEqual(self.client.get(self.draft.url).status_code, 404)
        self.assertFalse(QRCode.objects.exists())

    def test_downloads_are_generated_in_memory_and_require_login(self):
        url = reverse("wagtail_qrcode_admin:download", args=[self.page.pk, "eps"])
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.user)
        for page in (self.page, self.draft):
            for file_format in ("svg", "eps"):
                url = reverse(
                    "wagtail_qrcode_admin:download", args=[page.pk, file_format]
                )
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    eps_without_timestamp(response.content),
                    eps_without_timestamp(WagtailQrCode(page).render(file_format)),
                )
        self.assertFalse(QRCode.objects.exists())

    def test_encoded_url_survives_slug_change_and_counts_usage(self):
        generator = WagtailQrCode(self.page)
        payload = generator.encoded_url()
        self.assertEqual(
            payload,
            f"{settings.WAGTAIL_QR_CODE_BASE_URL}/qr-code/?id={self.page.pk}",
        )
        self.page.slug = "new-slug"
        self.page.save_revision().publish()
        response = self.client.get(reverse("qr_code_page_view"), {"id": self.page.pk})
        self.page.refresh_from_db()
        self.assertRedirects(response, self.page.url)
        self.assertEqual(self.page.qr_code_usage, 1)
        self.assertEqual(generator.encoded_url(), payload)
        self.assertEqual(
            self.client.get(
                reverse("qr_code_page_view"), {"id": self.draft.pk}
            ).status_code,
            404,
        )
        self.assertFalse(QRCode.objects.filter(page=self.draft).exists())

    def form_data(self, title):
        revision = self.page.get_latest_revision()
        return {
            "title": title,
            "slug": self.page.slug,
            "loaded_revision_id": revision.pk,
            "loaded_revision_created_at": revision.created_at.isoformat(),
            "email_address": "reader@example.test",
            "email_subject": "Sandbox EPS",
            "email_body": "QR code",
        }

    def test_editor_autosave_and_explicit_draft_email(self):
        self.client.force_login(self.user)
        url = reverse("wagtailadmin_pages:edit", args=[self.page.pk])
        editor = self.client.get(url)
        self.assertContains(editor, "Download SVG")
        self.assertContains(editor, "Download EPS")
        self.assertContains(editor, "email_address")
        self.assertNotContains(editor, 'name="qr_code_eps"')
        live_title = self.page.title
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                url,
                self.form_data("Autosaved title"),
                headers={"Accept": "application/json"},
            )
        self.assertTrue(response.json()["success"])
        self.assertEqual(len(mail.outbox), 0)
        data = self.form_data("Draft title")
        data["action-save-draft"] = "Save draft"
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, live_title)
        draft = self.page.get_latest_revision_as_object()
        self.assertEqual(draft.title, "Draft title")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["reader@example.test"])
        self.assertEqual(
            eps_without_timestamp(mail.outbox[0].attachments[0][1]),
            eps_without_timestamp(WagtailQrCode(draft).render("eps")),
        )
        self.assertFalse(QRCode.objects.exists())

    def test_file_capture_contains_generated_eps_without_a_document(self):
        with tempfile.TemporaryDirectory() as folder:
            if DJANGO_VERSION >= (6, 1):
                options = {
                    "MAILERS": {
                        "default": {
                            "BACKEND": "django.core.mail.backends.filebased.EmailBackend",
                            "OPTIONS": {"file_path": folder},
                        }
                    }
                }
            else:
                options = {
                    "EMAIL_BACKEND": "django.core.mail.backends.filebased.EmailBackend",
                    "EMAIL_FILE_PATH": folder,
                }
            with self.settings(**options), self.captureOnCommitCallbacks(execute=True):
                send_qr_code_email(self.page, email="reader@example.test")
            messages = list(Path(folder).glob("*.log"))
            self.assertEqual(len(messages), 1)
            message = BytesParser(policy=policy.default).parsebytes(
                messages[0].read_bytes()
            )
            self.assertEqual(message["To"], "reader@example.test")
            (attachment,) = message.iter_attachments()
            self.assertEqual(attachment.get_filename(), f"qr-code-{self.page.pk}.eps")
            self.assertEqual(
                eps_without_timestamp(attachment.get_payload(decode=True)),
                eps_without_timestamp(WagtailQrCode(self.page).render("eps")),
            )
        self.assertFalse(QRCode.objects.exists())

    def test_test_media_is_separate_from_manual_sandbox_media(self):
        self.assertNotEqual(
            Path(settings.MEDIA_ROOT), settings.SANDBOX_DATA_DIR / "media"
        )


class ResetTests(TestCase):
    def test_reset_is_limited_to_sandbox_data_and_preserves_local_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "sandbox"
            (project / ".data" / "media").mkdir(parents=True)
            (project / ".data" / "media" / "qr.eps").write_text("generated")
            (project / "settings").mkdir()
            local = project / "settings" / "local.py"
            local.write_text("SANDBOX_BASE_URL = 'http://localhost:8000'")
            unrelated = root / "db.sqlite3"
            unrelated.write_text("unrelated")
            reset_data(project)
            reset_data(project)
            self.assertFalse((project / ".data").exists())
            self.assertTrue(local.exists())
            self.assertEqual(unrelated.read_text(), "unrelated")

    def test_reset_refuses_a_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "sandbox"
            project.mkdir()
            (project / ".data").symlink_to(root, target_is_directory=True)
            with self.assertRaisesMessage(ValueError, "symlinked"):
                reset_data(project)

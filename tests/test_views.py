import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import Client, TestCase
from django.urls import reverse
from wagtail.documents import get_document_model
from wagtail.models import GroupPagePermission, Page, PageViewRestriction

from tests.testapp.models import QRCodePage
from tests.utils import eps_without_timestamp
from wagtail_qrcode.cls import WagtailQrCode
from wagtail_qrcode.models import QRCode


class TestViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = Page.objects.get(pk=2)
        cls.page = cls.parent.add_child(instance=QRCodePage(title="QR page"))
        cls.page.save_revision().publish()
        cls.other = cls.parent.add_child(instance=Page(title="Other page"))
        cls.other.save_revision().publish()
        cls.admin = get_user_model().objects.create_superuser(
            "qr-admin", "", "password"
        )

    def scan(self, page):
        return self.client.get(reverse("qr_code_page_view"), {"id": page.pk})

    def test_scan_redirects_and_counts_without_saving_page(self):
        before = self.page.latest_revision_id
        with patch.object(QRCodePage, "save", side_effect=AssertionError("page saved")):
            for count in range(1, 4):
                response = self.scan(self.page)
                self.assertRedirects(
                    response, self.page.url, fetch_redirect_response=False
                )
                self.assertEqual(self.page.qr_code_usage, count)
        self.page.refresh_from_db()
        self.assertEqual(self.page.latest_revision_id, before)
        self.assertIn("no-store", response["Cache-Control"])

    def test_bad_scan_ids_return_404_without_record(self):
        for value in (None, "", "no", "0", "-1", "9" * 100, "999999"):
            with self.subTest(value=value):
                params = {} if value is None else {"id": value}
                self.assertEqual(
                    self.client.get(reverse("qr_code_page_view"), params).status_code,
                    404,
                )
        self.assertFalse(QRCode.objects.exists())

    def test_unpublished_and_non_qr_pages_do_not_count(self):
        self.assertEqual(self.scan(self.other).status_code, 404)
        self.page.unpublish()
        self.assertEqual(self.scan(self.page).status_code, 404)
        self.assertFalse(QRCode.objects.exists())

    def test_scan_keeps_private_destination_access_controls(self):
        PageViewRestriction.objects.create(
            page=self.parent, restriction_type="password", password="secret"
        )
        response = self.scan(self.page)
        self.assertRedirects(response, self.page.url, fetch_redirect_response=False)
        destination = self.client.get(response.url)
        self.assertContains(destination, "password")
        self.assertEqual(self.page.qr_code_usage, 1)

    def test_scan_requires_get(self):
        self.assertEqual(
            self.client.post(
                reverse("qr_code_page_view"), {"id": self.page.pk}
            ).status_code,
            405,
        )
        self.assertFalse(QRCode.objects.exists())

    def test_copy_translation_and_alias_use_their_own_id(self):
        from wagtail.models import Locale

        locale = Locale.objects.create(language_code="fr")
        self.parent.copy_for_translation(locale)
        translated = self.page.copy_for_translation(locale)
        copied = self.page.copy(update_attrs={"slug": "copied"})
        alias = self.page.create_alias(update_slug="alias")
        chained = alias.create_alias(update_slug="chained")
        for page in (translated, copied, alias, chained):
            renderer = WagtailQrCode(page.specific)
            self.assertTrue(renderer.encoded_url().endswith(f"?id={page.pk}"))
        for page in (copied, alias, chained):
            self.assertRedirects(
                self.scan(page), page.url, fetch_redirect_response=False
            )
            self.assertEqual(page.specific.qr_code_usage, 1)
        self.assertEqual(self.page.qr_code_usage, 0)

    def test_preview_and_download_are_read_only_and_write_no_files(self):
        self.client.force_login(self.admin)
        with tempfile.TemporaryDirectory() as media, self.settings(MEDIA_ROOT=media):
            for file_format in ("svg", "eps"):
                url = reverse(
                    "wagtail_qrcode_admin:download", args=[self.page.pk, file_format]
                )
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    eps_without_timestamp(response.content),
                    eps_without_timestamp(WagtailQrCode(self.page).render(file_format)),
                )
                self.assertEqual(
                    response["Content-Disposition"],
                    f'attachment; filename="qr-code-{self.page.pk}.{file_format}"',
                )
                self.assertIn("no-store", response["Cache-Control"])
            response = self.client.get(
                reverse("wagtail_qrcode_admin:preview", args=[self.page.pk])
            )
            self.assertEqual(response["Content-Type"], "image/svg+xml")
            self.assertNotIn("Content-Disposition", response)
            self.assertEqual(list(Path(media).rglob("*")), [])
        self.assertFalse(QRCode.objects.exists())
        self.assertFalse(get_document_model().objects.exists())

    def test_download_requires_admin_and_page_permission(self):
        urls = [
            reverse("wagtail_qrcode_admin:preview", args=[self.page.pk]),
            reverse("wagtail_qrcode_admin:download", args=[self.page.pk, "eps"]),
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 302)
        user = get_user_model().objects.create_user("limited", password="password")
        group = Group.objects.create(name="Limited QR editors")
        group.permissions.add(Permission.objects.get(codename="access_admin"))
        user.groups.add(group)
        self.client.force_login(user)
        for url in urls:
            self.assertEqual(
                self.client.get(
                    url, headers={"X-Requested-With": "XMLHttpRequest"}
                ).status_code,
                403,
            )
        GroupPagePermission.objects.create(
            group=group,
            page=self.page,
            permission=Permission.objects.get(
                content_type__app_label="wagtailcore", codename="change_page"
            ),
        )
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200)
        user.is_active = False
        user.save()
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 302)

    def test_draft_download_and_invalid_targets(self):
        self.client.force_login(self.admin)
        self.page.unpublish()
        url = reverse("wagtail_qrcode_admin:download", args=[self.page.pk, "eps"])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.post(url).status_code, 405)
        for page_id, file_format in (
            (self.page.pk, "pdf"),
            (self.other.pk, "eps"),
            (999999, "svg"),
        ):
            url = reverse("wagtail_qrcode_admin:download", args=[page_id, file_format])
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_reset_count_without_editor_side_effects(self):
        self.client.force_login(self.admin)
        record = QRCode.objects.create(page=self.page, usage_count=42)
        QRCode.objects.create(page=self.other, usage_count=7)
        revision_ids = list(self.page.revisions.values_list("pk", flat=True))
        url = reverse("wagtail_qrcode_admin:reset", args=[self.page.pk])
        with patch.object(QRCodePage, "save", side_effect=AssertionError("page saved")):
            response = self.client.post(url)
        self.assertEqual(response.json()["usage_count"], 0)
        record.refresh_from_db()
        self.assertEqual(record.usage_count, 0)
        self.assertEqual(self.other.qr_code_record.usage_count, 7)
        self.assertEqual(
            list(self.page.revisions.values_list("pk", flat=True)), revision_ids
        )
        self.assertIn("no-store", response["Cache-Control"])
        self.scan(self.page)
        self.assertEqual(self.page.qr_code_usage, 1)

    def test_reset_missing_counter_and_draft_page(self):
        self.client.force_login(self.admin)
        self.page.unpublish()
        url = reverse("wagtail_qrcode_admin:reset", args=[self.page.pk])
        for _ in range(2):
            self.assertEqual(self.client.post(url).json()["usage_count"], 0)
        self.assertFalse(QRCode.objects.exists())

    def test_reset_requires_post_csrf_and_edit_permission(self):
        url = reverse("wagtail_qrcode_admin:reset", args=[self.page.pk])
        record = QRCode.objects.create(page=self.page, usage_count=42)
        self.assertEqual(self.client.post(url).status_code, 302)
        user = get_user_model().objects.create_user("reset-editor", password="password")
        group = Group.objects.create(name="Reset editors")
        group.permissions.add(Permission.objects.get(codename="access_admin"))
        user.groups.add(group)
        self.client.force_login(user)
        self.assertEqual(
            self.client.post(
                url, headers={"X-Requested-With": "XMLHttpRequest"}
            ).status_code,
            403,
        )
        GroupPagePermission.objects.create(
            group=group,
            page=self.page,
            permission=Permission.objects.get(
                content_type__app_label="wagtailcore", codename="change_page"
            ),
        )
        self.assertEqual(self.client.get(url).status_code, 405)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(user)
        self.assertEqual(csrf_client.post(url).status_code, 403)
        record.refresh_from_db()
        self.assertEqual(record.usage_count, 42)
        csrf_client.get(reverse("wagtailadmin_pages:edit", args=[self.page.pk]))
        self.assertEqual(
            csrf_client.post(
                url,
                headers={"X-CSRFToken": csrf_client.cookies["csrftoken"].value},
            ).status_code,
            200,
        )
        self.assertEqual(self.client.post(url).status_code, 200)
        user.is_active = False
        user.save()
        self.assertEqual(self.client.post(url).status_code, 302)

    def test_reset_rejects_invalid_targets(self):
        self.client.force_login(self.admin)
        for page_id in (self.other.pk, 999999):
            url = reverse("wagtail_qrcode_admin:reset", args=[page_id])
            self.assertEqual(self.client.post(url).status_code, 404)

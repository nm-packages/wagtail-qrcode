from django.conf import settings
from django.core import mail
from django.test import RequestFactory, TestCase
from wagtail.documents import get_document_model
from wagtail.models import Page

from tests.testapp.models import QRCodePage
from wagtail_qrcode.models import QRCodeMixin
from wagtail_qrcode.wagtail_hooks import (
    delete_document,
    generate_qr_code,
    send_qr_code_email,
)


class TestWagtailHooks(TestCase):
    def test_generate_qr_code(self):
        request = RequestFactory().get("/")
        page = QRCodePage(title="Test Page")

        self.assertEqual(page.qr_code_svg, None)
        self.assertEqual(page.qr_code_eps, None)
        self.assertEqual(page.qr_code_usage, 0)

        root_page = Page.objects.get(id=1)
        home_page = root_page.get_children().first()
        home_page.add_child(instance=page)

        rev = page.save_revision()
        rev.publish()

        test_page = QRCodePage.objects.get(id=page.id)

        generate_qr_code(request, test_page)

        rev = test_page.save_revision()
        rev.publish()

        document = get_document_model().objects.get()
        self.assertEqual(test_page.qr_code_svg[:4], "<svg")
        self.assertEqual(test_page.qr_code_eps_id, document.pk)
        self.assertEqual(document.title, test_page.title)
        self.assertEqual(test_page.qr_code_usage, 0)

    def test_send_qr_code_email(self):
        request = RequestFactory().get("/")
        page = QRCodePage(title="Test Page")

        root_page = Page.objects.get(id=1)
        home_page = root_page.get_children().first()
        home_page.add_child(instance=page)

        rev = page.save_revision()
        rev.publish()

        test_page = QRCodePage.objects.get(id=page.id)

        generate_qr_code(request, test_page)

        send_qr_code_email(
            test_page,
            email="foo@bar.com",
            subject="QR Code for Test Page",
            body="QR Code for Test Page",
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "QR Code for Test Page")
        self.assertEqual(mail.outbox[0].body, "QR Code for Test Page")
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(mail.outbox[0].to, ["foo@bar.com"])
        self.assertEqual(
            mail.outbox[0].attachments[0][0], "qr-code-{}.eps".format(test_page.id)
        )

    def test_is_qrcode_instance(self):
        # not inherit from QRCodeMixin
        page = Page(title="Test Page")

        home_page = Page.objects.get(id=1)
        home_page.add_child(instance=page)

        rev = page.save_revision()
        rev.publish()

        test_page = Page.objects.get(id=page.id)

        self.assertNotIsInstance(test_page, QRCodeMixin)

        # inherit from QRCodeMixin
        qr_code_page = QRCodePage(title="Test Page")

        home_page.add_child(instance=qr_code_page)

        rev = qr_code_page.save_revision()
        rev.publish()

        test_qr_code_page = QRCodePage.objects.get(id=qr_code_page.id)

        self.assertIsInstance(test_qr_code_page, QRCodeMixin)

    def test_delete_document(self):
        request = RequestFactory().get("/")
        page = QRCodePage(title="Test Page")

        root_page = Page.objects.get(id=1)
        home_page = root_page.get_children().first()
        home_page.add_child(instance=page)

        rev = page.save_revision()
        rev.publish()

        test_page = QRCodePage.objects.get(id=page.id)

        generate_qr_code(request, test_page)

        document_id = test_page.qr_code_eps_id
        self.assertTrue(get_document_model().objects.filter(pk=document_id).exists())

        delete_document(request, test_page)

        self.assertFalse(get_document_model().objects.filter(pk=document_id).exists())

    def test_delete_document_not_qrcode_page(self):
        request = RequestFactory().get("/")
        page = Page(title="Test Page")

        root_page = Page.objects.get(id=1)
        home_page = root_page.get_children().first()
        home_page.add_child(instance=page)

        rev = page.save_revision()
        rev.publish()

        test_page = Page.objects.get(id=page.id)

        result = delete_document(request, test_page)

        # really should be None as the page does not inherit from QRCodeMixin
        # and the function doesn't return anything
        self.assertEqual(result, None)

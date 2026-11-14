import io
import tempfile

import pyqrcode
from django.core.files.base import File
from django.test import TestCase, override_settings
from wagtail.documents import get_document_model
from wagtail.models import Collection, Page

from tests.testapp.models import QRCodePage
from wagtail_qrcode.cls import WagtailQrCode, create_collection

Document = get_document_model()


class TestWagtailQrCode(TestCase):
    def setUp(self):
        home_page = Page.objects.get(id=2)
        self.test_page = home_page.add_child(
            instance=QRCodePage(
                title="Test Page",
            ),
        )
        rev = self.test_page.save_revision()
        rev.publish()

    def test_settings(self):
        instance = WagtailQrCode(self.test_page)
        self.assertIsInstance(instance.settings["scale"], int)
        self.assertEqual(instance.settings["scale"], 3)
        self.assertIsInstance(instance.settings["quiet_zone"], int)
        self.assertEqual(instance.settings["quiet_zone"], 6)
        self.assertIsInstance(instance.settings["svg_has_xml_declaration"], bool)
        self.assertEqual(instance.settings["svg_has_xml_declaration"], False)
        self.assertIsInstance(instance.settings["svg_has_doc_type_declaration"], bool)
        self.assertEqual(instance.settings["svg_has_doc_type_declaration"], False)

    @override_settings(
        WAGTAIL_QR_CODE={
            "scale": 1,
            "quiet_zone": 2,
            "svg_has_xml_declaration": True,
            "svg_has_doc_type_declaration": True,
        }
    )
    def test_override_settings(self):
        instance = WagtailQrCode(self.test_page)
        self.assertIsInstance(instance.settings["scale"], int)
        self.assertEqual(instance.settings["scale"], 1)
        self.assertIsInstance(instance.settings["quiet_zone"], int)
        self.assertEqual(instance.settings["quiet_zone"], 2)
        self.assertIsInstance(instance.settings["svg_has_xml_declaration"], bool)
        self.assertEqual(instance.settings["svg_has_xml_declaration"], True)
        self.assertIsInstance(instance.settings["svg_has_doc_type_declaration"], bool)
        self.assertEqual(instance.settings["svg_has_doc_type_declaration"], True)

    def test_create_collection(self):
        collection = create_collection("Foo Collection")
        self.assertIsInstance(collection, Collection)
        self.assertEqual(collection.name, "Foo Collection")

    def test_create_collection_exists(self):
        count = Collection.objects.count()  # includes root collection
        root_collection = Collection.get_first_root_node()
        root_collection.add_child(name="Custom Collection")
        create_collection("Custom Collection")
        self.assertEqual(Collection.objects.count(), count + 1)

    def test_instance_past_collection(self):
        root_collection = Collection.get_first_root_node()
        collection = root_collection.add_child(name="Custom Collection")
        instance = WagtailQrCode(self.test_page, collection=collection)
        self.assertEqual(instance.collection, collection)

    def test_make_qr_code(self):
        instance = WagtailQrCode(self.test_page)
        qrc = instance.make_qr_code("foo string")
        self.assertIsInstance(qrc, pyqrcode.QRCode)
        self.assertEqual(str(qrc.data), "b'foo string'")

    def test_make_svg(self):
        instance = WagtailQrCode(self.test_page)
        qrc = pyqrcode.create("bar string")
        svg = instance.make_svg(qrc)
        self.assertIsInstance(svg, str)
        self.assertIn(
            '<svg height="111" width="111" class="pyqrcode"><title>Test Page</title>',
            svg,
        )
        self.assertEqual(svg[:4], "<svg")
        self.assertEqual(svg[-7:].replace("\n", ""), "</svg>")

    def test_make_eps(self):
        instance = WagtailQrCode(self.test_page)
        qrc = pyqrcode.create("baz string")
        eps = instance.make_eps(qrc)
        self.assertIsInstance(eps, io.StringIO)
        self.assertIsNotNone(eps.getvalue())

    def test_make_document(self):
        root_collection = Collection.get_first_root_node()
        collection = root_collection.add_child(name="Custom Collection")
        instance = WagtailQrCode(self.test_page, collection=collection)
        qrc = pyqrcode.create("foo string")
        eps = io.StringIO()
        qrc.eps(eps, scale=3, quiet_zone=3)
        document = instance.make_document("Foo Doc", eps, collection)
        self.assertIsInstance(document, Document)
        self.assertEqual(document.title, "Foo Doc")
        self.assertEqual(document.collection, collection)

    def test_make_document_exists(self):
        root_collection = Collection.get_first_root_node()
        collection = root_collection.add_child(name="Custom Collection")
        with tempfile.TemporaryFile() as f:
            f.write(b"content")
            doc = Document(
                title="Foo Doc",
                file=File(f, name="foo-doc.eps"),
            )
            doc.save()
        self.assertEqual(Document.objects.count(), 1)
        instance = WagtailQrCode(self.test_page, collection=collection)
        qrc = pyqrcode.create("foo string")
        eps = io.StringIO()
        qrc.eps(eps, scale=3, quiet_zone=3)
        new_document = instance.make_document("Foo Doc", eps, collection)
        self.assertEqual(Document.objects.count(), 2)
        self.assertNotEqual(new_document.pk, doc.pk)
        self.assertTrue(Document.objects.filter(pk=doc.pk).exists())

    def test_make_document_not_exists(self):
        root_collection = Collection.get_first_root_node()
        collection = root_collection.add_child(name="Custom Collection")
        with tempfile.TemporaryFile() as f:
            f.write(b"content")
            doc = Document(
                title="Foo Doc",
                file=File(f, name="foo-doc.eps"),
                collection=collection,
            )
            doc.save()
        self.assertEqual(Document.objects.count(), 1)

        instance = WagtailQrCode(self.test_page, collection=collection)
        qrc = pyqrcode.create("foo string")
        eps = io.StringIO()
        qrc.eps(eps, scale=3, quiet_zone=3)
        instance.make_document("Bar Doc", eps, collection)
        self.assertEqual(Document.objects.count(), 2)

    def test_build(self):
        collection = create_collection("Foo Collection")
        instance = WagtailQrCode(self.test_page, collection)
        svg, document = instance.build()
        self.assertIsInstance(svg, str)
        self.assertIsInstance(document, Document)

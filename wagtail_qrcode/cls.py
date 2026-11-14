import io

import pyqrcode
from django.conf import settings
from django.core.files.base import File
from wagtail.documents import get_document_model
from wagtail.images import get_image_model
from wagtail.models import Collection

Document = get_document_model()
Image = get_image_model()


class WagtailQrCode:
    def __init__(self, page, collection=None):
        self.page = page
        # self.content = content
        self.collection = collection

        self.settings = self.settings()

    def settings(self):
        if hasattr(settings, "WAGTAIL_QR_CODE"):
            return settings.WAGTAIL_QR_CODE
        else:
            return {
                "collection_name": "QR Codes",
                "scale": 3,
                "quiet_zone": 6,
                "svg_has_xml_declaration": False,
                "svg_has_doc_type_declaration": False,
            }

    def build(self):
        title = self.page.title

        try:
            base_url = settings.WAGTAIL_QR_CODE_BASE_URL
        except AttributeError:
            base_url = settings.WAGTAILADMIN_BASE_URL

        # QR Code instance
        qrc = self.make_qr_code(f"{base_url}/qr-code?id={self.page.id}")

        # SVG QR code
        svg = self.make_svg(qrc)

        # EPS QR code and save a document
        eps = self.make_eps(qrc)
        document = self.make_document(title, eps, self.collection)

        return svg, document

    def make_qr_code(self, content):
        qrc = pyqrcode.create(content)
        return qrc

    def make_svg(self, qrc):
        svg_io = io.BytesIO()
        qrc.svg(
            svg_io,
            scale=self.settings["scale"],
            quiet_zone=self.settings["quiet_zone"],
            xmldecl=self.settings["svg_has_xml_declaration"],
            svgns=self.settings["svg_has_doc_type_declaration"],
            title=self.page.title,
        )
        svg_io = svg_io.getvalue().decode()

        return svg_io

    def make_eps(self, qrc):
        eps_io = io.StringIO()
        qrc.eps(
            eps_io,
            scale=self.settings["scale"],
            quiet_zone=self.settings["quiet_zone"],
        )

        return eps_io

    def make_document(self, title, eps, collection):
        # Existing documents can still be referenced by live pages or revisions.
        doc = Document(
            title=title,
            file=File(eps, name=f"qr-code-{self.page.id}.eps"),
            collection=collection,
        )
        doc.save()

        return doc


def create_collection(name):
    """Create a collection for the QR codes."""

    try:
        collection = Collection.objects.get(name=name)
    except Collection.DoesNotExist:
        root_collection = Collection.get_first_root_node()
        collection = root_collection.add_child(name=name)

    return collection

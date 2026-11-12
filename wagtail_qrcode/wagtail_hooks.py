from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from wagtail import hooks
from wagtail.documents import get_document_model

from wagtail_qrcode.admin_forms import QrCodeEmailFieldsForm, QrCodeEmailForm
from wagtail_qrcode.cls import WagtailQrCode, create_collection
from wagtail_qrcode.models import QRCodeMixin


@hooks.register("after_create_page")
@hooks.register("after_edit_page")
@transaction.atomic
def generate_qr_code(request, page):
    """Add QR assets to the saved revision without changing its publication state."""

    # Wagtail uses the JSON save flow for autosave, including page creation.
    if not is_qrcode_instance(page) or not request.accepts("text/html"):
        return

    revision = page.get_latest_revision()
    collection = create_collection("QR Codes")
    svg, document = WagtailQrCode(revision.as_object(), collection).build()
    page.qr_code_svg = svg
    page.qr_code_eps = document

    # Wagtail has already saved (and possibly published or scheduled) this revision.
    # Enrich it rather than saving another revision or publishing draft content.
    revision.content.update(qr_code_svg=svg, qr_code_eps=document.pk)
    revision.save(update_fields=["content"])

    # Workflow approval may publish through a different page instance. Refresh
    # only publication state so draft field values on this instance are preserved.
    page.refresh_from_db(fields=["live", "live_revision"])

    # Live rows must retain their published QR assets when editing a draft.
    if not page.live or page.live_revision_id == revision.pk:
        type(page).objects.filter(pk=page.pk).update(
            qr_code_svg=svg, qr_code_eps=document
        )

    if request.method == "POST" and issubclass(
        page.get_edit_handler().get_form_class(), QrCodeEmailForm
    ):
        email_form = QrCodeEmailFieldsForm(request.POST)
        if email_form.is_valid() and email_form.cleaned_data["email_address"]:
            send_qr_code_email(
                page,
                email=email_form.cleaned_data["email_address"],
                subject=email_form.cleaned_data["email_subject"],
                body=email_form.cleaned_data["email_body"],
            )


def send_qr_code_email(page, email=None, subject=None, body=None):
    """Send the QR code to the email address."""
    doc = page.qr_code_eps
    if doc is None or email is None:
        return

    if subject is None:
        subject = f"QR Code for {page.title}"
    if body is None:
        body = f"QR Code for {page.title}"

    with doc.file.open("rb") as eps:
        attachment = eps.read()

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
        attachments=[("qr-code-{}.eps".format(page.id), attachment, "image/eps")],
    )

    def send():
        try:
            email.send()
        except Exception as e:
            print(e)

    transaction.on_commit(send)


@hooks.register("after_delete_page")
def delete_document(request, page):
    if is_qrcode_instance(page) and page.qr_code_eps:
        doc = get_document_model().objects.filter(id=page.qr_code_eps.id)
        if doc:
            doc.delete()


def is_qrcode_instance(page):
    """Check if the page is a QR code page and inherits from the QRCodeMixin"""
    return isinstance(page, QRCodeMixin)

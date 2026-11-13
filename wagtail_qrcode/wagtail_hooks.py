from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.urls import include, path
from wagtail import hooks

from wagtail_qrcode.admin_forms import QrCodeEmailFieldsForm, QrCodeEmailForm
from wagtail_qrcode.cls import WagtailQrCode
from wagtail_qrcode.models import QRCodeMixin
from wagtail_qrcode.views import qr_code_download, qr_code_preview


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        path(
            "qr-codes/",
            include(
                (
                    [
                        path("<int:page_id>/preview/", qr_code_preview, name="preview"),
                        path(
                            "<int:page_id>/download/<str:file_format>/",
                            qr_code_download,
                            name="download",
                        ),
                    ],
                    "wagtail_qrcode_admin",
                )
            ),
        )
    ]


@hooks.register("after_create_page")
@hooks.register("after_edit_page")
def email_qr_code(request, page):
    """Handle explicit editor email requests without changing saved content."""
    if (
        request.method != "POST"
        or not request.accepts("text/html")
        or not isinstance(page, QRCodeMixin)
        or not issubclass(page.get_edit_handler().get_form_class(), QrCodeEmailForm)
    ):
        return
    email_form = QrCodeEmailFieldsForm(request.POST)
    if email_form.is_valid() and email_form.cleaned_data["email_address"]:
        send_qr_code_email(
            page,
            email=email_form.cleaned_data["email_address"],
            subject=email_form.cleaned_data["email_subject"],
            body=email_form.cleaned_data["email_body"],
        )


def send_qr_code_email(page, email=None, subject=None, body=None):
    """Render an EPS attachment in memory and send it after commit."""
    if email is None:
        return
    message = EmailMessage(
        subject=subject if subject is not None else f"QR Code for {page.title}",
        body=body if body is not None else f"QR Code for {page.title}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
        attachments=[
            (
                f"qr-code-{page.pk}.eps",
                WagtailQrCode(page).render("eps"),
                "application/postscript",
            )
        ],
    )
    transaction.on_commit(message.send, robust=True)

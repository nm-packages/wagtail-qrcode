from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.urls import include, path
from wagtail import hooks

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


@hooks.register("before_publish_page")
def preserve_qr_code_email(request, page):
    # Publishing reloads the page before the after-edit hook runs.
    email_data = page.__dict__.pop("_qr_code_email", None)
    if email_data is not None:
        request._qr_code_email = {page.pk: email_data}


@hooks.register("after_create_page")
@hooks.register("after_edit_page")
def email_qr_code(request, page):
    """Handle explicit editor email requests without changing saved content."""
    published_email_data = request.__dict__.pop("_qr_code_email", {})
    email_data = page.__dict__.pop("_qr_code_email", None) or published_email_data.get(
        page.pk
    )
    if (
        request.method != "POST"
        or not request.accepts("text/html")
        or not isinstance(page, QRCodeMixin)
        or not email_data
        or not email_data["email"]
    ):
        return
    send_qr_code_email(page, **email_data)


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

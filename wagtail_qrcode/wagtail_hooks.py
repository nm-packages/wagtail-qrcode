from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.urls import include, path, reverse
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.widgets import Button

from wagtail_qrcode.cls import WagtailQrCode
from wagtail_qrcode.email import get_email_defaults
from wagtail_qrcode.models import QRCodeMixin
from wagtail_qrcode.views import qr_code_download, qr_code_preview, qr_code_reset


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        path(
            "qr-codes/",
            include(
                (
                    [
                        path("<int:page_id>/preview/", qr_code_preview, name="preview"),
                        path("<int:page_id>/reset/", qr_code_reset, name="reset"),
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


@hooks.register("register_page_header_buttons")
def alias_qr_code_buttons(page, user, view_name, next_url=None):
    if (
        not page.alias_of_id
        or not issubclass(page.specific_class, QRCodeMixin)
        or not page.permissions_for_user(user).can_edit()
    ):
        return
    yield Button(
        _("Preview QR code"),
        reverse("wagtail_qrcode_admin:preview", args=[page.pk]),
        icon_name="image",
        priority=80,
    )
    for priority, file_format in enumerate(("svg", "eps"), start=81):
        yield Button(
            _("Download QR SVG") if file_format == "svg" else _("Download QR EPS"),
            reverse("wagtail_qrcode_admin:download", args=[page.pk, file_format]),
            icon_name="download",
            priority=priority,
        )


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
    defaults = get_email_defaults()
    message = EmailMessage(
        subject=subject if subject is not None else defaults["email_subject"],
        body=body if body is not None else defaults["email_body"],
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

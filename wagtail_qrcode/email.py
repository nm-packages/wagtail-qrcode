from django.conf import settings


def get_email_defaults():
    """Read shared editor and sender defaults from the current site settings."""
    return {
        "email_subject": getattr(
            settings, "WAGTAIL_QRCODE_EMAIL_SUBJECT", "Your QR code"
        ),
        "email_body": getattr(
            settings,
            "WAGTAIL_QRCODE_EMAIL_BODY",
            "Please find your QR code attached as an EPS file.",
        ),
    }

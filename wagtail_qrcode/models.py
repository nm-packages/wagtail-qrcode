from django.db import models

from wagtail_qrcode.field_panels import QrCodePanel


class QRCode(models.Model):
    """Page-owned scan statistics, independent of page revisions and QR output."""

    page = models.OneToOneField(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="qr_code_record",
    )
    usage_count = models.PositiveBigIntegerField(default=0, editable=False)


class QRCodeMixin(models.Model):
    GENERATE_QR_CODE = True

    class Meta:
        abstract = True

    panels = [QrCodePanel(heading="QR code")]

    @property
    def qr_code_usage(self):
        if not self.pk:
            return 0
        return (
            QRCode.objects.filter(page_id=self.pk)
            .values_list("usage_count", flat=True)
            .first()
            or 0
        )

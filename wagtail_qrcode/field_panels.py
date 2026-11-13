from django.urls import reverse
from wagtail.admin.panels import Panel


class QrCodePanel(Panel):
    """Read-only QR preview, downloads and scan count for a saved page."""

    class BoundPanel(Panel.BoundPanel):
        template_name = "wagtail_qrcode/admin/qr_code_panel.html"

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            if self.instance.pk:
                context.update(
                    preview_url=reverse(
                        "wagtail_qrcode_admin:preview", args=[self.instance.pk]
                    ),
                    svg_url=reverse(
                        "wagtail_qrcode_admin:download", args=[self.instance.pk, "svg"]
                    ),
                    eps_url=reverse(
                        "wagtail_qrcode_admin:download", args=[self.instance.pk, "eps"]
                    ),
                    usage_count=self.instance.qr_code_usage,
                )
            return context

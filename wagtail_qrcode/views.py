from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.http import content_disposition_header
from django.utils.translation import ngettext
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST
from wagtail.models import Page

from wagtail_qrcode.cls import WagtailQrCode
from wagtail_qrcode.models import QRCode, QRCodeMixin


@never_cache
@require_GET
@transaction.atomic
def qr_code_page_view(request):
    """Resolve a scanned page ID and atomically record a successful redirect."""
    try:
        page_id = int(request.GET.get("id", ""))
    except ValueError:
        raise Http404("Page not found") from None
    # Avoid out-of-range integers reaching the database backend.
    if not 0 < page_id <= 9223372036854775807:
        raise Http404("Page not found")
    page = get_object_or_404(Page.objects.live(), pk=page_id).specific
    if not isinstance(page, QRCodeMixin):
        raise Http404("Page not found")
    # Destination serving retains Wagtail's private-page access controls.
    url = page.get_url(request)
    if not url:
        raise Http404("Page not found")
    record, _ = QRCode.objects.get_or_create(page_id=page.pk)
    QRCode.objects.filter(pk=record.pk).update(usage_count=F("usage_count") + 1)
    return HttpResponseRedirect(url)


def editable_qr_page(request, page_id):
    page = get_object_or_404(Page, pk=page_id).specific
    if not isinstance(page, QRCodeMixin):
        raise Http404("Page not found")
    if not page.permissions_for_user(request.user).can_edit():
        raise PermissionDenied
    return page


@never_cache
@require_GET
def qr_code_download(request, page_id, file_format):
    page = editable_qr_page(request, page_id)
    if file_format not in ("svg", "eps"):
        raise Http404("Unsupported QR code format")
    response = render_qr_response(page, file_format)
    response["Content-Disposition"] = content_disposition_header(
        True, f"qr-code-{page.pk}.{file_format}"
    )
    return response


@never_cache
@require_GET
def qr_code_preview(request, page_id):
    return render_qr_response(editable_qr_page(request, page_id), "svg")


@never_cache
@require_POST
def qr_code_reset(request, page_id):
    """Reset page-owned statistics without saving revisioned page content."""
    page = editable_qr_page(request, page_id)
    QRCode.objects.filter(page_id=page.pk).update(usage_count=0)
    return JsonResponse(
        {
            "usage_count": 0,
            "count_label": ngettext("%(count)s scan", "%(count)s scans", 0)
            % {"count": 0},
        }
    )


def render_qr_response(page, file_format):
    content_type = "image/svg+xml" if file_format == "svg" else "application/postscript"
    response = HttpResponse(
        WagtailQrCode(page).render(file_format), content_type=content_type
    )
    response["X-Content-Type-Options"] = "nosniff"
    return response

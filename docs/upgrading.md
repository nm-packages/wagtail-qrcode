# Upgrade from 2.1.1

This guide covers upgrading from wagtail-qrcode 2.1.1 to the release described
under [Unreleased](../CHANGELOG.md#unreleased). It changes QR storage, scan
counting and the editor controls. Upgrading the dependency alone is not enough.

Existing printed codes can keep working. Keep their domain, scan route and page
IDs available; the move away from stored QR files does not require reprinting.

## Prepare a copy of your site

Back up the database and media, and rehearse the upgrade on a restored copy.
Keep the old application code and dependency lock so you can restore a matching
application and database if needed.

Choose a [supported framework combination](../README.md#installation).
Plan any Python, Django and Wagtail upgrades alongside this package change,
following the frameworks' intermediate upgrade instructions. Do not assume
2.1.1 works with every framework version supported by the new package.

The package currently uses `wagtail.models.Page`. Sites using Wagtail 8 custom
base page models need to adapt the scan view and counter relation before using
the package with those models.

Before changing anything, record:

- Every page model that uses `QRCodeMixin`, with sample page IDs and scan counts.
- The exact URLs encoded by existing codes, preferably from printed material.
- Custom templates, panels, forms and Python code that access the old QR fields.
- Links to existing EPS documents that your site still needs to serve.

## Keep printed codes working

Version 2.1.1 generated URLs such as `https://example.com/qr-code?id=123`.
With the standard route, new output uses `https://example.com/qr-code/?id=123`.
Both can reach the same scan view and page.

Keep the old address explicitly routed, rather than depending on Django's
trailing-slash redirect. For the standard configuration, put these routes before
Wagtail's page-serving routes:

```python
from django.urls import include, path

from wagtail_qrcode.views import qr_code_page_view

urlpatterns = [
    path("qr-code", qr_code_page_view),
    path("qr-code/", include("wagtail_qrcode.urls")),
    # ... Wagtail routes
]
```

The included route supplies the name `qr_code_page_view`, which new QR generation
uses. If you wire the view directly, give the route for new codes that name;
the old README's `qr-code-view` name is no longer sufficient.

Adapt the compatibility route to the URLs your codes actually contain. Keep
the old domain reachable if you change domains, and preserve the `id` query
parameter through any redirects. Updating `WAGTAIL_QR_CODE_BASE_URL` only changes
new output. It cannot change an already printed code.

Keep existing page IDs during the upgrade. Deleting and recreating pages, or
importing them with different IDs, can break their printed codes. Old codes on
copies or aliases retain whichever page ID they originally encoded; new codes
use each copy or alias's own ID.

## Update your application code

Install the new package version in your development environment using your
project's dependency manager, then update custom integrations:

| Previous integration | Replacement |
| --- | --- |
| Stored `page.qr_code_svg` | Use the `qr_code_svg` template tag |
| Stored `page.qr_code_eps` document | Use the editor downloads or `WagtailQrCode(page).render("eps")` |
| Assigning to or querying the `qr_code_usage` field | Read the `page.qr_code_usage` property; query the new `QRCode` model for stored counts |
| `QrCodeFieldPanel` and `QrCodeUsageFieldPanel` | Use `QRCodeMixin.panels` |
| `WagtailQrCode(page, collection).build()` | Use `WagtailQrCode(page).render("svg")` or `.render("eps")`; both return bytes |
| `create_collection()` or `make_document()` | Remove calls; QR generation no longer creates Documents |

For a template preview:

```html
{% load wagtail_qrcode_tags %}
{% qr_code_svg page %}
```

Keep `QRCodeMixin` on your page models. Follow the [page-model example](../README.md#page-model)
for editor panels and email fields, preserving your own content panels and form
customisations. Remove custom panels that reference the old database fields.

Remove `collection_name` and `svg_has_doc_type_declaration` from
`WAGTAIL_QR_CODE`. SVG output always includes its namespace. Other rendering
options and the QR base URL remain configurable.

Email is now sent after an explicit editor save commits, rather than from the
form's `save()` method. Review custom code that relied on calling that method
to send email. Autosave sends nothing, and the recipient is not retained.
Subject and body defaults are described in [configuration](../README.md#configuration).

## Preserve counts before removing fields

The old mixin added three fields to your site's page tables:
`qr_code_svg`, `qr_code_eps` and `qr_code_usage`. The new package migration
creates a separate counter table; it does not copy values from your page tables.
Removing `qr_code_usage` without copying it first discards the historical count.

Create migrations in your own app, in this order:

1. Copy the old counts into `wagtail_qrcode.QRCode` using a data migration that
   depends on the package's `0001_initial` migration.
2. Remove the three old fields in a subsequent schema migration.

Use the current values in the page tables as the source. Counts embedded in old
revisions may be stale. The migration should cover drafts and unpublished pages
as well as live pages.

The following example assumes an app called `blog`, a concrete `QRCodePage`
model and an existing migration called `0041_previous`. Replace those names
with your own. Run commands through your site's environment; these examples
use uv.

First create an empty migration:

```bash
uv run python manage.py makemigrations --empty blog --name preserve_qr_scan_counts
```

Put this code in the new file, retaining the correct dependency on your app's
previous migration:

```python
from django.db import migrations


def copy_scan_counts(apps, schema_editor):
    Page = apps.get_model("blog", "QRCodePage")
    Counter = apps.get_model("wagtail_qrcode", "QRCode")
    database = schema_editor.connection.alias
    pages = Page.objects.using(database).values_list("pk", "qr_code_usage")

    for page_id, count in pages.iterator():
        if count < 0:
            raise RuntimeError(f"Negative QR count for page {page_id}")
        record, created = Counter.objects.using(database).get_or_create(
            page_id=page_id,
            defaults={"usage_count": count},
        )
        if not created and record.usage_count != count:
            raise RuntimeError(f"Conflicting QR count for page {page_id}")


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0041_previous"),
        ("wagtail_qrcode", "0001_initial"),
    ]

    operations = [migrations.RunPython(copy_scan_counts)]
```

Use [historical models](https://docs.djangoproject.com/en/5.2/topics/migrations/#historical-models)
from `apps.get_model()`, as above. Importing your current page model would give
you the new property instead of the old database field.

Adapt the copy step for every table that owns the old fields. If page types
inherit them from a shared concrete parent, copy from that parent once. For
models in different apps, add the corresponding migration dependencies. The
example stops on negative or conflicting counts so you can investigate instead
of overwriting them.

Then generate the field-removal migration:

```bash
uv run python manage.py makemigrations blog
uv run python manage.py migrate --plan
```

Check that the generated migration depends on your copy migration and removes
the three old fields. Repeat for other affected apps. Do not rewrite migrations
that have already been applied.

During deployment, pause scans, editor saves and background writes until all
migrations finish. Otherwise counts could change after being copied. Run
`uv run python manage.py migrate` before starting the new application processes.

The example deliberately has no reverse operation. Reversing field removal
does not recover the deleted data; plan rollback by restoring the matching
database backup and old application.

## Keep existing documents and revisions

Removing `qr_code_eps` removes a reference, not the EPS document or its file.
Keep existing documents and the QR collection while checking whether templates,
downloads or external links still use them. New QR output does not need them.
Do any cleanup separately after checking those references.

Existing revision JSON is not rewritten by these migrations. Test previewing,
restoring and publishing representative old revisions, including custom page
fields. After the upgrade, restoring a revision should leave the separate scan
count unchanged.

## Verify the upgrade before deploying

On your restored site copy, check that:

- A code printed before the upgrade still reaches the correct live page and
  adds exactly one scan. Try both `/qr-code?id=...` and `/qr-code/?id=...`.
- Page IDs and copied counts match your records for every affected page type.
- Existing drafts remain drafts, and public pages retain their published content.
- Previewing, restoring and publishing an old revision works without resetting
  counts or changing the code's page ID.
- SVG/EPS previews and downloads work, and a test email is sent only after an
  explicit save. Use a test mail backend when rehearsing.
- Existing document links still work, and users without page edit permission
  cannot download codes or reset counts through the new admin controls.

Only live QR pages now redirect. Unpublished, missing and non-QR page IDs return
404. Private live pages still enforce access at the destination. Include these
cases in your site's tests if custom integrations depended on earlier behaviour.

Commit the application changes and reviewed migrations together, then deploy
the same changes you rehearsed. The [smoke tests](smoke-tests.md) provide further
editor checks, but a fresh sandbox does not replace testing your existing data.

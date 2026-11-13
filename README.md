# Wagtail QR code

Add QR codes to Wagtail pages with an editor preview, printable EPS downloads,
usage counts and optional email attachments.

![Wagtail's QR Code editor tab showing an SVG preview, usage count, EPS document and email fields](docs/sample.png?raw=true)

## Features

- Preview a generated SVG in the page editor and download an EPS for printed materials.
- Link scans to a page through its ID, so printed QR codes continue to work when its slug changes.
- Track requests to the QR redirect with a usage count.
- Email the newly generated EPS to a one-time recipient when saving a draft or publishing.

## Installation

### Compatibility

Python 3.11–3.15, Django 5.2 LTS–6.1 and Wagtail 7.4 LTS–8.1 are supported in
compatible combinations. We support Python releases that have not reached end
of life, and framework releases from the preceding LTS through the latest
stable release. See the
[tested combinations and upgrade notes](docs/platform-upgrade.md) before
choosing versions; newer frameworks require newer Python versions.

To add the package to an existing Wagtail project:

**Install the package into your environment.**

```bash
pip install wagtail-qrcode
```

**Add the package to `INSTALLED_APPS` in your site settings.**

```python
INSTALLED_APPS = [
    # ...
    "wagtail_qrcode",
    # ...
]
```

**Set the public base URL used in generated QR codes.**

Use a full HTTP or HTTPS URL, including the scheme and without a trailing slash:

```python
WAGTAIL_QR_CODE_BASE_URL = "https://example.com"
```

The URL must be reachable from the device scanning the code. Localhost works
for testing on the same computer; another device needs a reachable LAN address
or tunnel. See the [sandbox device configuration guide](docs/sandbox.md#configuration-and-another-device)
for local testing. Changing the base URL requires regenerating QR assets;
previous downloads still encode the old URL.

## Using the QR code page model mixin

Add `QRCodeMixin` to a new or existing page model. This example includes the
optional email fields; configure your project's Django email backend and
`DEFAULT_FROM_EMAIL` before using them. The sandbox captures email locally for
inspection without external delivery.

```python
# models.py

from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.models import Page

from wagtail_qrcode.admin_forms import QrCodeEmailForm
from wagtail_qrcode.models import QRCodeMixin


class QRCodePage(QRCodeMixin, Page):
    qrcode_panels = QRCodeMixin.panels + [
        MultiFieldPanel(
            [
                FieldPanel("email_address"),
                FieldPanel("email_subject"),
                FieldPanel("email_body"),
            ],
            heading="Send QR code via email",
        )
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(Page.content_panels, heading="Content"),
            ObjectList(Page.promote_panels, heading="Promote"),
            ObjectList(Page.settings_panels, heading="Settings", classname="settings"),
            ObjectList(qrcode_panels, heading="QR Code", classname="qr-code"),
        ]
    )

    base_form_class = QrCodeEmailForm
```

The **QR Code** editor tab shows the SVG preview, usage count and downloadable
EPS document. Generated EPS files are also available in Wagtail's Documents area.

Choose **Save draft** or **Publish** to generate or update the QR code. To email
the EPS file, fill in the recipient, subject and body before choosing either
action. The email uses the newly generated file and is sent after the save
transaction commits. Autosave only saves draft content; it does not generate
QR files, publish edits or send emails.

Saving a draft of a live page keeps its published content and QR files unchanged.
New EPS documents are retained alongside older files so that published pages
and saved revisions can continue to use their original documents.

Published page aliases, including chained aliases, receive the source page's
updated QR assets. Draft and scheduled edits leave aliases unchanged until
publication.

### Without email fields

In the example above, set `qrcode_panels = QRCodeMixin.panels` and omit
`base_form_class = QrCodeEmailForm`. Remove the unused `QrCodeEmailForm`,
`FieldPanel` and `MultiFieldPanel` imports. Keep the same `edit_handler` to retain
the QR Code tab with its preview, usage count and EPS document.

### Create and apply migrations

After adding `QRCodeMixin` to a page model, create and apply migrations for the
app containing that model. Replace `your_app` with its Django app label:

```bash
python manage.py makemigrations your_app
python manage.py migrate
```

This creates the database fields for the SVG, EPS document reference and usage
count.

## URLs

Register the QR redirect in your project's URL configuration before Wagtail's
catch-all page route (`wagtail_urls`).

The generator encodes `BASE_URL/qr-code?id=PAGE_ID`. Register the endpoint
without a trailing slash so scans resolve directly, without relying on Django's
automatic slash redirect.

```python
from django.urls import include, path

urlpatterns = [
    # ...
    path("qr-code", include("wagtail_qrcode.urls")),
    # ...
]
```

Alternatively, register the view directly:

```python
from django.urls import path

from wagtail_qrcode.views import qr_code_page_view

urlpatterns = [
    # ...
    path("qr-code", qr_code_page_view, name="qr_code_page_view"),
    # ...
]
```

## Configuration

QR appearance settings are optional. If you define `WAGTAIL_QR_CODE`, supply
all four keys below: the dictionary replaces the defaults rather than merging
with them. For example, setting only `{"scale": 4}` causes generation to fail
because the remaining keys are missing.

These are the default values:

```python
WAGTAIL_QR_CODE = {
    "scale": 3,
    "quiet_zone": 6,
    "svg_has_xml_declaration": False,
    "svg_has_doc_type_declaration": False,
}
```

Generated EPS documents are stored in the **QR Codes** collection, which is
created automatically. The collection name is currently fixed; setting
`collection_name` does not change it.

- `scale`: the size of each QR code module (dot).
- `quiet_zone`: the border width around the QR code, measured in modules.
- `svg_has_xml_declaration`: includes an XML declaration in the SVG.
- `svg_has_doc_type_declaration`: includes the SVG namespace (`xmlns="http://www.w3.org/2000/svg"`); despite its name, this does not add a doctype declaration.

## Local demonstration

Run `uv sync --locked`, `make sandbox-setup` and `make sandbox-run` to explore
this checkout at <http://localhost:8000/> (local admin login: `admin` / `admin`).
See the [sandbox setup guide](docs/sandbox.md) and
[developer smoke tests](docs/smoke-tests.md) for downloads, email, draft saves,
autosave, persistence and optional device testing.

## Contributing

See the [contributor guide](docs/contrubute.md) for development setup, testing
and contribution instructions.

Create working branches from `main` and target pull requests at `main`.
Prepare and tag package releases from `main`.
See the [branch workflow](docs/contrubute.md#branches-and-pull-requests) for details.

## Issues

Report bugs and suggest improvements in the
[issue tracker](https://github.com/nm-packages/wagtail-qrcode/issues).

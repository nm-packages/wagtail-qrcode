# Wagtail QR code

This package can be used to create a page in Wagtail CMS that has a corresponding QR Code.

![Alt text](docs/sample.png?raw=true "Title")

## Features

- Generate QR previews and SVG/EPS downloads on demand, without storing files or using Wagtail Documents.
- Scan a URL containing the page ID to reach its current location, even after a title, slug or parent change.
- Track successful scan redirects in a separate page-owned record, outside page revisions.
- Email a generated EPS attachment on an explicit draft save or publication.
- Give copies, translations and aliases their own QR identity based on their page ID.

## Installation

### Compatibility

Python 3.11–3.15, Django 5.2 LTS–6.1 and Wagtail 7.4 LTS–8.1 are supported in
compatible combinations. We support Python releases that have not reached end
of life, and framework releases from the preceding LTS through the latest
stable release. See the
[tested combinations and upgrade notes](docs/platform-upgrade.md) before
choosing versions; newer frameworks require newer Python versions.

To add the package to your own Wagtail CMS

**Install the package into your environment.**

```bash
pip install wagtail-qrcode
```

**Add the package to your site settings.**

```python
INSTALLED_APPS = [
    # ...
    "wagtail_qrcode",
    # ...
]
```

**Create the database tables.**

```bash
python manage.py migrate
```

The package owns a scan-counter table with a one-to-one relationship to Wagtail's
base Page. A row is created on the first successful scan; previewing, downloading
and emailing do not create records.

**Add this setting to your Wagtail settings.**

It is used to generate the base url for the QR code

```python
WAGTAIL_QR_CODE_BASE_URL = "https://example.com"
```

You'll likely want to test the QRcode using another device. Your device will need to be able to resolve your testing domain and localhost probably won't work.

Try using a service like [ngrok](https://ngrok.com/) to set up a url to your localhost and use that domain name as in the `WAGTAIL_QR_CODE_BASE_URL` setting.

This is the command I use to start ngrok.

```bash
./ngrok http 8000 --scheme=http
```

## Using the QRCode page model mixin

Use the model mixin in a new or an existing page model.

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

This adds a `QR Code` tab with a read-only preview, **Download SVG** and
**Download EPS** buttons, and the scan count. Save a new page first so that it has
an ID. No document chooser or generated asset fields are needed on the page.
Downloads and previews require Wagtail admin access and permission to edit that
page, including for unpublished pages.

Editors with permission to edit the page can choose **Reset scan count** beside
the count and confirm to reset it to zero. The button is disabled at zero.
Resetting takes effect immediately and preserves unsaved editor input; it does
not save or publish the page or send email. It cannot be undone by restoring a
revision. Subsequent scans start counting again from zero.

To email an EPS, fill in the recipient, subject and body before choosing **Save
draft** or **Publish**. The attachment is rendered in memory and sent after the
save transaction commits. Autosave does not send email, and later workflow
approval or scheduled publication does not repeat an earlier email request.

Changing page content does not create or synchronise QR assets. Drafts and
revisions use the same page identity; restoring a revision does not reset scan
counts. Each copy, translation and alias uses its own page ID, including chained
aliases. Deleting a page removes its counter record and leaves no QR files to
clean up.

This design is for new QR usage. Importing existing QR documents, counters or
legacy revisions is outside the current implementation. Host page models that
used the old mixin fields need schema migrations when those fields are removed;
no legacy data conversion is provided.

### If you don't need to be able to send the qrcode via email your page model can be

```python
# models.py

from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.models import Page

from wagtail_qrcode.models import QRCodeMixin


class QRCodePage(QRCodeMixin, Page):
    qrcode_panels = QRCodeMixin.panels

    edit_handler = TabbedInterface(
        [
            ObjectList(Page.content_panels, heading="Content"),
            ObjectList(Page.promote_panels, heading="Promote"),
            ObjectList(Page.settings_panels, heading="Settings", classname="settings"),
            ObjectList(qrcode_panels, heading="QR Code", classname="qr-code"),
        ]
    )
```

## URLS

Include the wagtail-qrcode urls in your site urls before `wagtail_urls`.

The url provides the redirect endpoint when the qr-code is scanned and viewed in a browser.

```python
urlpatterns = [
    # ...
    path("qr-code/", include("wagtail_qrcode.urls")),
    # ...
]
```

The named `qr_code_page_view` route is used when generating the QR payload, so a
custom mount path is supported. If wiring the view directly, use that same name.
For the example above, the payload is `https://example.com/qr-code/?id=123`.
The base URL falls back to `WAGTAILADMIN_BASE_URL` if no QR base URL is set.

The scan endpoint redirects only live, QR-enabled pages. Private-page access is
still enforced by Wagtail when the destination is opened. The counter measures
redirects, including redirects to a private page's access prompt; it is not a
count of unique visitors or confirmed content views. Invalid IDs and unpublished
or non-QR pages return 404 without increasing a count.

Keep the scan domain and route reachable after printing. Newly generated codes
use the current base URL; configuration changes do not change paper copies.
Page IDs are stable within a database, but an export/import that remaps IDs does
not preserve them automatically.

### Optional public preview

To render a QR directly in a page template:

```html
{% load wagtail_qrcode_tags %}
{% qr_code_svg page %}
```

This renders SVG in memory and does not require a document or an admin download
URL. It produces no output for an unsaved page. QR generation in Python uses
`WagtailQrCode(page).render("svg")` or `.render("eps")`, returning bytes.

## Configuration

Set the configuration (optional, these are the defaults)

```python
WAGTAIL_QR_CODE = {
    "scale": 3,
    "quiet_zone": 6,
    "svg_has_xml_declaration": False,
}
```

- scale: the size of the dots in the QR code
- quiet_zone: the plain border around the QR code
- svg_has_xml_declaration: does the QR code SVG have an XML declaration

SVG output always includes the XML namespace needed for standalone images. The
old `collection_name` and `svg_has_doc_type_declaration` options are removed.
Rendering settings apply to the next preview, download or email; generated output
is not archived.

## Local demonstration

Run `uv sync --locked`, `make sandbox-setup` and `make sandbox-run` to explore
this checkout at <http://localhost:8000/> (initial admin login: `admin` / `admin`).
The persistent sandbox has published and draft examples using on-demand QR
previews, SVG/EPS downloads and page-owned scan counts, without QR Documents.
See the [sandbox guide](docs/sandbox.md) and [smoke tests](docs/smoke-tests.md)
for email capture, test isolation, copies, aliases and device testing.

## Contributing

If you would like to suggest an improvement to the package [contributions](docs/contrubute.md) are welcome

Create working branches from `main` and target pull requests at `main`.
Prepare and tag package releases from `main`.
See the [branch workflow](docs/contrubute.md#branches-and-pull-requests) for details.

## Issues

If you find an issue please consider [raising and issue](https://github.com/nickmoreton/wagtail-qrcode/issues)

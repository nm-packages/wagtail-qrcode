# Local QR code sandbox

The Wagtail project in `sandbox/` is a persistent manual testing site for this
checkout. Its examples use the same in-memory QR renderer as the package: setup,
page saves, previews and downloads create no QR files or Documents.

This is a development site with a known password, intended for your own machine.
It runs with the locked contributor dependencies installed by `just sync`.
The package's framework compatibility matrix is tested separately with tox.

## Install, set up and start

Install Python 3.11 or newer, uv 0.12.10 or newer and Just 1.59.0 or newer
(see [contributor setup](contrubute.md#install-uv-and-just-then-sync-dependencies)).
From the repository root:

```bash
just sync
just sandbox-setup
just sandbox-run
```

Open <http://localhost:8000/> and <http://localhost:8000/admin/>.
The initial local login is **admin / admin**. Setup applies migrations, configures
the Wagtail Site for localhost on port 8000, and creates:

- **Published QR example — scan and download**: listed on the homepage, with a
  generated SVG preview and authenticated SVG/EPS downloads in its editor.
- **Draft QR example — save and preview**: available in admin and Preview, with
  authenticated downloads; its public page and scan URL return 404 until published.

`uv sync` installs the checkout in editable mode. The server reloads Python
changes; restart after changing settings and run setup after adding migrations.

The sandbox uses Django's development server through `sandbox/manage.py`, with
no standalone WSGI entrypoint. It includes the Wagtail admin and QR examples;
public search, Documents, Django admin, form builder, URL-history redirects,
embeds and snippets are omitted. QR scan redirects continue to use the package's
page-ID endpoint, including after a page's slug changes.
`wagtail.search` remains installed for Wagtail's built-in admin search.

Repeat `just sandbox-setup` whenever necessary. It preserves existing users,
passwords, titles, slugs, revisions and scan counts. Missing examples are
recreated without overwriting other pages with the same slug. Copies and aliases
have their own page-ID codes and do not duplicate the setup identity markers.
Setup updates the Site's hostname and port to match the configured base URL.

No QR asset regeneration is necessary after changing settings. The next preview,
download or email uses the current configuration. Previous downloads and printed
copies retain their original payload.

Follow the [developer smoke tests](smoke-tests.md) to check the editor, downloads,
redirects, counters, draft isolation, autosave, copies, aliases and email.

## Data and automated tests

The sandbox stores its SQLite database, uploaded media, static output, captured
emails and explicitly extracted attachments inside `sandbox/.data/`, ignored by
Git. Restarting the server preserves this directory. No generated QR files are
stored there by previews or downloads. A page-owned counter row is created only
on its first successful scan redirect.

```bash
just test
just sandbox-test
```

Package tests use the root project's settings. Sandbox tests use their own
settings, a temporary test database and temporary media, preserving the manual
site. Equivalent direct commands are:

```bash
uv run --locked python manage.py test tests
uv run --locked python sandbox/manage.py test home
```

Use the explicit labels to keep each suite's discovery separate. The root
`manage.py`, `just migrate`, `just admin` and `just run` belong to the older test
fixture site; use `sandbox-` recipes for this persistent environment.

Sandbox migrations create the current page models directly, without historical
QR asset fields or document-library dependencies. Use `just sandbox-reset` to
recreate development data if an older sandbox's schema is out of date.

## Local email and attachments

The file backend writes messages to `sandbox/.data/emails/*.log`, without external
delivery. Enter recipient `reader@example.test`, subject and body in the QR tab,
then choose **Save draft** or **Publish**. The EPS is generated in memory and
included in the captured MIME message; it is not registered as a Document.
Autosave sends no message.

```bash
just sandbox-email
```

This prints the latest message and explicitly extracts its EPS attachment to
`sandbox/.data/attachments/`. This inspection command is the only sandbox QR
workflow that deliberately writes a standalone EPS. Preview/download responses
remain transient; a browser download is saved wherever you choose.

Compare the QR geometry or scan destination when inspecting a new download and
an attachment. PyQRCode adds an export timestamp to EPS, so files generated at
different times can differ at `%%CreationDate:`. SVG is the easier format to open
in Pixelmator Pro; EPS requires a viewer that supports standard PostScript EPS.
Both contain vector artwork.

## Configuration and another device

No tunnel is required for localhost. Configure the sandbox with environment
variables; it does not load a `local.py` settings file.

For a phone on the same LAN, use this computer's LAN address
and allow access to port 8000. Use the same origin for both commands:

```bash
SANDBOX_BASE_URL=http://192.168.1.10:8000 just sandbox-setup
SANDBOX_BASE_URL=http://192.168.1.10:8000 just sandbox-run
```

The origin aligns the QR URL, allowed hosts, CSRF origin and admin base URL;
setup aligns the Wagtail Site hostname and port. It must be an HTTP(S) origin
without a path, query or fragment. An existing tunnel's public origin can be used
instead. The server listens on `0.0.0.0:8000`.

After an origin change, run setup and restart with the same setting, then simply
reopen the preview or download a new code. No save or publish action is needed.
The payload is `ORIGIN/qr-code/?id=PAGE_ID`. A phone cannot reach this Mac using
`localhost`; open the configured homepage on the phone before testing its scan.
Printed codes require the encoded domain and route to stay reachable.

To return to localhost, unset `SANDBOX_BASE_URL`, run setup and restart.
Newly generated outputs use localhost again.

Email defaults and QR rendering options can also be set when starting the server:

```bash
WAGTAIL_QRCODE_EMAIL_SUBJECT='Sandbox QR code' \
WAGTAIL_QRCODE_EMAIL_BODY='Here is your QR code.' \
WAGTAIL_QR_CODE='{"scale": 4}' just sandbox-run
```

`WAGTAIL_QR_CODE` takes a JSON object. Omitted options use the package defaults.

## Explicit reset

Stop the sandbox server before running:

```bash
just sandbox-reset
```

This deletes **all** sandbox database content, uploaded media, captured messages
and extracted attachments under `sandbox/.data/`, then restores the examples and
initial login. Back up that directory first to retain manual edits. Reset
preserves the root database and files outside `sandbox/.data/`. A symlinked data
directory is refused.

To remove data without reseeding, use
`uv run --locked python sandbox/reset.py --yes`. Ordinary setup never resets data.

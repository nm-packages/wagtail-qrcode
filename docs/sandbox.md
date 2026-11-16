# Local QR code sandbox

The project in `sandbox/` is a persistent manual testing site.
Follow the [contributor setup](contrubute.md#setup), then run:

```bash
just sandbox-setup
just sandbox-run
```

Open <http://localhost:8000/> or <http://localhost:8000/admin/>.
The initial login is **admin / admin**, for local development only.

Setup applies migrations, configures the Wagtail Site, and creates a published
QR example and a draft. The homepage lists the published example; the draft is
available in admin and Preview, with a public page and scan URL returning 404.

Setup preserves existing passwords, edited pages, revisions and counts.
It recreates missing examples without overwriting pages with the same slug.
Copies and aliases keep their own IDs and do not duplicate setup markers.

The server reloads Python changes. Restart after settings changes and run setup
after adding migrations. Use the [smoke tests](smoke-tests.md) to check workflows.

## Data and tests

Data lives in Git-ignored `sandbox/.data/`: the SQLite database, media, static
output, captured email and extracted attachments. Server restarts preserve it.

QR previews and downloads are generated in memory. No QR Documents or server
assets are created. The first successful scan creates a counter record.

```bash
just test
just sandbox-test
```

Package tests use the root settings; sandbox tests use a temporary database and
media. Both preserve manual sandbox data. See [test commands](contrubute.md#checks)
for direct invocation with explicit discovery labels.

The sandbox uses Django's development server, Wagtail admin and QR pages.
It omits Documents, public search, Django admin, forms, redirects, embeds and
snippets; `wagtail.search` remains for admin search. QR scan redirects still work.
There is no standalone WSGI entrypoint or `local.py` override.

## Email capture

Enter a recipient such as `reader@example.test`, review the subject and body,
then choose **Save draft** or **Publish**. Messages go to
`sandbox/.data/emails/*.log`, without external delivery. Autosave sends nothing.

```bash
just sandbox-email
```

This prints the latest message and extracts its EPS to
`sandbox/.data/attachments/`. Extraction deliberately writes a file; ordinary
previews and downloads do not store server assets.

EPS exports include a `%%CreationDate:` timestamp, so compare geometry or scan
destinations rather than exact bytes. Use an SVG viewer for SVG and a
PostScript-capable viewer for EPS; Pixelmator Pro may reject EPS.

## Configuration and another device

Use environment variables; the sandbox does not load `local.py`.
For a phone on the same LAN, allow port 8000 and use your computer's LAN address:

```bash
SANDBOX_BASE_URL=http://192.168.1.10:8000 just sandbox-setup
SANDBOX_BASE_URL=http://192.168.1.10:8000 just sandbox-run
```

Use the same origin for setup and startup. It sets the Site hostname/port,
allowed hosts, CSRF origin, QR base URL and admin base URL.
Supply an HTTP(S) origin without a path, query or fragment; a tunnel origin
also works. The server listens on `0.0.0.0:8000`.

Open the homepage on the phone before scanning. `localhost` points to the phone,
not your computer. After changing origin, rerun setup, restart and download a new
code; no page save is needed. Printed codes retain the old origin.
Unset `SANDBOX_BASE_URL`, rerun setup and restart to return to localhost.

Override email and rendering defaults when starting the server:

```bash
WAGTAIL_QRCODE_EMAIL_SUBJECT='Sandbox QR code' \
WAGTAIL_QRCODE_EMAIL_BODY='Here is your QR code.' \
WAGTAIL_QR_CODE='{"scale": 4}' just sandbox-run
```

`WAGTAIL_QR_CODE` takes a JSON object; omitted options use
[package defaults](../README.md#configuration).

## Reset

Stop the server and back up `sandbox/.data/` if you need to keep anything:

```bash
just sandbox-reset
```

This deletes all sandbox data and restores the examples and initial login.
Files outside `sandbox/.data/`, including the root database, are preserved.
Symlinked data directories are refused. Use reset if an older sandbox's schema
predates the current migrations.

To delete without reseeding, run
`uv run --locked python sandbox/reset.py --yes`. Ordinary setup never resets data.

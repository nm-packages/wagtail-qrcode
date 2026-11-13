# Local QR code sandbox

The Wagtail project in `sandbox/` is a persistent manual testing site for this
checkout. Its examples use the same in-memory QR renderer as the package: setup,
page saves, previews and downloads create no QR files or Documents.

This is a development site with a known password, intended for your own machine.

## Install, set up and start

From the repository root, with Python 3.11 or newer and uv 0.12.10 or newer:

```bash
uv sync --locked
make sandbox-setup
make sandbox-run
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

Repeat `make sandbox-setup` whenever necessary. It preserves existing users,
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
make test
make sandbox-test
```

Package tests use the root project's settings. Sandbox tests use their own
settings, a temporary test database and temporary media, preserving the manual
site. Equivalent direct commands are:

```bash
uv run --locked python manage.py test tests
uv run --locked python sandbox/manage.py test home
```

Use the explicit labels to keep each suite's discovery separate. The root
`manage.py`, `make migrate`, `make admin` and `make run` belong to the older test
fixture site; use `sandbox-` targets for this persistent environment.

Existing sandbox databases receive a schema migration that removes the old QR
asset fields. Page content and logins remain, but old QR counters are not imported
and historical document files are not cleaned up. Legacy QR data conversion is
outside the current design. The root database and media are left untouched.

## Local email and attachments

The file backend writes messages to `sandbox/.data/emails/*.log`, without external
delivery. Enter recipient `reader@example.test`, subject and body in the QR tab,
then choose **Save draft** or **Publish**. The EPS is generated in memory and
included in the captured MIME message; it is not registered as a Document.
Autosave sends no message.

```bash
make sandbox-email
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

No tunnel is required for localhost. Copy `sandbox/settings/local.py.example` to
`sandbox/settings/local.py` for persistent overrides. This file is ignored and
survives setup/reset. Its `SANDBOX_BASE_URL` takes precedence over the environment
variable of the same name.

For a phone on the same LAN, replace the example with this computer's LAN address
and allow access to port 8000. Use the same origin for both commands:

```bash
SANDBOX_BASE_URL=http://192.168.1.10:8000 make sandbox-setup
SANDBOX_BASE_URL=http://192.168.1.10:8000 make sandbox-run
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

To return to localhost, remove the override or change `local.py`, run setup and
restart. Newly generated outputs use localhost again.

## Explicit reset

Stop the sandbox server before running:

```bash
make sandbox-reset
```

This deletes **all** sandbox database content, uploaded media, captured messages
and extracted attachments under `sandbox/.data/`, then restores the examples and
initial login. Back up that directory first to retain manual edits. Reset
preserves `sandbox/settings/local.py`, the root database and files outside
`sandbox/.data/`. A symlinked data directory is refused.

To remove data without reseeding, use
`uv run --locked python sandbox/reset.py --yes`. Ordinary setup never resets data.

# Local QR code sandbox

The supplied Wagtail project in `sandbox/` is a persistent manual testing site.
Use it to try local package changes without touching the automated test fixtures.
This is a development site with a known password, intended for your own machine.

## Install, set up and start

From the repository root, with Python 3.11 or newer and uv 0.12.10 or newer:

```bash
uv sync --locked
make sandbox-setup
make sandbox-run
```

`uv sync` installs this checkout in editable mode. Changes to `wagtail_qrcode/`
are picked up by the development server's Python reloader; restart after changing
settings, and run setup after adding migrations.

Open <http://localhost:8000/> and <http://localhost:8000/admin/>.
The initial local login is **admin / admin**. Setup applies migrations, configures
the scaffold's Wagtail Site for localhost on port 8000, and creates:

- **Published QR example — scan and download**: a live page with SVG and EPS assets.
- **Draft QR example — save and preview**: an unpublished page with assets,
  available through the admin explorer and preview.

Repeat `make sandbox-setup` whenever necessary. It preserves existing users,
passwords, page edits, slugs, revisions and files, including unpublished changes.
Missing example pages are recreated. Setup updates the sandbox Site's hostname
and port to match the configured base URL. It does not regenerate existing QR
assets; save or publish through the editor to regenerate them.

Follow the [developer smoke tests](smoke-tests.md) to check QR generation,
downloads, redirects, counters, draft isolation, autosave and email attachments.

## Data and automated tests

The sandbox stores its SQLite database, media, static output, captured emails and
extracted attachments inside `sandbox/.data/`, ignored by Git. Stopping or
restarting the server preserves this directory. The root `manage.py` uses the
package test settings and must not be used to start or migrate the sandbox.

```bash
make test
make sandbox-test
```

Package tests use their own settings. Sandbox tests use a temporary database and
temporary media directory, leaving the manual site intact. The equivalent direct
sandbox command is `uv run --locked python sandbox/manage.py test home`.
Use the `home` label to avoid discovering unrelated package tests.

If you used the original scaffold before this integration, its root
`db.sqlite3` and `media/` are left untouched. The integrated sandbox starts with
new state in `sandbox/.data/`; keep any old files until you no longer need them.

## Local email and attachments

The file backend writes messages to `sandbox/.data/emails/*.log`, without
external delivery. Enter any valid recipient such as `reader@example.test`,
subject and body in the QR Code tab, then **Save draft** or **Publish**.

```bash
make sandbox-email
```

This prints the latest captured message and extracts its EPS attachment to
`sandbox/.data/attachments/`. Open the `.eps` with an EPS-capable viewer or inspect
its `%!PS-Adobe` header in a text editor. Compare it with the newly generated
editor download, rather than an older published document. Raw `.log` files
contain the full MIME message, including the attachment.

## Configuration and another device

No tunnel is required for localhost. To persist configuration, copy
`sandbox/settings/local.py.example` to `sandbox/settings/local.py` and edit it.
This file is ignored by Git and survives setup and reset. Set `SANDBOX_BASE_URL`
to configure the origin; its value in `local.py` takes precedence over the
environment variable of the same name.

For a phone on the same LAN, replace this example address with your computer's
LAN address, allow access to port 8000, and run both commands with the same origin:

```bash
SANDBOX_BASE_URL=http://192.168.1.10:8000 make sandbox-setup
SANDBOX_BASE_URL=http://192.168.1.10:8000 make sandbox-run
```

Use that address in the browser on both devices. The server binds to `0.0.0.0`;
the setting aligns the QR base URL, allowed host, CSRF trusted origin and admin
base URL. Setup aligns the Wagtail Site hostname and port. The origin must be
HTTP or HTTPS without a path, query or fragment.

For an existing tunnel, use its public origin instead (for example,
`https://your-tunnel.example`), point it to port 8000, and run setup and startup
with that origin. A changing tunnel origin requires updating the setting and
repeating setup. After any origin change, **Publish** each live QR page and
**Save draft** each draft page to regenerate the assets; previous downloads
still encode the previous origin. The ID redirect survives slug changes, not
changes to the encoded host.

To return to localhost, remove the environment override or change `local.py`,
repeat setup, restart, and regenerate the example QR assets in the editor.

## Explicit reset

Stop the sandbox server before running:

```bash
make sandbox-reset
```

This explicitly deletes **all** sandbox database content, media, captured mail,
and extracted attachments under `sandbox/.data/`, then migrates and restores the
examples and initial login. Back up that directory first if you want to keep
manual edits. Reset preserves `sandbox/settings/local.py`, the root database,
test media and files outside `sandbox/.data/`. A symlinked data directory is
refused. To remove data without reseeding, run
`uv run --locked python sandbox/reset.py --yes`.

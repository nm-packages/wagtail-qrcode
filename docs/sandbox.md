# Local QR code sandbox

Use the sandbox to try the QR code editor, download codes and test scans in a
local Wagtail site. It includes a published example and a draft you can edit.

## Start the sandbox

Complete the [contributor setup](contrubute.md#setup), then run these commands
from the repository root:

```bash
just sandbox-setup
just sandbox-run
```

Open <http://localhost:8000/> to see the published example. Sign in to
<http://localhost:8000/admin/> with **admin / admin** to edit either example.
These credentials are for local development only.

The server reloads Python changes. Restart after settings changes and run setup
after adding migrations.

## Try previews, downloads and scans

1. Open the published example from the homepage and choose
   **Edit page and download QR**.
2. Open the **QR Code** tab to see the preview and scan count. Choose
   **Download SVG** or **Download EPS** to save a code to your computer.
3. Return to the public page and choose **Follow encoded redirect**. It takes
   you back to the page and adds one to the scan count.
4. In the editor, choose **Reset scan count** and confirm to return the count
   to zero.

Use an SVG viewer for SVG files and a PostScript-capable viewer for EPS files.
Previews and downloads do not create Wagtail Documents or store QR files on
the server.

You can also open the draft example in the admin to preview and download its
code. Its public page and scan URL return 404 until you publish it.

For a fuller check of drafts, revisions, copies and permissions, follow the
[manual smoke tests](smoke-tests.md). See the
[contributor checks](contrubute.md#checks) for automated test commands.

## Send and inspect a test email

In the editor's **QR Code** tab, enter a recipient such as `reader@example.test`,
review the subject and body, then choose **Save draft** or **Publish**. The
sandbox captures the message locally; it does not deliver email to the recipient.
Autosave sends nothing.

In another terminal, run:

```bash
just sandbox-email
```

This prints the latest message and saves its EPS attachment in
`sandbox/.data/attachments/`. Captured messages are in
`sandbox/.data/emails/*.log`.

Clear the recipient before saving unrelated edits to avoid capturing another
message.

## Scan from a phone

Connect your phone to the same network as your computer. Stop the sandbox server,
then run the following commands, replacing `192.168.1.10` with your computer's
LAN address. Allow incoming connections on port 8000 if your firewall blocks them.

```bash
SANDBOX_BASE_URL=http://192.168.1.10:8000 just sandbox-setup
SANDBOX_BASE_URL=http://192.168.1.10:8000 just sandbox-run
```

Use the same base URL for both commands so that page links and QR codes point
to the address your phone can reach. It must be an HTTP(S) origin without a path,
query or fragment. You can also use a tunnel's origin instead of a LAN address.

Open `http://192.168.1.10:8000/` on your phone first to check the connection, then
download a fresh code and scan it. Codes made with `localhost` will point to the
phone itself.

Whenever you change the base URL, rerun setup, restart the server and download
new codes. You do not need to save the pages again. Existing codes keep their
old address.

To return to localhost, stop the server and run setup and startup without
`SANDBOX_BASE_URL`. If you exported it in your shell, unset it first.

## Change settings

Pass environment variables when starting the server to change the default email
text or QR rendering options:

```bash
WAGTAIL_QRCODE_EMAIL_SUBJECT='Sandbox QR code' \
WAGTAIL_QRCODE_EMAIL_BODY='Here is your QR code.' \
WAGTAIL_QR_CODE='{"scale": 4}' just sandbox-run
```

Restart the server to apply changes, then reopen the editor or download a new
code. `WAGTAIL_QR_CODE` takes a JSON object; omitted options use the
[package defaults](../README.md#configuration). The sandbox reads these overrides
from the environment and does not load `local.py`.

## Reset the sandbox

Your pages, passwords, revisions and scan counts survive server restarts and
repeated setup. Setup applies migrations and creates missing examples while
preserving your edits. Package and sandbox tests also leave this manual data
alone.

The database, media, static output, captured email and extracted attachments are
stored in Git-ignored `sandbox/.data/`.

To start again, stop the server and back up that directory if you want to keep
anything. Then run:

```bash
just sandbox-reset
just sandbox-run
```

Reset deletes everything in `sandbox/.data/` and restores the two examples and
the **admin / admin** login. Files outside that directory, including the root
database, are preserved. You can also use reset if an older sandbox's database
cannot work with the current migrations.

To delete the data without recreating the examples, use
`uv run --locked python sandbox/reset.py --yes` instead of `just sandbox-reset`.

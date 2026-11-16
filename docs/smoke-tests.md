# Developer smoke tests

Use the [sandbox](sandbox.md) and disposable pages for copy, reset and deletion
checks. QR previews, downloads and email attachments should not create Documents
or stored server assets.

## 1. Setup and downloads

Run `just sandbox-setup` and `just sandbox-run`. Sign in at
<http://localhost:8000/admin/> with `admin` / `admin`, unless changed.

- The homepage lists the published example. The draft is available only in admin
  and Preview. New examples have zero scans and no counter rows.
- Open each example's **QR Code** tab. Check the preview, count and email fields.
  Download SVG and EPS, including from the saved draft.
- SVG opens in an SVG viewer; EPS starts with `%!PS-Adobe`. Export timestamps
  may differ. Downloads create no counter rows or server files.
- Signed-out preview/download requests require login. An admin user without
  permission to edit the page cannot download its QR.

## 2. Scan, rename and move

Choose **Follow encoded redirect** on the published example.

- `ORIGIN/qr-code/?id=PAGE_ID` redirects to the current URL and adds one scan.
- Rename the title and slug, publish, then retry the same scan URL. It still
  works. Repeat a move with a disposable page type that allows it.
- Missing, invalid, unknown, draft and non-QR page IDs return 404 without counting.
- Private live pages enforce access at the destination; redirects to an access
  prompt still count.

## 3. Reset counts

Scan a disposable page, open its editor and change the title without saving.

- Choose **Reset scan count**; cancel once, then confirm.
- The count becomes zero, a success message appears and the button is disabled.
  The unsaved title remains; no revision or email is created.
- Scan again and reload: the count is one. Also check a previously scanned page
  after unpublishing it.
- A user without edit permission cannot reset. A failed reset leaves the count
  unchanged and allows retry.

## 4. Drafts, revisions and autosave

Record a published title and count. Change the title with the recipient blank,
then choose **Save draft**.

- Preview shows the draft; the public page keeps its published content.
- Publish a title, scan, then restore an earlier revision. The QR identity and
  count remain; no QR files are created.
- Enter a new title and valid email fields. Wait for a successful autosave request
  in the browser Network panel, then reload.
- The draft title remains, live content stays unchanged, and no email is sent.
  One-time email inputs are not restored.

## 5. Email

Reopen the editor. The recipient is blank; the subject is **Your QR code** and
the body is **Please find your QR code attached as an EPS file.**

- Enter a recipient, clear each message field in turn and save. Validation
  requires the missing value and preserves input.
- Enter `reader@example.test`, subject `QR smoke test` and a body. Save a draft,
  then run `just sandbox-email`. Repeat with **Publish**.
- Each request captures one message with those values and `qr-code-PAGE_ID.eps`.
  Extracted EPS matches a fresh download apart from `%%CreationDate:`.
  No external email or Document is created; saving a draft does not publish it.
- Restart with the [email environment overrides](sandbox.md#configuration-and-another-device)
  and reopen the editor to check new defaults.

Clear the recipient before unrelated saves.

## 6. Copies and aliases

Copy the published example, create an alias and optionally a chained alias.
Publish the ordinary copy.

- Each page's preview/download encodes its own ID and starts with zero scans.
  For alias downloads, use the header's **Actions** menu.
- Scan each: counts remain independent. Publish a source title change: aliases
  update their content while keeping their QR identity.
- Repeat setup: no duplicate examples or changes to copies, aliases or edited titles.

## 7. Settings, persistence and deletion

Restart with `WAGTAIL_QR_CODE='{"scale": 4}' just sandbox-run`.

- Reopen previews and downloads without saving: new output uses scale 4;
  omitted options retain defaults.
- Record titles, drafts, counts and captured email. Stop the server, run setup
  twice, `just test` and `just sandbox-test`, then restart without overrides.
  Tests pass and manual data remains, with one of each seeded example.
- Delete a scanned disposable page or alias. Its scan URL returns 404 and its
  counter is removed; other pages and counts remain. Downloads and captured
  emails remain independent copies.

## 8. Device testing and reset

Optionally follow the [LAN/tunnel setup](sandbox.md#configuration-and-another-device)
and scan a new code from a phone. It reaches the page and adds a scan.

To discard manual data, stop the server, back up `sandbox/.data/` if needed,
then run `just sandbox-reset` and `just sandbox-run`. The two examples and
initial login return, with no counts or stored QR assets. Files outside the
data directory remain.

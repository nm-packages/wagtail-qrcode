# Developer smoke tests

Use the [persistent sandbox](sandbox.md) to verify the package's in-memory QR
workflow. These checks do not require any QR Documents or stored SVG/EPS assets.
Use disposable pages for copy and deletion checks; keep manual edits you need.

## 1. Set up and inspect the examples

Run `uv sync --locked`, `make sandbox-setup` and `make sandbox-run`. Open
<http://localhost:8000/> and sign into <http://localhost:8000/admin/> with
`admin` / `admin` (unless you have changed that user's password).

**Expected:** Home lists the published example. The draft is available only in
admin and Preview. Setup creates no QR Documents and no QR counter rows.
The public example displays a freshly generated SVG and a usage count of zero
unless it has already been scanned.

## 2. Preview and download

Open the published example's **QR Code** editor tab. Check the preview, **Download
SVG**, **Download EPS**, scan count and one-time email inputs. Download both
formats, then repeat with the draft example.

**Expected:** There is no document chooser or editable asset/count field.
Both formats download immediately, including for the saved draft. SVG opens in
an SVG-capable viewer. EPS begins with `%!PS-Adobe` and is vector PostScript;
Pixelmator may reject standard EPS, so use SVG there. Repeated downloads create
no Documents, counter rows or server-side QR files. EPS export timestamps may
differ between requests.

### Reset the scan count

On a disposable QR page, follow its scan URL to make the count positive. Open
the editor, change the title without saving, and choose **Reset scan count**.
Cancel once, then confirm. Check that the count changes to zero, a success
message appears and the button becomes disabled. The unsaved title must remain
in the editor. Confirm no revision or email was created, then scan again and
reload the editor to see one scan. At zero the button is disabled. Repeat on a
saved draft with an existing count. A user without permission to edit the page
must not be able to reset it. If the reset request fails, the count must stay
unchanged and the button must allow a retry.

Open the preview or download URL in a signed-out/private browser.

**Expected:** Admin login is required. A user who can access admin but cannot edit
that page cannot download its QR. The public template's inline SVG is independent
of these authenticated download endpoints.

## 3. Scan, rename and move

On the published example, choose **Follow encoded redirect**. Refresh its usage
count in the public page and editor. Change the title and slug, publish, and
repeat the same scan URL.

**Expected:** The payload is `ORIGIN/qr-code/?id=PAGE_ID`; a successful request
redirects to the page's current URL and increments the page-owned count. The page
ID and scan payload remain the same after a rename. On a disposable page type
that allows moving, the same applies after moving to another parent.

Try missing, invalid and unknown IDs. Try the draft example's scan URL.

**Expected:** These return 404 and do not increase counts. Unpublished pages are
not served through the scan endpoint. Access restrictions on a private live page
remain enforced at the destination; the count measures redirects, not confirmed
content views or unique visitors.

## 4. Save a draft and restore a revision

Record the live title and scan count. Edit the published page's title, leave email
blank, and choose **Save draft**. Open Preview and refresh the public page. Then
publish an intended title, scan once, and restore an earlier content revision.

**Expected:** Draft content stays separate from published content. QR identity is
the same for both because it uses the page ID. Previewing, saving and restoring
create no QR files. The earlier revision does not restore or reset the scan count.
Publishing does not need an asset generation step.

## 5. Check autosave

Edit a title and enter valid email recipient, subject and body. Wait for a
successful Wagtail autosave request in the browser Network panel without choosing
Save draft or Publish. Reload the editor and public page.

**Expected:** The draft title is retained, live content stays unchanged, no QR
files or captured emails are created, and one-time email fields are not restored.
Clear email inputs before unrelated saves.

## 6. Capture an EPS email

Open the QR Code tab and check that the subject is **Your QR code** and the body
is **Please find your QR code attached as an EPS file.**, with a blank recipient.
Check that both messages can be edited. With a recipient entered, clear the body
and save: validation should retain your input and require a body. Restore the
body before continuing. Overrides in `sandbox/settings/local.py` using
`WAGTAIL_QRCODE_EMAIL_SUBJECT` and `WAGTAIL_QRCODE_EMAIL_BODY` should appear after
restarting the server and reopening the editor.

Enter recipient `reader@example.test`, subject `QR smoke test`, and a body. Choose
**Save draft**, then run `make sandbox-email`. Optionally repeat with **Publish**.

**Expected:** Each explicit email request produces one captured message with the
requested fields and a `qr-code-PAGE_ID.eps` attachment. Extraction writes an EPS
under `sandbox/.data/attachments/`. It represents the same code as a fresh EPS
download; ignore the `%%CreationDate:` line when comparing bytes. No Document is
created, and no external delivery occurs. Saving a draft does not publish it.
Clear email inputs before subsequent saves.

## 7. Copy and create an alias

Create an ordinary copy and an alias of the published example, then a chained
alias if desired. Publish the ordinary copy. Download or preview each code and
follow each page's scan URL. Publish a source title change and repeat setup.

**Expected:** Each page's code embeds its own page ID. Counts are independent and
start at zero. Aliases receive the source content updates while retaining their
own scan identity. Setup adds no duplicate example pages and does not change the
copies, aliases, counts or edited titles.

## 8. Change rendering settings

Add this to `sandbox/settings/local.py`, then restart:

```python
WAGTAIL_QR_CODE = {"scale": 4}
```

Reopen a preview and download both formats, without saving or publishing a page.

**Expected:** New output uses the new scale immediately. Unspecified settings
retain their defaults. No new Document, saved file or page revision appears.
Restore the previous setting and restart when finished.

## 9. Restart, repeat setup and run tests

Record edited titles/slugs, unpublished content, scan counts and captured email.
Stop the server, run `make sandbox-setup` twice, `make test`, and
`make sandbox-test`, then restart with `make sandbox-run`.

**Expected:** Both suites pass. Manual pages, passwords, revisions, counts and
captured mail remain available, with one copy of each seeded example. Tests use
isolated databases/media. There are no generated QR files to recover after restart.

## 10. Delete a disposable page

Scan a disposable published QR page, record its ID, then delete it through the
explorer. Repeat with a disposable alias if useful.

**Expected:** Its scan URL returns 404, its counter record is deleted, and other
pages and their counts remain. There are no QR Documents or asset files to clean
up. Previously saved browser downloads and captured emails are independent copies.

## 11. Test another device or reset (optional)

For device testing, apply the [LAN/tunnel configuration](sandbox.md#configuration-and-another-device)
to setup and startup. Open the homepage on the phone, then scan a newly generated
code. It should reach that page and increase its count. No page save is required
to apply a new origin. Restore local configuration afterwards if desired.

To discard manual sandbox content, stop the server and back up `sandbox/.data/`
if needed, then explicitly run `make sandbox-reset` and `make sandbox-run`.

**Expected:** Reset restores the two examples and `admin` / `admin`, with no
counters or stored QR assets. Local settings and files outside `sandbox/.data/`
remain intact. Do not reset content you intend to keep.

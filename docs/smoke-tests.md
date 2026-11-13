# Developer smoke tests

These checks exercise the persistent [local sandbox](sandbox.md). Run them in
order against a fresh setup or explicitly reset first if you no longer need your
manual content. Optional device checks are marked below. Record the
commit, browser, Python/Django/Wagtail versions and the result of each check.

## 1. Start, log in and confirm editable installation

**Prerequisites:** uv and a supported Python installed; terminal at repository root.

**Actions:** Run `uv sync --locked`, `make sandbox-setup` and `make sandbox-run`.
Open <http://localhost:8000/> and then `/admin/`. Log in with `admin` / `admin`.
In Pages, open Home and edit **Published QR example — scan and download**.
Open its **QR Code** tab. To confirm the installation points to this checkout, run:

```bash
uv run --locked python -c 'import wagtail_qrcode; print(wagtail_qrcode.__file__)'
```

**Expected:** The import path is this checkout's `wagtail_qrcode/__init__.py`.
The homepage links to the published example. The admin has both examples; the
QR tab shows an SVG, an EPS document, a usage count and three email fields.

**Cleanup:** None; leave the server running. For a configured LAN/tunnel, replace
localhost throughout this guide with your configured origin.

## 2. Create and save a draft

**Prerequisites:** Logged in; Home is visible in the page explorer.

**Actions:** Choose **Add child page** under Home, select QR code page if prompted,
and enter title `Smoke draft` and slug `smoke-draft` (Promote tab). Leave email
fields empty. Choose **Save draft**, then reopen the page's QR Code tab.
Download the EPS through the document link and open Preview.

**Expected:** The page remains draft, its QR tab displays an SVG and a new EPS
document, and the download starts with `%!PS-Adobe` when opened as text. Preview
shows `Smoke draft`, the SVG and an EPS download link. The public
`/smoke-draft/` URL returns 404 and the homepage does not list it.

**Cleanup:** Keep this page for the next check. Repeat explicit draft saving on
**Draft QR example — save and preview** if you also want to inspect the seeded draft.

## 3. Publish and inspect the public page

**Prerequisites:** The `Smoke draft` page from check 2.

**Actions:** Edit it, change its title to `Smoke published`, and choose **Publish**.
Open `/smoke-draft/` in a second tab and download its EPS.

**Expected:** The page is live and appears on the homepage. Its public title is
`Smoke published`, with a visible SVG, a working EPS download, a redirect link
and a usage count. The editor's current document and public download match.

**Cleanup:** Keep the page and downloaded EPS for checks 4–7.

## 4. Follow the encoded URL and check usage

**Prerequisites:** The live page from check 3. Note the usage count shown publicly.

**Actions:** Scan its SVG using a QR-capable browser/image reader, or use the
public **Follow encoded redirect** link, which uses the same ID endpoint.
For actual QR decoding on a separate device, complete optional check 11.
Reload the public page and reopen the QR Code editor tab.

**Expected:** The encoded address is `BASE_URL/qr-code?id=PAGE_ID`, with this
page's numeric ID. Following it redirects to `/smoke-draft/`. Each request to
the QR redirect increases usage by one; ordinary public-page refreshes do not.
The public page and freshly loaded editor show the updated count. Scanner
previews can fetch a URL more than once, so use one browser request when
checking an exact increment.

**Cleanup:** None. Keep the full QR redirect URL for check 5.

## 5. Change a published slug

**Prerequisites:** The live page and its original QR redirect URL from check 4.

**Actions:** Edit the slug in Promote to `smoke-renamed` and choose **Publish**.
Visit the original ID-based QR redirect URL again.

**Expected:** It redirects to `/smoke-renamed/` with the same page ID, and usage
increases. The downloaded/printed QR remains usable because the page ID did not
change. A redirect from the old page slug is not the behavior being tested.

**Cleanup:** Keep this page for the draft and autosave checks.

## 6. Save draft changes to a live page

**Prerequisites:** The live page at `/smoke-renamed/`. Record its public title,
SVG (save the page source), and EPS URL and bytes. Close other editor tabs.

**Actions:** Edit the title to `Unpublished draft title`, leave email blank, and
choose **Save draft**. Reopen the editor and its Preview. Refresh the public
page in a separate tab and download its EPS again.

**Expected:** The editor and preview show the draft title and regenerated draft
QR assets. The public title, SVG, EPS URL and EPS bytes stay unchanged. The page
has unpublished changes. The original document remains downloadable; generating
a draft EPS does not delete published or historical files.

**Cleanup:** Publish the intended title to return the page to a clean live state
before check 7. Do not publish a title you want to keep private.

## 7. Allow autosave without explicit saving

**Prerequisites:** Wagtail with autosave available and enabled (the locked
environment enables it by default). A clean live page from check 6. Record its
public title, SVG and EPS URL, the number of documents in the **QR Codes**
collection under Documents, and existing captured messages. Close other editor tabs.

**Actions:** Open browser developer tools on the editor's Network tab. Change the
title to `Autosave only`, enter recipient `reader@example.test`, subject
`Do not send from autosave` and body `Autosave check`. Do not click Save draft or
Publish. Wait until the editor's automatic save completes; inspect the save
request and confirm its JSON response reports success. Reload the editor and
check the public page, Documents and local email capture.

**Expected:** The automatic request succeeds and the reloaded editor retains the
draft title. Published content and assets stay unchanged. No new EPS document or
email is created. Email fields are one-time inputs and are not restored after
reload. If the installed Wagtail has no autosave, record this check as unavailable
and repeat it with the locked contributor environment.

**Cleanup:** Clear email inputs if still present, restore the intended title and
choose **Publish**. This explicit action generates assets, so count documents
before this cleanup when judging the autosave result.

## 8. Send and inspect an EPS email

**Prerequisites:** The sandbox running with file capture. Note the current
document ID and existing messages.

**Actions:** Edit the QR page, change its title to `Email attachment check`, and
enter recipient `reader@example.test`, subject `QR smoke test` and body
`Please inspect this EPS.` Choose **Save draft**, then run `make sandbox-email`.
Download the new draft EPS from the editor and compare it with the extracted
email attachment.
For example, replace these paths with your downloads:

```bash
cmp sandbox/.data/attachments/qr-code-PAGE_ID.eps /path/to/new-draft.eps
```

**Expected:** One new message has the requested recipient, subject and body and
an attachment named `qr-code-PAGE_ID.eps`. Its bytes match the newly generated
draft EPS, whose document ID differs from the previous one. `cmp` exits zero.
The public page and its EPS remain unchanged. No external delivery occurs.
Repeat with **Publish** if you also want to check publication and email together.

**Cleanup:** Clear any email fields before later saves. Publish the intended
content when finished, or leave the draft for further inspection. Keep the
captured message until after check 9.

## 9. Restart and run automated tests

**Prerequisites:** Existing sandbox content and at least one downloaded QR file.
Record the live page URL, title and EPS URL. Optionally note draft edits and mail.

**Actions:** Stop the server with Ctrl-C. Run `make test` and `make sandbox-test`,
then `make sandbox-run`. Log in again and open the recorded public page, EPS
URL, editor draft and captured email.

**Expected:** Both suites pass. The sandbox content, login, generated files,
draft revisions and captured mail remain available after tests and restart.

**Cleanup:** None.

## 10. Repeat setup and explicitly reset

**Prerequisites:** Manual content you can discard or a backup of `sandbox/.data/`.
Stop the server. This check intentionally erases sandbox edits in its reset step.

**Actions:** Run `make sandbox-setup` twice, restart, and inspect the pages, users
and Sites in admin. Confirm previous titles/slugs, drafts and password edits
remain, with one admin and one copy of each example. Stop the server again,
then run `make sandbox-reset` and `make sandbox-run`.

**Expected:** Repeated setup causes no duplicates or loss of edits. Reset restores
the two named examples, fresh QR assets and `admin` / `admin`, removes other
sandbox content and captured mail, and preserves local configuration. Files
outside `sandbox/.data/`, including any root database/test media, are untouched.
The restored draft is not public; the published example is listed on Home.

**Cleanup:** None; the restored sandbox is ready for the next session. Remove
backup copies only when no longer needed.

## 11. Scan from another device (optional)

**Prerequisites:** A phone/other device, shared LAN or existing tunnel, and the
[device configuration](sandbox.md#configuration-and-another-device) applied to
both setup and startup. Regenerate QR assets after setting the new origin.

**Actions:** First open the configured homepage on the other device. On the
computer, open the published example and scan its displayed SVG with the phone.
Follow the scan's URL, then refresh the usage count on the computer.

**Expected:** The scan encodes the configured LAN/tunnel origin and
`/qr-code?id=PAGE_ID`, reaches the intended public page and increases usage.
If the homepage cannot load on the phone, resolve network/tunnel access before
judging QR generation.

**Cleanup:** Restore localhost configuration if desired, repeat setup, restart
and regenerate the QR assets. Stop any optional tunnel when no longer needed.

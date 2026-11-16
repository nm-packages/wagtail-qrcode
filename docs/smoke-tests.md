# Developer smoke tests

Use these checks to test the QR code workflows in the Wagtail admin. Follow the
[sandbox guide](sandbox.md#start-the-sandbox) to start the site and sign in.

Use disposable pages for changes you want to undo, especially moves, count
resets and deletion. The final check resets the whole sandbox, so back up any
manual data you want to keep before running it.

QR previews, downloads and email attachments are generated in memory. Running
`just sandbox-email` saves the captured EPS attachment in
`sandbox/.data/attachments/` so you can inspect it.

## Preview and download a code

After a fresh setup, the homepage should list the published example. The draft
should be available in the admin and through Preview, but not as a public page.
Both examples should start with zero scans and no scan-counter records.

1. Open each example in the editor and select the **QR Code** tab. Check that
   the preview, scan count and email fields appear.
2. Download both SVG and EPS files from each example, including the saved draft.
   Open the SVG in an SVG viewer and check that the EPS starts with `%!PS-Adobe`.
   Export timestamps may differ between downloads.
3. Check that previewing and downloading have not created scan-counter records
   or stored QR files on the server.
4. Request a preview and a download while signed out. Both should require login.
   Then try downloading as an admin user who cannot edit the page; the download
   should be denied.

## Scan a code after renaming or moving a page

1. Open the published example and choose **Follow encoded redirect**. The scan
   URL, `ORIGIN/qr-code/?id=PAGE_ID`, should redirect to the page's current URL
   and add one to its count. Keep this scan URL for the next steps.
2. Change the page's title and slug, then publish it. Visit the same scan URL
   again. It should reach the new page URL and add another scan.
3. Move a disposable QR page to another location, using a page type that allows
   the move. Its existing scan URL should still reach it and increase its count.

Also check requests with no page ID, an invalid value, an ID that does not exist,
a draft's ID and a non-QR page's ID. Each should return 404 without increasing
any count.

For a private, published page, check that the destination still enforces its
access restrictions. A redirect to an access prompt should count as a scan.

## Reset a scan count

Scan a disposable page, open its editor and change the title without saving it.

1. Choose **Reset scan count**, then cancel. The count should stay unchanged.
2. Choose it again and confirm. The count should become zero, a success message
   should appear and the reset button should become disabled. Your unsaved title
   should remain in the editor, with no new revision or email.
3. Scan the page again and reload the editor. The count should now be one.
4. Unpublish the page and check that you can still reset its existing count.

Check that a user without edit permission cannot reset the count. Also try a
reset while the server is temporarily stopped: the request should fail without
changing the count. Restart the server and check that you can retry successfully.

## Save drafts, restore revisions and check autosave

1. Record a published page's title and scan count. Leave the email recipient
   blank, change the title and choose **Save draft**. Preview should show your
   new title while the public page keeps its published content.
2. Publish a title change and scan the page. Restore an earlier revision and
   check that the page keeps its QR identity and count. Restoring the revision
   should not create QR files.
3. Enter another title change and fill in valid email fields. In your browser's
   Network panel, wait for a successful autosave request, then reload the editor.
   The draft title should remain and the public page should stay unchanged.
   Autosave should send no email, and your entered email values should not be
   restored.

## Send a QR code by email

Use a draft page for this check. Reopen its editor without email overrides
configured. The recipient should be blank, the subject should be **Your QR code**
and the body should be **Please find your QR code attached as an EPS file.**

1. Enter a recipient and clear the subject, then try saving. Validation should
   ask for the subject and preserve your input. Restore the subject and repeat
   with an empty body.
2. Enter `reader@example.test`, use `QR smoke test` as the subject and write a
   body. Choose **Save draft**, then run `just sandbox-email` in another terminal.
   There should be one new captured message with those values and an attachment
   named `qr-code-PAGE_ID.eps`. The page should remain a draft.
3. Compare the extracted EPS with a fresh download. They should match apart
   from the `%%CreationDate:` timestamp.
4. Enter the email values again and repeat with **Publish**. This should capture
   one more message. Neither action should deliver external email or create a
   Wagtail Document.
5. Restart with the [email environment overrides](sandbox.md#change-settings)
   and reopen the editor. The subject and body should use the new defaults.

Clear the recipient before saving unrelated edits.

## Copy a page and create aliases

Copy the published example, create an alias and, optionally, create an alias of
that alias. Publish the ordinary copy.

1. Preview and download each new page's code. For aliases, use the header's
   **Actions** menu. Each code should encode its own page ID, and each new page
   should start with zero scans.
2. Scan each code and check that only its own page's count increases.
3. Publish a title change on the source page. Its aliases should receive the
   content change while keeping their own QR identities.
4. Run `just sandbox-setup` again. It should leave copies, aliases and edited
   titles unchanged, without creating duplicate examples.

## Change QR rendering settings

Stop the server and restart it with a different scale:

```bash
WAGTAIL_QR_CODE='{"scale": 4}' just sandbox-run
```

Reopen a preview and download new codes without saving the page. The new output
should use scale 4, with omitted options keeping their default values.

## Check that setup and tests preserve your data

Record your page titles, drafts, scan counts and captured email. Stop the server,
then run:

```bash
just sandbox-setup
just sandbox-setup
just test
just sandbox-test
just sandbox-run
```

Start without the earlier settings overrides. Both test suites should pass,
your manual data should remain and there should still be exactly one of each
seeded example.

## Delete a page

Delete a scanned disposable page or alias, then visit its scan URL. It should
return 404, and the page's scan-counter record should be removed. Other pages
and their counts should stay unchanged.

Previously downloaded codes and captured emails should remain available as
independent copies.

## Scan from a phone

Follow the [phone setup](sandbox.md#scan-from-a-phone), then scan a newly
downloaded code from your phone. It should reach the page and add one scan.
You can skip this check if you are not testing with another device.

## Reset the sandbox

Stop the server and back up `sandbox/.data/` if you want to keep any manual data.
Then run:

```bash
just sandbox-reset
just sandbox-run
```

The two examples and the initial **admin / admin** login should return, with
zero scans and no stored QR assets. Files outside `sandbox/.data/` should remain
unchanged.

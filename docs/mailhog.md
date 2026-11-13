# Optional local MailHog

The [sandbox](sandbox.md) captures mail to files by default. For a browser-based
viewer with attachment downloads, Docker users can start the existing MailHog
container with:

```bash
make mail
SANDBOX_MAIL=smtp make sandbox-run
```

Stop any running sandbox server before restarting with SMTP capture. If
`sandbox/settings/local.py` sets `SANDBOX_MAIL`, change it to `"smtp"` there;
local settings take precedence over the environment. `make mail` only starts
the container, binding SMTP and the viewer to loopback; it never changes
`tests/local.py` or `sandbox/settings/local.py`, and does not start Django.

Open <http://localhost:8025/>. Fill in the recipient, subject and body in a QR
page's QR Code tab, then choose **Save draft** or **Publish**. Inspect the message
and download the EPS attachment in MailHog. Follow the detailed
[email smoke test](smoke-tests.md#8-send-and-inspect-an-eps-email) to compare it
with the newly generated document.

If a container named `mailhog` already exists, use `docker start mailhog`.
Stop and remove it with `make mail-stop`. Messages in the container are temporary
and disappear when it is removed; sandbox reset only deletes file capture, not
Docker state. Switch back to `SANDBOX_MAIL=file` and restart the server when
finished. These commands retain the repository's existing optional image and
require Docker; no container is needed for file capture or automated tests.

To use MailHog with the older test fixture site, configure `tests/local.py`
explicitly using `tests/local.py.example`; the persistent sandbox is the
recommended manual testing site.

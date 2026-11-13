#!/usr/bin/env python
"""Print the latest captured email and extract its attachment for inspection."""

from email import policy
from email.parser import BytesParser
from pathlib import Path


def main():
    data = Path(__file__).resolve().parent / ".data"
    messages = list((data / "emails").glob("*.log"))
    if not messages:
        raise SystemExit("No captured email. Send a QR email from the editor first.")
    latest = max(messages, key=lambda path: path.stat().st_mtime_ns)
    message = BytesParser(policy=policy.default).parsebytes(latest.read_bytes())
    print(f"Message: {latest}")
    for header in ("From", "To", "Subject"):
        print(f"{header}: {message[header]}")
    print(message.get_body(preferencelist=("plain",)).get_content())
    for attachment in message.iter_attachments():
        output = data / "attachments" / Path(attachment.get_filename()).name
        output.parent.mkdir(exist_ok=True)
        output.write_bytes(attachment.get_payload(decode=True))
        print(f"Attachment: {output}")


if __name__ == "__main__":
    main()

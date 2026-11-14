def eps_without_timestamp(content):
    """Compare QR geometry and metadata without PyQRCode's export timestamp."""
    return b"\n".join(
        line for line in content.splitlines() if not line.startswith(b"%%CreationDate:")
    )

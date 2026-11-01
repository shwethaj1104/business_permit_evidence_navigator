import ipaddress
import socket
import time
from urllib.parse import urljoin, urlsplit

import httpx

from app.core.errors import AppError
from app.core.logging import logged_operation
from app.models.domain import ALLOWED_DOMAINS

MAX_BYTES = 10 * 1024 * 1024


def validate_url(url, resolve=True):
    # Restrict every request and redirect to approved public HTTPS destinations.
    parsed = urlsplit(url)
    hostname = (parsed.hostname or "").lower()
    allowed = any(hostname == domain or hostname.endswith("." + domain) for domain in ALLOWED_DOMAINS)
    if (
        parsed.scheme != "https"
        or not allowed
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 443)
    ):
        raise AppError("Source URL is outside the approved official HTTPS domains.", 422)
    if resolve:
        addresses = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(row[4][0]).is_global for row in addresses):
            raise AppError("Source URL did not resolve to a public destination.", 422)
    return url


class SourceFetcher:
    """Download bounded official HTML/PDF snapshots with explicit redirect checks."""

    @logged_operation("sources.fetch")
    def fetch(self, url):
        # Retry transient transport failures without following unchecked redirects.
        for attempt in range(3):
            try:
                return self._download(url)
            except (httpx.TransportError, socket.gaierror) as exc:
                if attempt == 2:
                    raise AppError("Official source could not be reached after three attempts.", 502) from exc
                time.sleep(attempt + 1)
        raise AppError("Official source could not be reached.", 502)

    def _download(self, url):
        # Stream bytes to cap memory and verify each redirected target.
        with httpx.Client(
            timeout=30,
            follow_redirects=False,
            trust_env=False,
            headers={"User-Agent": "PermitNavigator/0.1 (local research application)"},
        ) as client:
            for _ in range(6):
                validate_url(url)
                with client.stream("GET", url) as response:
                    if response.is_redirect:
                        location = response.headers.get("location")
                        if not location:
                            raise AppError("Official source returned a redirect without a destination.", 502)
                        url = urljoin(url, location)
                        continue
                    if response.status_code != 200:
                        raise AppError(f"Official source returned HTTP {response.status_code}.", 502)
                    content_type = response.headers.get("content-type", "").split(";")[0].lower()
                    if content_type not in ("text/html", "application/pdf", "application/xhtml+xml"):
                        raise AppError("Only official HTML and PDF sources are supported.", 422)
                    content = bytearray()
                    for block in response.iter_bytes():
                        content.extend(block)
                        if len(content) > MAX_BYTES:
                            raise AppError("Official source exceeds the 10 MB ingestion limit.", 422)
                    return bytes(content), content_type, url
        raise AppError("Official source exceeded the redirect limit.", 502)

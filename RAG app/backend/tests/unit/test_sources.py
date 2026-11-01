import pytest

from app.core.errors import AppError
from app.integrations.official_sources.extractor import chunk_sections, content_hash, extract
from app.integrations.official_sources.fetcher import validate_url


@pytest.mark.parametrize(
    "url",
    [
        "http://u.ae/page",
        "https://u.ae.evil.test",
        "https://127.0.0.1",
        "https://user:pass@u.ae",
        "https://u.ae:8000/page",
        "file:///etc/passwd",
    ],
)
def test_reject_unsafe_urls(url):
    # Reject lookalike domains, credentials, internal addresses, and unsupported schemes.
    with pytest.raises(AppError):
        validate_url(url, resolve=False)


def test_date_provenance_and_normalization():
    # Preserve explicit source dates while excluding navigation noise.
    raw = (
        '<html><head><title>Guide</title><meta property="article:published_time" content="2026-01-02"></head>'
        "<body><nav>Noise</nav><main>" + "<p>Required business document.</p>" * 20 + "</main></body></html>"
    ).encode()
    doc = extract(raw, "text/html")
    assert doc.published == "2026-01-02"
    assert doc.updated is None
    assert "Noise" not in doc.text
    assert len(chunk_sections(doc.sections)) > 0
    first = content_hash(doc)
    doc.updated = "2026-02-03"
    assert content_hash(doc) != first


def test_empty_js_page_is_not_indexed():
    # Prevent an empty JavaScript shell from becoming licensing evidence.
    with pytest.raises(AppError):
        extract(b"<main>Loading...</main>", "text/html")


def test_private_dns_is_rejected(monkeypatch):
    # Reject an allowed hostname if DNS points at a private network destination.
    monkeypatch.setattr("socket.getaddrinfo", lambda *args, **kwargs: [(2, 1, 6, "", ("10.0.0.1", 443))])
    with pytest.raises(AppError):
        validate_url("https://u.ae/page")


def test_unchanged_sections_retain_prior_observation_date():
    # Preserve dates on unchanged text while dating only added/modified sections anew.
    from app.integrations.official_sources.extractor import section_history

    first, _ = section_history([{"locator": "Documents", "text": "Existing requirement"}], [], "2026-10-25")
    second, changes = section_history(
        [
            {"locator": "Documents", "text": "Existing requirement"},
            {"locator": "Premises", "text": "Additional requirement"},
        ],
        first,
        "2026-10-26",
    )
    assert second[0]["change_detected_at"] == "2026-10-25"
    assert changes[0]["status"] == "unchanged"
    assert second[1]["change_detected_at"] == "2026-10-26"
    removed, removal = section_history([], second, "2026-10-27")
    assert removed == []
    assert all(row["status"] == "removed" for row in removal)

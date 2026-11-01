import hashlib
import io
import json
import re

from bs4 import BeautifulSoup
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.core.errors import AppError
from app.core.logging import logged_operation
from app.integrations.official_sources.embedded_content import sitecore_sections
from app.models.domain import ExtractedDocument


def normalize(text):
    # Remove layout noise while preserving paragraph boundaries for comparisons.
    return "\n".join(
        line for line in (re.sub(r"[ \t]+", " ", row).strip() for row in text.splitlines()) if line
    )


@logged_operation("sources.extract")
def extract(content, content_type):
    # Extract source text and explicit page metadata without inferring regulatory dates.
    if content_type == "application/pdf":
        try:
            reader = PdfReader(io.BytesIO(content))
        except PdfReadError as exc:
            raise AppError("Source PDF could not be parsed; manual review or OCR is required.", 422) from exc
        if len(reader.pages) > 200:
            raise AppError("PDF exceeds the 200-page ingestion limit.", 422)
        sections = [
            {"locator": f"Page {i + 1}", "text": normalize(page.extract_text() or "")}
            for i, page in enumerate(reader.pages)
        ]
        doc = ExtractedDocument(
            str((reader.metadata or {}).get("/Title", "Official PDF")),
            "\n".join(row["text"] for row in sections),
            sections,
        )
    else:
        soup = BeautifulSoup(content, "html.parser")
        title = soup.title.get_text(" ", strip=True) if soup.title else "Official source"
        dates = {}
        for tag in soup.find_all("meta"):
            key = tag.get("property") or tag.get("name")
            if key in ("article:published_time", "datePublished"):
                dates["published"] = tag.get("content")
            if key in ("article:modified_time", "dateModified"):
                dates["updated"] = tag.get("content")
        embedded = sitecore_sections(soup)
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()
        main = soup.find("main") or soup.find("article") or soup.body or soup
        text = normalize(main.get_text("\n", strip=True))
        sections, heading, paragraphs = [], "Overview", []
        for block in main.find_all(["h1", "h2", "h3", "h4", "p", "li", "table"]):
            if block.find_parent(["li", "table"]):
                continue
            if block.name in ("h1", "h2", "h3", "h4"):
                if paragraphs:
                    sections.append({"locator": heading, "text": normalize("\n".join(paragraphs))})
                heading, paragraphs = block.get_text(" ", strip=True), []
            else:
                paragraphs.append(block.get_text(" ", strip=True))
        if paragraphs:
            sections.append({"locator": heading, "text": normalize("\n".join(paragraphs))})
        if not sections:
            sections = [{"locator": "Web page", "text": text}]
        counts = {}
        for section in sections:
            base = section["locator"]
            counts[base] = counts.get(base, 0) + 1
            section["locator"] = f"{base} ({counts[base]})"
        if len(text) < 200 and embedded:
            sections = embedded
            text = "\n".join(section["text"] for section in sections)
        doc = ExtractedDocument(title, text, sections, dates.get("published"), dates.get("updated"))
    if len(doc.text) < 200:
        raise AppError("Source has too little extractable text; it may require JavaScript or OCR.", 422)
    if len(doc.text) > 250000:
        raise AppError("Source exceeds the extracted-text limit; narrow the registered source.", 422)
    return doc


def content_hash(document):
    # Include explicit source-date changes in version identity.
    payload = json.dumps([document.text, document.published, document.updated], ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def chunk_sections(sections, size=1400, overlap=180):
    # Keep page locators and modest overlap without mixing document versions.
    chunks = []
    for section in sections:
        for start in range(0, len(section["text"]), size - overlap):
            text = section["text"][start : start + size].strip()
            if text:
                chunks.append(
                    {
                        "text": text,
                        "locator": section["locator"],
                        "ordinal": len(chunks),
                        "content_hash": hashlib.sha256(text.encode()).hexdigest(),
                    }
                )
    return chunks


def section_history(sections, previous_sections, detected_at):
    # Retain observation dates for unchanged sections; never infer the authority's edit time.
    previous = {section["locator"]: section for section in previous_sections}
    current, changes = [], []
    for section in sections:
        fingerprint = hashlib.sha256(section["text"].encode()).hexdigest()
        before = previous.get(section["locator"])
        changed = before is None or before["content_hash"] != fingerprint
        last_change = detected_at if changed else before["change_detected_at"]
        current.append({**section, "content_hash": fingerprint, "change_detected_at": last_change})
        changes.append(
            {
                "locator": section["locator"],
                "status": "new" if before is None else "modified" if changed else "unchanged",
                "change_detected_at": last_change,
                "previous_change_detected_at": before["change_detected_at"] if before else None,
            }
        )
    current_locators = {section["locator"] for section in sections}
    for locator, before in previous.items():
        if locator not in current_locators:
            changes.append(
                {
                    "locator": locator,
                    "status": "removed",
                    "change_detected_at": detected_at,
                    "previous_change_detected_at": before["change_detected_at"],
                }
            )
    return current, changes

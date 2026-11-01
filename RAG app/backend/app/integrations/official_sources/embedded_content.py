import json
import logging

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def sitecore_sections(soup):
    # Read only known article components from embedded Next.js/Sitecore data, never navigation or scripts.
    script = soup.find("script", id="__NEXT_DATA__", type="application/json")
    if not script:
        return []
    try:
        data = json.loads(script.string or script.get_text())
        placeholders = data["props"]["pageProps"]["layoutData"]["sitecore"]["route"]["placeholders"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []
    sections = []

    def plain(value):
        # Convert CMS rich text into inert evidence text without executing markup.
        return BeautifulSoup(value, "html.parser").get_text(" ", strip=True) if isinstance(value, str) else ""

    def field_text(field):
        # Unwrap known CMS text fields without traversing links, media, or analytics.
        if not isinstance(field, dict):
            return ""
        return plain((field.get("jss") or field.get("field") or field).get("value"))

    def add_item(item, description_fields=("description",)):
        # Keep each article/FAQ/service section under its original heading.
        title = field_text(item.get("title"))
        body = "\n".join(filter(None, [field_text(item.get(key)) for key in description_fields]))
        if body:
            sections.append({"locator": title or "Article section", "text": f"{title}\n{body}".strip()})

    def visit(value):
        # Limit extraction to documented rich-text and step-accordion components.
        if isinstance(value, list):
            for child in value:
                visit(child)
        elif isinstance(value, dict):
            fields = value.get("fields") or {}
            if value.get("componentName") == "RichText":
                text = plain((fields.get("text") or {}).get("value"))
                if text:
                    sections.append({"locator": "Introduction", "text": text})
            elif value.get("componentName") == "AccordionSteps":
                children = ((fields.get("data") or {}).get("item") or {}).get("children") or []
                for child in children:
                    title = plain(((child.get("title") or {}).get("jss") or {}).get("value"))
                    description = plain(((child.get("description") or {}).get("jss") or {}).get("value"))
                    if title and description:
                        sections.append({"locator": title, "text": f"{title}\n{description}"})
            elif value.get("componentName") == "SectionDetail":
                add_item(((fields.get("data") or {}).get("item") or {}), ("description1", "description2"))
            elif value.get("componentName") in ("StepCards", "DetailsCardService", "AccordionFAQ"):
                item = (fields.get("data") or {}).get("item") or {}
                add_item(item)
                entries = (
                    item.get("cards")
                    or item.get("children")
                    or (item.get("items") or {}).get("targetItems")
                    or []
                )
                for entry in entries:
                    add_item(entry)
            for child in (value.get("placeholders") or {}).values():
                visit(child)
            if "componentName" not in value:
                for child in value.values():
                    visit(child)

    visit(placeholders)
    if sections:
        logger.info("event=embedded_content_extracted sections=%s", len(sections))
    return sections

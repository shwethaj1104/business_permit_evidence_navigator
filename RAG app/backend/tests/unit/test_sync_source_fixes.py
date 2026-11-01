import json
from types import SimpleNamespace

from app.integrations.official_sources.extractor import extract
from app.integrations.openai.client import provider_error


def test_article_accordion_embedded_content_is_retrieved_without_navigation():
    # Extract official setup steps hidden from initial HTML without indexing unrelated CMS fields.
    step = {
        "title": {"jss": {"value": "Select business activities"}},
        "description": {"jss": {"value": "<p>Choose primary and secondary activities.</p>" * 8}},
    }
    components = [
        {"componentName": "HeaderGenericTertiary", "fields": {"text": {"value": "NAVIGATION_SENTINEL"}}},
        {"componentName": "AccordionSteps", "fields": {"data": {"item": {"children": [step]}}}},
    ]
    route = {"placeholders": {"root": components}}
    data = {"props": {"pageProps": {"layoutData": {"sitecore": {"route": route}}}}}
    raw = (
        "<html><head><title>Official guide</title></head><body><main>Short introduction</main>"
        '<script id="__NEXT_DATA__" type="application/json">' + json.dumps(data) + "</script></body></html>"
    ).encode()
    doc = extract(raw, "text/html")
    assert "Select business activities" in doc.text
    assert "NAVIGATION_SENTINEL" not in doc.text
    assert doc.published is None
    assert doc.sections[0]["locator"] == "Select business activities"


def test_generation_model_access_error_is_actionable():
    # Differentiate unavailable model access from billing or network errors.
    exc = SimpleNamespace(status_code=404, code="model_not_found")
    error = provider_error(exc, "generation", "gpt-4.1-nano")
    assert "404/model_not_found" in error.message
    assert "gpt-4.1-nano" in error.message


def test_quota_error_has_specific_billing_hint():
    # Tell exhausted quota apart from ordinary temporary rate limiting.
    error = provider_error(SimpleNamespace(status_code=429, code="insufficient_quota"), "embeddings", "test")
    assert "quota" in error.message
    assert "billing" in error.message


def test_service_and_faq_components_are_extracted_as_evidence():
    # Capture substantive service/FAQ fields while continuing to exclude navigation and analytics.
    from bs4 import BeautifulSoup

    from app.integrations.official_sources.embedded_content import sitecore_sections

    child = {
        "title": {"jss": {"value": "Documents required"}},
        "description": {"jss": {"value": "<p>Specific documents depend on the licence type.</p>"}},
    }
    component = {"componentName": "DetailsCardService", "fields": {"data": {"item": {"children": [child]}}}}
    route = {"placeholders": {"root": [component]}}
    data = {"props": {"pageProps": {"layoutData": {"sitecore": {"route": route}}}}}
    soup = BeautifulSoup(
        '<script id="__NEXT_DATA__" type="application/json">' + json.dumps(data) + "</script>", "html.parser"
    )
    sections = sitecore_sections(soup)
    assert sections[0]["locator"] == "Documents required"
    assert "Specific documents" in sections[0]["text"]

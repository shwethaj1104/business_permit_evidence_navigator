from dataclasses import replace
from types import SimpleNamespace

import httpx
import pytest
from openai import BadRequestError

from app.core.errors import AppError
from app.integrations.official_sources.discovery import OfficialDiscovery
from app.models.domain import PROFILE


def test_discovery_preserves_domain_filters_and_uses_low_reasoning(model, settings):
    # Search settings must stay separate from chat's minimal reasoning and filter before limiting results.
    model.settings = replace(settings, discovery_model="gpt-5-nano")
    sources = [SimpleNamespace(url="https://u.ae.evil.test/unsafe", title="Unsafe")]
    sources.extend(
        SimpleNamespace(url=f"https://u.ae/guide-{index}", title=f"Guide {index}") for index in range(8)
    )
    model.client.responses.create.return_value = SimpleNamespace(
        output=[
            SimpleNamespace(
                type="web_search_call", status="completed", action=SimpleNamespace(sources=sources)
            )
        ]
    )
    results = OfficialDiscovery(model).discover(PROFILE)
    arguments = model.client.responses.create.call_args.kwargs
    assert arguments["reasoning"] == {"effort": "low"}
    assert arguments["model"] == "gpt-5-nano"
    assert arguments["tools"][0]["filters"]["allowed_domains"] == ["investindubai.gov.ae", "u.ae"]
    assert len(results) == 5
    assert all(row["url"].startswith("https://u.ae/") for row in results)


def test_unsupported_filter_error_is_actionable_without_removing_filters(model):
    # Do not silently broaden search when a provider rejects the allowlist option.
    request = httpx.Request("POST", "https://api.openai.com/v1/responses")
    model.client.responses.create.side_effect = BadRequestError(
        "SECRET_PROVIDER_BODY",
        response=httpx.Response(400, request=request),
        body={"message": "Parameter 'filters' not supported with model 'gpt-4.1-mini'"},
    )
    with pytest.raises(AppError, match="does not support official-domain filters") as caught:
        OfficialDiscovery(model).discover(PROFILE)
    assert "SECRET_PROVIDER_BODY" not in caught.value.message
    assert model.client.responses.create.call_count == 1


def test_discovery_requires_a_completed_search_call(model):
    # An incomplete/model-only response must not be reported as successful discovery.
    model.client.responses.create.return_value = SimpleNamespace(output=[])
    with pytest.raises(AppError, match="did not complete"):
        OfficialDiscovery(model).discover(PROFILE)

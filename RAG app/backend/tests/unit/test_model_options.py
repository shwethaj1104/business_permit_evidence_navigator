from app.integrations.openai.client import generation_options


def test_nano_uses_supported_minimal_reasoning():
    # Apply cost-conscious GPT-5 nano settings to both alias and pinned snapshots.
    assert generation_options("gpt-5-nano") == {"reasoning": {"effort": "minimal"}}
    assert generation_options("gpt-5-nano-2025-08-07") == {"reasoning": {"effort": "minimal"}}


def test_other_models_do_not_inherit_nano_settings():
    # Do not silently apply an incompatible reasoning option to another model family.
    assert generation_options("gpt-4.1-nano") == {}
    assert generation_options("gpt-5.6-luna") == {}

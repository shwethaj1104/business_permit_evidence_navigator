import argparse
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI, OpenAIError

from app.core.config import ROOT, get_settings
from app.integrations.openai.client import generation_options, provider_error
from app.models.domain import GeneratedSummary


def check(label, operation, model):
    # Report safe status metadata without exposing keys, prompts, vectors, or provider bodies.
    try:
        result = operation()
    except OpenAIError as exc:
        print(f"{label}: FAIL — {provider_error(exc, label, model).message}")
        return None
    print(f"{label}: OK")
    return result


def main():
    # List visible models for free; run tiny billable endpoint checks only when explicitly requested.
    parser = argparse.ArgumentParser(description="Check configured OpenAI model/endpoint access safely.")
    parser.add_argument(
        "--probe",
        action="store_true",
        help="Make one tiny embedding and structured Responses call (API usage applies).",
    )
    parser.add_argument(
        "--compare-chat",
        action="store_true",
        help="Also test Chat Completions with the same generation model (API usage applies).",
    )
    args = parser.parse_args()
    settings = get_settings()
    if not settings.openai_key:
        parser.error("Set OPENAI_API_KEY in the root .env first.")
    file_key = dotenv_values(ROOT / ".env").get("OPENAI_API_KEY")
    print("Generation model:", settings.model)
    print("Embedding model:", settings.embedding_model)
    print("Loaded key matches root .env:", settings.openai_key == file_key)
    with OpenAI(api_key=settings.openai_key, timeout=30, max_retries=0) as client:
        print("Provider endpoint host:", urlsplit(str(client.base_url)).hostname)
        models = check("List models", client.models.list, "model catalogue")
        if models is not None:
            for name in sorted(row.id for row in models.data):
                print(" -", name)
        else:
            print("Model listing can be denied separately; this alone does not establish inference access.")
        if args.probe:
            result = check(
                "Embeddings",
                lambda: client.embeddings.create(
                    model=settings.embedding_model,
                    input="Model access test",
                    dimensions=settings.embedding_dimensions,
                ),
                settings.embedding_model,
            )
            if result is not None:
                print("Embedding dimensions:", len(result.data[0].embedding))
            result = check(
                "Responses structured generation",
                lambda: client.responses.parse(
                    model=settings.model,
                    **generation_options(settings.model),
                    input="Summarize in five words: A new official guide was captured.",
                    text_format=GeneratedSummary,
                    max_output_tokens=1000,
                    store=False,
                ),
                settings.model,
            )
            if result is not None:
                print("Structured output parsed:", result.output_parsed is not None)
        if args.compare_chat:
            check(
                "Chat Completions",
                lambda: client.chat.completions.create(
                    model=settings.model,
                    messages=[{"role": "user", "content": "Reply with OK."}],
                    max_completion_tokens=1000,
                    **({"reasoning_effort": "minimal"} if generation_options(settings.model) else {}),
                    store=False,
                ),
                settings.model,
            )


if __name__ == "__main__":
    main()

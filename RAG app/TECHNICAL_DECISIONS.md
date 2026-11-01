# Technical decisions

Status: local frontend/backend implemented; live Atlas/OpenAI integration and authoritative scope validation pending.
Recorded: 25 October 2026.

## Product and scope
UAE Business Permit Evidence Navigator: a guided RAG chatbot that produces evidence-backed preparation checklists. Initial domain: IT / software development, Dubai mainland, new application, with a provisional LLC structure. Each dropdown initially has one available value plus an unselected placeholder. The same shared profile configuration drives both tabs. Exact official activity code, applicability of the legal structure, and authoritative sources must be verified before publishing licensing checklists. This profile is a development scope, not a verified licensing classification.

## Stack
- Frontend: React + TypeScript; approximately 30% profile panel and 70% chat panel on desktop.
- Backend: Python + FastAPI + Pydantic.
- Persistence: one managed MongoDB Atlas application database, provisionally named `permit_navigator`.
- Search: Atlas keyword and vector search; no separate vector database.
- Original files: MongoDB GridFS within the same database; no separate object-storage service in v1.
- Processing: separate Python worker using a MongoDB-backed queue. No Redis requirement.
- Provider: OpenAI. Generation configuration now uses `MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")` per the 27 October user selection.
- Embeddings: OpenAI `text-embedding-3-small` as the initial default, configurable separately using `OPENAI_EMBEDDING_MODEL`. Generation and embeddings serve different purposes.
- Secrets: root `.env` contains `OPENAI_API_KEY` and `MONGODB_URI`; user fills these after setup. Commit `.env.example`, never `.env`. Load environment variables in the backend only, never into the React bundle.
- Authentication/login/roles: excluded from v1. Both tabs and review actions are open within the local application.
- Run frontend/API on loopback for this local-only build. Hosting, styling library, and final retrieval framework remain unselected.

## Runtime boundaries
1. Checklist Assistant uses only approved, active evidence in MongoDB. It has no web-search or website-fetching tools. Calling a hosted model to generate an answer is distinct from browsing.
2. Knowledge Updates is open in the local application. Sync starts only after a manual button action; no login or administrator checks in v1.
3. The ingestion worker may discover and fetch official sources within approved domains and the selected scope.
4. No scheduler is implemented or enabled in v1. Future scheduling will reuse the ingestion pipeline.
5. Inadequate evidence produces a knowledge-gap response, not a model-generated licensing requirement.
6. Users may open saved official citation URLs; this is not a chatbot web call.

## UI behavior
Both tabs read one shared profile definition; adding domains later extends that definition. Initially there is one value in each single-select dropdown: emirate, mainland/free zone, specific free zone if applicable, exact activity, application type, and legal structure. Expose supported combinations only. Allow introductory messages before selection. Enable Generate my checklist only when all five required selections are complete. Further business details can be collected in chat. Changing a profile marks previous answers as belonging to the old profile.

Knowledge Updates shows job progress, source/category, new/modified/unchanged status, short change summary, dates, section comparisons, and review/publish decisions. Closing the UI does not stop the job.

## Collections
| Collection | Responsibility / important fields |
|---|---|
| `business_profiles` | Valid dropdown combinations; emirate, jurisdiction, authority, activity code/name, legal structure, application type, coverage status |
| `sources` | Official URL, approved domain, title, authority, category/profile associations, last check, last successful fetch, active version reference |
| `document_versions` | Source reference, immutable normalized content/version hash, GridFS original reference, extracted content metadata, dates, review state, extraction version |
| `chunks` | Version/source references, section/page locator, text, embedding, embedding model/dimensions, profile filters, content hash |
| `update_runs` | Selected scope, local requester label, job state, lease, attempts, progress, errors, per-source outcomes and processing checkpoints |
| `change_records` | Previous/new versions, section differences, affected categories, generated summary, review decision timestamps (no authenticated reviewer in v1) |
| `conversations` | Anonymous conversation ID, profile, title, preview, timestamps, and message-count allocation |
| `conversation_messages` | Ordered user/assistant messages, structured answers, and immutable citation snapshots |
| `fs.files`, `fs.chunks` | GridFS-managed file metadata and binary segments; distinct from application retrieval `chunks` |

Messages now live in `conversation_messages`; cursor pagination bounds responses without deleting history. Legacy embedded messages remain readable. Use an anonymous conversation ID for local continuity. There are no accounts or per-user access guarantees in v1.

## Dates and provenance
Store timestamps in UTC and display them in the user's timezone. Preserve the raw source date, its location, and its precision when a source supplies only a calendar date.

| Field | Meaning |
|---|---|
| `source_published_at` | Publication date explicitly stated by the source, nullable |
| `source_updated_at` | Source-stated update date, nullable |
| `effective_from` | Explicit requirement effective date, nullable |
| `fetched_at` | Time our worker obtained a particular snapshot |
| `change_detected_at` | Time our system first observed changed content |
| `reviewed_at` | Time a local user reviewed the version |
| `activated_at` | Time approved evidence became available to chat |
| `last_checked_at` | Most recent check attempt; track success/failure separately |

A fetch date never becomes an inferred publication or effective date. HTTP Last-Modified may be retained as a technical hint, not proof of a regulatory change date. If an edit time is unknown, report the observation interval between the prior successful check and detection. Unchanged sections retain their historical change attribution.

## Versioning and publication
- Preserve original snapshots and prior versions used by answers.
- Compare normalized content hashes before invoking embeddings or change summarization. Metadata-only changes should remain distinguishable from substantive requirement changes.
- Changed content is staged for review; rejection preserves the prior approved active version.
- Keep approval, activation, and effective dates distinct. Future-effective requirements must be labeled and must not silently replace current requirements.
- Build/index staged evidence before activation. Search indexes can lag writes; confirm readiness before publishing.
- Capture active version references for retrieval and revalidate retrieved chunks against authoritative version records before generation, so stale index flags cannot expose rejected or superseded evidence.
- Preserve exact citations for historical answers even after a new version is activated.

## Retrieval and answer generation
Filter by jurisdiction, authority, activity, application type, and applicable structure before retrieval. Combine keyword and vector results, then check sufficiency. Answer as a follow-up, supported checklist, or explicit evidence gap. Each requirement includes its condition, authority, and supporting citation. Known applicability conditions must be enforced in backend logic rather than relying solely on prompts. The precise representation of structured applicability rules will be finalized with the first reviewed source set.

## Jobs, access, and cost
- API creates a durable job and returns an ID; UI polls status in v1.
- Worker atomically claims jobs with leases; expired leases permit recovery. Steps must be idempotent, with bounded retries and duplicate-scope protection.
- No authentication or authorization in the local-only version. Keep review/publish as explicit actions. Authentication is a future requirement before shared/public hosting.
- Validate fetch targets and redirects to avoid access to internal/private network destinations.
- Keep database/model/search credentials server-side and out of logs.
- Use restricted service credentials; separate chat and ingestion permissions where practical.
- Manual sync avoids recurring discovery costs. Embeddings, summaries, and chat still consume model usage. Skip unchanged work and record usage per job/request.
- Retention, backup tier, rate limits, evaluation thresholds, and hosting sizing remain implementation decisions.

## Future enhancements
- Scheduled sync; excluded from v1.
- Additional domains/profiles.
- Authentication and authorization if shared deployment is introduced.

## Delivery order
1. Confirm narrow coverage and official source registry.
2. Bootstrap React, FastAPI, MongoDB connectivity, and configuration.
3. Manually ingest and version one source.
4. Review/publish and return one cited answer.
5. Demonstrate changed-source comparison and safe publication.
6. Complete UI, evaluations, operational controls, and local startup documentation.

## Diagram
See `WORKFLOW.svg` for the visual architecture and `WORKFLOW.mmd` for editable Mermaid source. Scheduler is shown only as a future enhancement.

## Official model references
- https://developers.openai.com/api/docs/models/gpt-4.1-nano
- https://developers.openai.com/api/docs/models/text-embedding-3-small

## Required code organization
See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for the target tree and strict layer responsibilities. Backend request flow: routes → controllers → services → repositories/integrations. API schemas and persistence/domain models remain separate. The worker reuses services directly. Frontend is organized by feature with shared profile controls and HTTP handling. Layered application code is implemented; see README for local startup.

## Frontend state and API organization
Redux Toolkit + React Redux with RTK Query. Central `store/` configuration; feature-level API endpoint files, slices/reducers, and selectors. Shared reusable code lives in `frontend/src/common/`. One RTK Query base API is extended by feature endpoint modules. RTK Query owns server data; slices hold shared client selections. See `PROJECT_STRUCTURE.md` for the full tree and dependency rules. Redux Toolkit, RTK Query, slices, selectors, and typed hooks are implemented.

## Implementation notes — 25 October 2026
- Manual sync defaults to fetching registered source URLs; optional discovery uses `OPENAI_SEARCH_MODEL=gpt-4.1-mini` because hosted search requires a compatible model. Chat and summaries preserve `OPENAI_MODEL=gpt-4.1-nano`.
- Atlas database initialization is an explicit command, not an API-startup side effect. Approval checks keyword/vector availability and commits review state plus the active source pointer in one transaction.
- Queue polling is worker infrastructure, not a source scheduler. Source refresh never starts merely by opening either tab.
- General-setup seed URLs are starting evidence only. The activity code and provisional LLC applicability remain unverified. No claim of complete UAE licensing coverage is made.
- Snapshot comparisons are document-level text differences. Section/page observation-date lineage is implemented; renamed headings appear as removed/new sections. Detailed structured applicability rules and future-effective requirement activation remain pending. Source effective dates remain null unless a later reviewed implementation supplies them.
- Frontend styling uses reusable CSS and Lucide icons. No LangChain dependency is needed for this direct RAG implementation.
- Dependency checks and mocked tests pass locally; real Atlas indexing/transactions and OpenAI responses are not yet validated. Consult the checklist for remaining work.

## Console diagnostics and saved chats
- Central safe logging includes HTTP method/route/status/duration and generated request IDs. Responses expose `X-Request-ID`; frontend RTK Query failures log the same ID when available.
- Services and integrations log timed stage boundaries. Worker processing carries job/source IDs; failures include exception types, safe error codes, controlled application hints, and file/function/line locations. Raw provider exception text, bodies, prompts, secrets, and document contents are excluded.
- `LOG_LEVEL` defaults to INFO. Idle queue polls are not logged as successful jobs; no model calls are introduced by logging.
- The right-hand chat workspace includes saved conversations, new chat, reopen, and cursor-based earlier-message loading. All chat actions require mandatory profile selections.
- New messages are stored individually with ordered slots. Existing embedded messages are read compatibly; prior deleted data cannot be reconstructed. Forty messages is now a page size, not a retention limit.

## First real sync diagnostics — 27 October 2026
Registered sources are curated URL seeds, not fixed document content. Website text is fetched during manual sync; optional discovery is separate. Dubai's setup page has embedded Sitecore article/AccordionSteps data that is now parsed directly from the fetched HTML without executing scripts or indexing navigation. A live minimal generation check returned 404/model_not_found with the configured gpt-4.1-nano; no automatic model substitution was introduced. Embeddings are checkpointed before summaries so a retry can reuse successful paid work while unfinished evidence remains inactive.

## User-selected GPT-5 nano — 27 October 2026
Generation/default and `.env` now use `gpt-5-nano`, with model-specific minimal reasoning. Embeddings remain `text-embedding-3-small`; no vectors or indexes require migration. Optional web discovery retains its separate model. Historical diagnostics above describe the retired former generation model. Retirement for the selected GPT-5 nano is scheduled for 11 December 2026.

Validation: the user-selected gpt-5-nano passed a live structured Responses probe with minimal reasoning; the embedding probe also passed. Model-list 403 remains separate. Forty automated backend tests pass.

## Discovery request compatibility — 27 October 2026
Confirmed provider error: HTTP 400, `Parameter 'filters' not supported with model 'gpt-4.1-mini'`. Search configuration/default now uses gpt-5-nano with low reasoning. Chat retains gpt-5-nano with minimal reasoning, and embeddings are unchanged. Keep the official domain allowlist at the provider and validate returned URLs locally before applying the five-source cap. Never retry without filters. Failed/incomplete search calls are not counted as successful discovery. Error mapping now distinguishes tool-filter incompatibility from permissions, quota, and model access failures.

Validation: the fixed discovery adapter returned five validated official URLs in a live filtered-search check. No new source records or approvals were created by that diagnostic. All 43 backend tests pass.

## Source freshness state clarification — 27 October 2026
A registered URL without an active version is not necessarily pending approval. Source responses now expose latest-version status and last-capture outcome/error. Historical failed captures are reconstructed from recent job outcomes; future outcomes are stored on each source. The UI displays failure reasons and a Review version action only when a real pending version exists. Embedded article/service/FAQ extraction now supports the components observed in the discovered mainland and trade-licence pages. General homepage text remains excluded. No source evidence or approval was changed during diagnostics; re-sync is required to create new versions. One existing discovered URL is a query-string duplicate of the mainland guide; discovery curation/deduplication remains an improvement area.


### Chat-first onboarding

Chat history is on the left; the shared profile selector is embedded in the assistant conversation and remains a sidebar in Knowledge Updates. Introductory conversations use a nullable `profile_id`; their welcome replies are deterministic and persisted without OpenAI calls. A complete profile binds to the existing conversation on its first evidence request. Once bound, profile changes require a new conversation. History can list all profiles, including introductory chats, with existing cursor pagination. New chat clears the active reference and selections while retaining saved history. Licensing guidance continues through the approved-evidence RAG pipeline without chat web search.

### Conversation actions and shared profile controls

PATCH `/api/v1/chat/conversations/{id}` validates and saves a trimmed title (1–80 characters). DELETE on the same path removes conversation metadata and its separate message records; unrelated knowledge and conversations remain intact. Both operations return 204 and use existing safe operation/request logging. The frontend refreshes saved-chat navigation after either action and resets the active reference after deletion.

Profile controls use the shared `SelectField` component in both tabs. Options expand in normal document flow, with listbox semantics, keyboard navigation and focus management, rather than native browser popups. The shared five-field selection and generation gating remain unchanged.

### On-demand Azure sync dispatch

`SYNC_DISPATCH_MODE=azure` adds a post-persistence dispatch step using the API managed identity. It reads the configured Manual Azure Job's complete template, overrides the command to `python -m app.workers.sync_worker --job-id <id>`, and starts an execution through ARM API version 2025-01-01. Azure dependencies are an optional package extra. The existing local mode remains the default. MongoDB leases ensure exclusive processing; a two-minute launch reservation reduces duplicate executions. No background recovery scheduler is added: failures and expired leases are recovered through explicit manual retry. See `AZURE_SYNC_SETUP.md` for configuration and limitations.

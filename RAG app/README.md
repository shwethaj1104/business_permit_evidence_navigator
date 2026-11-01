# Business Permit Evidence Navigator

A local UAE business-setup evidence workspace with a React/Redux frontend, FastAPI API, independent Python worker, and one MongoDB Atlas database. There is no login and no scheduled source sync.

## Current scope

Dubai mainland → IT / software development → new application → provisional LLC. Both tabs share this one profile. The exact official activity code and activity-specific requirements are **not verified yet**. The two initial official URLs provide general setup guidance, not a complete IT licensing checklist. No sample checklist is passed off as official evidence.

## Prerequisites

- Python 3.12–3.14 (tested with 3.12). Python 3.15 is excluded until dependencies are verified.
- Node.js 22.12+ and npm (tested with Node 26).
- MongoDB Atlas with Search/Vector Search and transaction support; no local database needed.
- OpenAI API access and billing for the configured generation and embedding models.

## 1. Configure the backend

Edit the existing root `.env`; use `.env.example` as the reference. Do not put credentials in the frontend or commit them.

```dotenv
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-5-nano
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
MONGODB_URI=your-atlas-connection-string
MONGODB_DB_NAME=permit_navigator
# Optional; only used when discovery is explicitly checked during manual sync.
OPENAI_SEARCH_MODEL=gpt-5-nano
```

`gpt-5-nano` is the generation/change-summary default, with minimal reasoning. Optional hosted web search uses separately configured `gpt-5-nano` with low reasoning; chat continues to use minimal reasoning. Registered-source sync fetches stored URLs without a search-model request. Embeddings currently use 1,536 dimensions. Changing the embedding model/dimensions requires rebuilding compatible vectors/indexes; it is not an automatic migration.

Allow your development IP in Atlas Network Access and give the database user the permissions needed to create collections and indexes. The setup command also creates Atlas search indexes; if your user cannot manage them, create equivalent indexes using an authorized Atlas account. Application code does not create infrastructure on every startup.

From the project root:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m scripts.setup_db
```

For a locked installation with uv instead: run `uv sync --python 3.12 --extra dev` from `backend`, then use `uv run` before the Python commands. `backend/uv.lock` and `frontend/package-lock.json` record dependency resolutions.

Wait for `permit_keywords` and `permit_vectors` on the `chunks` collection to become queryable in Atlas. The application also checks that staged chunks are searchable before approval. Do not run `setup_db` against an unrelated existing database.

## 2. Start the API

In the activated backend terminal:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

API documentation: http://127.0.0.1:8000/docs

The API can start without credentials and serves profile/setup information. Data operations then return an actionable setup message. Restart the API and worker after changing `.env`.

## 3. Start the worker

In a second terminal, from the project root:

```bash
cd backend
source .venv/bin/activate
python -m app.workers.sync_worker
```

The worker processes only manually enqueued jobs. Its queue polling is not a scheduled source refresh. Temporary queue disconnections are retried on the next five-second poll; permanent queue errors expose a safe error code. It renews exclusive job leases, resumes completed source checkpoints after crashes, and bounds crash/restart attempts. Fetch transport errors and OpenAI transport/rate errors have bounded retries. A failed source/job can be retried by starting another manual sync.

## 4. Start the frontend

In a third terminal, from the project root:

```bash
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173. Vite proxies `/api` to the Python backend. Keep this no-auth version bound to loopback.

## First use

1. Select the single available value in each of the five dropdowns.
2. Open **Knowledge updates** and click **Sync official sources**.
3. Leave discovery unchecked to fetch only registered official URLs. Checking it runs a bounded approved-domain web search during this sync only.
4. Watch job outcomes; inspect the captured version, previous content, difference, summary, and dates.
5. Approve a suitable pending version once Atlas has indexed its chunks. Rejected or superseded versions are not activated.
6. Open **Checklist assistant** and generate a checklist or ask a question. Chat has no discovery/fetch adapter and uses only approved active database evidence.

New/modified sources incur embedding and summary usage; identical versions skip those calls. Unchanged passage embeddings are reused when compatible. Search discovery is optional. Generation and query embeddings still incur usage when asking questions over active evidence.

A version summary describes observed text differences, not a verified legal change. Unknown publication/update/effective dates remain unknown. A successful source check never becomes an inferred publication date. If a newer version exists but has not been activated, citation details flag it explicitly.

## Code organization

Backend: routes → controllers → services → repositories/integrations. API request/response schemas are separate from internal models. HTTP and worker entry points reuse services.

Frontend: shared components/utilities in `common/`, central Redux Toolkit store, feature-specific components, separate RTK Query endpoint files, slices, and selectors. RTK Query owns server data; slices keep shared client selections.

See `PROJECT_STRUCTURE.md`, `TECHNICAL_DECISIONS.md`, `DEVELOPMENT_CHECKLIST.md`, and `WORKFLOW.svg` for architecture details. Each implemented function/service/endpoint has a brief purpose comment or docstring.

## Verification

```bash
cd backend
source .venv/bin/activate
pytest -q
ruff check app scripts tests
ruff format --check app scripts tests
```

```bash
cd frontend
npm run build
npm run lint
npm run format:check
```

Backend tests use synthetic sources, mocks, and an in-memory Mongo test double. Desktop/mobile UI and an intercepted synthetic sync/review/chat workflow were also checked in headless Chrome. They never connect to a local/Atlas database or spend OpenAI tokens. Atlas search execution, transactions, and live provider responses still require a credentialed end-to-end run; the mock tests do not establish those external capabilities.

## What remains before the first real checklist

- Supply `OPENAI_API_KEY` and `MONGODB_URI` locally; confirm Atlas network access and model access.
- Run database setup and verify both Atlas indexes.
- Confirm the exact official activity code/legal structure and supplement general setup sources with authoritative activity-specific material. Source URLs/domains live in `backend/app/models/domain.py`; expand deliberately, then sync/review.
- Perform one real sync → review → approval → cited chat run, and evaluate against a manually reviewed checklist.

Current limits: English text extraction; no OCR/browser-rendered extraction; 10 MB/200-page/250,000-character source limits; no automatic legal-rule extraction or effective-date inference; message history paginated in pages of 40, and 100 recent version summaries in the review API. Side-by-side comparisons use document snapshots and line diffs. Section/page observation dates are retained across versions; heading renames appear as removed/new sections. Per-section regulatory effective dates are not inferred. All local visitors share open access; anonymous conversation IDs are not an authorization mechanism.

## Future enhancements

Scheduled sync, more verified business profiles, reviewer notifications, richer section/applicability modeling, and authentication if shared hosting is introduced.

## Saved chats
The right-hand chat panel lists persisted conversations for the selected profile. Complete all five selections to enable New chat, Generate checklist, Send, and reopening. Use Load more chats or Load earlier messages to access older history. New chat clears the active view without deleting prior conversations. MongoDB stores metadata in `conversations` and individual messages/citation snapshots in `conversation_messages`; existing embedded messages remain readable.

## Console logs
Restart the worker after code changes; the API restarts itself when launched with `--reload`. API and worker terminals now print timestamp, severity, module, request/job/source IDs, stage, duration, and safe failure diagnostics. Frontend API failures appear in the browser developer console as `[Permit API failed]` with endpoint, method, status, duration, and the matching backend request ID.

Example (illustrative):
```text
INFO app.core.logging request=abc123 job=- source=- event=request_finished method=POST route=/api/v1/chat status=200 duration_ms=850.0
ERROR app.core.logging request=- job=job-id source=source-id event=failed stage=sources.fetch errors=type=AppError ...
```

`LOG_LEVEL=INFO` is the default; set it in root `.env` and restart processes to change verbosity. Raw request bodies, prompts, provider response bodies, credentials, and source content are not logged. Application hints are controlled errors; stack diagnostics show file/function/line locations without local-variable values. No paid provider calls are made merely by logging or opening saved history.

## Check OpenAI access
From the activated backend environment:
```bash
python -m scripts.check_models
```
This lists models visible to the current key without generating text or embeddings. Listing may require permissions separate from inference. For minimal billable endpoint probes:
```bash
python -m scripts.check_models --probe --compare-chat
```
This tests the configured embedding model, structured Responses generation, and the same generation model through Chat Completions. It never prints the key, prompts, returned text, or vectors, and never changes `.env`. On 27 October 2026 the current credentials passed text-embedding-3-small (1,536 dimensions), returned 404 for gpt-4.1-nano on both generation endpoints, and returned 403 for model listing. Check API-key/project permissions rather than changing the working embedding model.

## Selected generation model — 27 October 2026
The user selected `gpt-5-nano`; root `.env`, its template, and the backend fallback now agree. Generation uses `reasoning.effort="minimal"` for this model only; embeddings and optional discovery settings remain unchanged. The diagnostic uses the same reasoning setting and a 1,000-token output ceiling to accommodate reasoning plus structured output. API token usage applies; the ceiling is not a fixed consumption amount. GPT-5 nano is scheduled to shut down on 11 December 2026, so migration will be required before that date.

## Discovery compatibility fix — 27 October 2026
The previous gpt-4.1-mini discovery request returned HTTP 400 because it does not support the requested `filters` parameter. Discovery now defaults to gpt-5-nano with low reasoning, retaining official-domain filtering. A separate live request confirmed a completed filtered search with returned source entries. The change does not affect chat generation, embeddings, active document approvals, or stored history. Restart the worker after updating code/configuration; API reload does not reload the worker. A full discovery-enabled ingestion still requires the normal manual sync and review process.

## On-demand Azure worker

The API can now start a one-shot Azure Container Apps Job after saving a sync request. Set `SYNC_DISPATCH_MODE=azure` only after creating the cloud job and configuring the API managed identity. The default remains `local` so existing development commands continue to work. See [AZURE_SYNC_SETUP.md](AZURE_SYNC_SETUP.md) for setup, permissions, failure recovery, and one-shot local commands. No cloud resources are provisioned automatically.

# Project structure and architecture rules

This is the agreed implementation structure. The runnable API, worker, and React application now use these boundaries. Avoid empty placeholder classes and generic abstractions without a concrete use.

```text
RAG app/
├── frontend/
│   ├── src/
│   │   ├── app/                     # App shell, tabs, Redux provider
│   │   ├── store/
│   │   │   ├── index.ts             # configureStore; exports AppStore/RootState/AppDispatch
│   │   │   ├── rootReducer.ts       # Combines feature reducers and RTK Query reducer
│   │   │   └── hooks.ts             # Typed useAppDispatch/useAppSelector
│   │   ├── common/
│   │   │   ├── components/          # Shared Button, Select, Loader, ErrorState, etc.
│   │   │   ├── hooks/               # Hooks reusable across features
│   │   │   ├── api/
│   │   │   │   └── baseApi.ts       # One RTK Query API; shared base URL/error handling
│   │   │   ├── utils/               # Pure date, formatting, and validation helpers
│   │   │   ├── constants/           # Shared UI constants; no duplicated profile options
│   │   │   └── types/               # Shared API contracts, preferably generated
│   │   ├── features/
│   │   │   ├── business-profile/
│   │   │   │   ├── components/      # ProfileSelectors shared by both tabs
│   │   │   │   ├── api/profileApi.ts
│   │   │   │   ├── store/profileSlice.ts
│   │   │   │   ├── store/profileSelectors.ts
│   │   │   │   └── types/
│   │   │   ├── checklist-chat/
│   │   │   │   ├── components/      # Chat panel, input, checklist, citations
│   │   │   │   ├── hooks/           # Chat orchestration, when needed
│   │   │   │   ├── api/chatApi.ts
│   │   │   │   ├── store/chatSlice.ts
│   │   │   │   ├── store/chatSelectors.ts
│   │   │   │   └── types/
│   │   │   └── knowledge-updates/
│   │   │       ├── components/      # Sync panel, progress, comparison, review
│   │   │       ├── hooks/           # Sync orchestration, when needed
│   │   │       ├── api/updatesApi.ts
│   │   │       ├── store/updatesSlice.ts
│   │   │       ├── store/updatesSelectors.ts
│   │   │       └── types/
│   │   └── styles/                 # Global styles and design tokens
│   ├── public/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application factory and lifecycle
│   │   ├── api/
│   │   │   ├── router.py           # Composes versioned feature routers
│   │   │   ├── dependencies.py     # Dependency injection / composition
│   │   │   └── routes/             # Profiles, chat, sources, sync, review endpoints
│   │   ├── controllers/            # HTTP use-case coordination and DTO mapping
│   │   ├── services/               # Business rules and use cases
│   │   │   ├── retrieval/          # Profile filtering, evidence selection, citations
│   │   │   └── ingestion/          # Fetch processing, diffs, versions, publication
│   │   ├── repositories/           # MongoDB queries and persistence operations
│   │   ├── models/                 # Internal domain and persisted-record models
│   │   ├── schemas/                # Pydantic API request/response contracts
│   │   ├── integrations/
│   │   │   ├── openai/             # Generation and embedding adapters
│   │   │   └── official_sources/   # Discovery, safe HTTP fetching, extraction
│   │   ├── db/                     # Mongo client lifecycle, indexes, GridFS adapter
│   │   ├── core/                   # Settings, logging, domain errors
│   │   └── workers/                # Job polling, leases, retries, shutdown
│   ├── scripts/                    # Explicit setup/index/source-seeding commands
│   ├── tests/
│   │   ├── unit/                   # Pure logic and service behavior
│   │   ├── integration/            # Repository, API, provider-boundary checks
│   │   └── fixtures/               # Synthetic source versions and reviewed examples
│   └── pyproject.toml
├── .env                            # Local secrets; ignored by Git
├── .env.example                    # Documented, blank credential template
├── .gitignore
├── README.md                       # Startup and usage; added with runnable scaffold
├── PROJECT_STRUCTURE.md
├── TECHNICAL_DECISIONS.md
├── DEVELOPMENT_CHECKLIST.md
├── WORKFLOW.mmd
└── WORKFLOW.svg
```

## Backend boundaries — required

Request path:

`Route → Controller → Service → Repository / Integration → MongoDB / external API`

- **Routes:** define URLs, methods, status codes, API schemas, and dependency bindings. No MongoDB queries, prompts, extraction, or business rules.
- **Controllers:** translate validated HTTP requests into service calls and map results into response schemas. Keep them thin. They must not implement retrieval or ingestion logic or call provider SDKs directly.
- **Services:** implement application behavior: supported-profile validation, evidence sufficiency, version comparison, checklist generation, sync processing, and publication rules. No FastAPI request/response objects or `HTTPException` here.
- **Repositories:** own MongoDB queries, atomic claims, updates, and persistence mapping. They return domain/record models, not API responses. No model calls or business decisions.
- **Models:** represent internal domain concepts and persisted records. MongoDB IDs and persistence details must not leak into frontend contracts unintentionally.
- **Schemas:** explicit request/response contracts, distinct from persistence models. Never return raw database documents.
- **Integrations:** encapsulate provider-specific SDKs and HTTP behavior. Generation and embedding adapters are separate from official-source discovery/fetching.
- **Database infrastructure:** owns client connections, index setup, and GridFS. The API and worker each create and close their own process-local client.
- **Workers:** claim durable jobs and invoke ingestion services. They do not call HTTP controllers or duplicate business logic.
- **Core:** validated settings, logging, and reusable errors. Keep it small; avoid making it a miscellaneous business-logic folder.

The composition layer injects repositories and adapters into services. Routes/controllers depend on services, never the reverse. Use small typed interfaces at external boundaries when they improve testability; avoid a universal base repository or base service.

Services raise typed application errors; centralized API handlers translate those into safe HTTP responses. The worker handles the same errors according to retry policy.

## Runtime separation

- Chat service receives retrieval and generation dependencies only. It has no source-discovery or HTTP-fetch dependency.
- Ingestion service receives official-source adapters, embedding generation, change summarization, and persistence dependencies.
- Both tabs load supported values from the same business-profile API/configuration; do not duplicate dropdown constants in each feature.
- No authentication, scheduler, Redis, or second database is introduced in v1.
- Settings load the root `.env` once, using a path independent of the process working directory. No environment reads scattered throughout services.
- Generation setting: `MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")`, centralized in settings after environment loading.
- Keep all secrets in Python processes; frontend uses a relative API path through a development proxy.
- Never perform network requests, create indexes, or launch workers at module import time.

## Frontend boundaries and Redux — required

- Use Redux Toolkit (`@reduxjs/toolkit`) and React Redux, with RTK Query for server state. Resolve current stable compatible versions when installing and commit the dependency lockfile.
- `store/index.ts` configures the store with `configureStore`; `rootReducer.ts` combines feature reducers plus the API reducer. Register RTK Query middleware once. `store/hooks.ts` exports typed dispatch/selector hooks.
- Each feature keeps its API endpoints in `api/*Api.ts`, reducers/actions in `store/*Slice.ts` using `createSlice`, and selectors in separate `store/*Selectors.ts` files. No HTTP calls inside reducers.
- `common/api/baseApi.ts` creates a single API instance for the FastAPI backend. Feature endpoint files extend it using `injectEndpoints`; do not create a separate API cache/middleware for each feature.
- Components invoke generated API hooks or feature hooks. URLs, request construction, response mapping, cache tags, and invalidation belong in API files. No ad hoc `fetch`/Axios calls inside presentation components.
- RTK Query owns fetched profiles, conversations, sync status, versions, and change records. Avoid copying server responses into ordinary slices. Use slices for shared client state such as selected profile, selected conversation ID, and comparison filters; local component state is sufficient for transient input text.
- Invalidate relevant cache tags after sync/review/publication. Poll only active sync jobs, stop on terminal states, and clean up subscriptions when the tab unmounts. Disable polling when unfocused where appropriate.
- Shared reusable components, hooks, utilities, constants, and types live under `common/`. Feature-specific components stay in that feature's `components/` directory. Shared modules must not import feature internals or the store singleton.
- Both tabs reuse the business-profile feature rather than storing separate dropdown definitions. Server-side profile validation remains authoritative.
- Use type-only imports for RootState/AppDispatch where needed to avoid runtime cycles. Do not import the configured store into API modules.
- Use typed contracts aligned with FastAPI OpenAPI; centralize loading, error, date-formatting, and safe citation-link behavior.
- Add only slices/hooks needed by implemented behavior; the tree above describes intended responsibilities, not a requirement for placeholder files.

Official references: [Redux style guide](https://redux.js.org/style-guide/) and [RTK Query endpoint splitting](https://redux.js.org/toolkit/rtk-query/usage/code-splitting).

## Quality gates

- Validate configuration and API input; handle missing credentials with actionable errors.
- Use bounded timeouts/retries and consistent application errors. Never log credentials or full connection strings.
- Test consequential behavior: evidence isolation, citation validity, idempotent sync, lease recovery, publication/version selection, and date provenance.
- Check frontend types/build and backend formatting/linting with the runnable implementation.
- Keep documentation and both diagram formats aligned when architecture changes.
- This structure supports maintainability; production readiness still requires implementation, verification, and operational checks. The current run target remains local-only.

## Implemented entry points
- Frontend: `frontend/src/main.tsx` and `frontend/src/app/App.tsx`.
- HTTP API: `backend/app/main.py`.
- Worker: `backend/app/workers/sync_worker.py`.
- Database setup: `backend/scripts/setup_db.py`.
- Dependency locks: `backend/uv.lock` and `frontend/package-lock.json`.
- Current internal records use a domain `Record` model and explicit API schemas. Richer per-collection domain types can be added as applicability rules expand.

## Saved-chat and diagnostics additions
`ChatHistory.tsx` owns saved-chat navigation; `chatApi.ts` owns cursor endpoints and server-cache merging. `conversation_repository.py` stores metadata separately from `conversation_messages`. Shared backend tracing lives in `core/logging.py`; shared browser failure logging lives in `common/api/baseApi.ts`.

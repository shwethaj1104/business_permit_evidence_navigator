# Development checklist

Updated: 25 October 2026. Checked means implemented and locally verified where applicable; it does not imply that Atlas/OpenAI live integration has passed. No paid API calls were made during development. Latest verification: 48 backend tests passed; frontend build/lint/format and backend lint/format passed.

## 1. Scope and requirements
- [x] One shared Dubai mainland IT/software-development development profile in both tabs.
- [x] One available option per dropdown, plus an unselected placeholder.
- [x] New application and provisional LLC scope; no login/roles or scheduler.
- [x] OpenAI provider with configurable `gpt-4.1-nano`; separate embedding model.
- [x] Register two official general-setup URLs and restrict discovery/fetch domains.
- [ ] Verify exact official activity code and legal-structure applicability.
- [ ] Add and review sufficient activity-specific official sources.
- [ ] Prepare a manually reviewed reference checklist and representative evaluation dataset.

## 2. Project and configuration
- [x] Separate frontend/backend packages and layered architecture.
- [x] Backend-only root `.env` loading, `.env.example`, and secret ignore rules.
- [x] React/TypeScript and Python dependency manifests and lockfiles.
- [x] Formatting/lint configuration and startup documentation in README.
- [ ] User supplies Atlas/OpenAI credentials and confirms external access.

## 3. Frontend — shared
- [x] React/TypeScript two-tab responsive workspace, approximately 30% / 70% desktop layout.
- [x] Common components, helpers, types, and API configuration under `common/`.
- [x] Redux Toolkit store, root reducer, typed hooks, slices, separate selectors, and provider.
- [x] One RTK Query cache, feature API files, request error handling, and cache invalidation.
- [x] Shared profile selector and server-defined options.
- [x] Loading/setup/empty/error states and safe external source links.
- [x] Browser check: gated actions, shared profile, opt-in discovery, and no mobile horizontal overflow.

## 4. Frontend — Checklist Assistant
- [x] Allow welcome messages before selection; require all five profile selections for checklist generation.
- [x] Generate checklist action, message input, and new conversation action.
- [x] Structured checklist, follow-up and gap rendering, and expandable evidence citations.
- [x] Publication/update/fetch/check dates and immutable evidence-version references.
- [x] Warn when a newer captured version is not active.
- [x] Prevent reuse of a conversation under a changed profile.
- [ ] Validate real model-generated answers against reviewed reference requirements.

## 5. Frontend — Knowledge Updates
- [x] Manual sync button and optional official-source discovery checkbox.
- [x] Durable job progress, per-source results, failure messages, and explicit refresh.
- [x] Poll only active jobs, pause polling when unfocused, and stop on terminal status.
- [x] Source freshness, active/pending counts, and bounded version history.
- [x] Short change summaries and affected pilot category.
- [x] Previous/new captured content and unified text difference.
- [x] Explicit approve/reject actions with search-readiness errors displayed.
- [ ] Verify all states with real Atlas source/version data.

## 6. Backend — FastAPI
- [x] Separate routes, controllers, services, repositories, internal models, and API schemas.
- [x] Shared dependency composition, client lifecycle, and centralized safe HTTP errors.
- [x] Profile and setup/health endpoints work without credentials.
- [x] Chat/history, sync creation/status, source/version, and review endpoints.
- [x] Request size validation and unsupported-profile checks.
- [x] Persistent conversation metadata and separate ordered messages; cursor pages of 40 without retention trimming.
- [x] One-line purpose comments/docstrings for implemented functions and services.

## 7. Ingestion and worker
- [x] Independent worker and Mongo-backed manually queued jobs.
- [x] Exclusive profile job index, atomic lease claims, heartbeat, crash recovery, and attempt cap.
- [x] Source-level checkpoints and idempotent version/chunk/file writes.
- [x] Approved-domain discovery isolated from chat; registered-source fetching needs no search call.
- [x] HTTPS/domain/DNS/redirect checks, bounded streaming, and fetch retries.
- [x] HTML/PDF extraction, PDF page locators, and explicit HTML source-date metadata.
- [x] Content hashing, unchanged detection, and compatible passage-embedding reuse.
- [x] GridFS snapshot storage, source versions, line differences, and grounded short summaries.
- [x] Manual review, superseded pending versions, and atomic approval transaction code.
- [ ] Verify real official-page extraction and handle any source-specific parsing needs.
- [ ] Add OCR/browser-rendered extraction only if the chosen sources require it.
- [x] Track section/page observed-change dates; unchanged sections retain earlier dates.
- [ ] Add structured applicability/effective-date rules after authoritative requirements are reviewed.

## 8. RAG
- [x] Profile/active-version filtering and reciprocal-rank keyword/vector fusion.
- [x] Recheck authoritative active versions against retrieved results and before returning cited items.
- [x] Structured generation with no chat search/fetch tools.
- [x] Citation-ID validation and server-resolved source URLs/excerpts.
- [x] Empty evidence returns a gap without a model call; model instructed to ask follow-ups or report insufficiency.
- [x] Treat retrieved content as untrusted evidence rather than instructions.
- [ ] Measure retrieval recall, requirement support, and answer completeness with real evidence.
- [ ] Add backend-enforced detailed applicability rules once authoritative requirements are reviewed.

## 9. MongoDB Atlas
- [x] Setup command for one database, unique/query indexes, source registration, and Atlas search definitions.
- [x] GridFS adapter and timezone-aware application timestamps.
- [x] Search-index readiness checks before approval and transactional publication implementation.
- [ ] Run setup against the user's Atlas cluster and verify permissions/capabilities.
- [ ] Verify real vector/keyword retrieval and transaction behavior.
- [ ] Configure backups/retention appropriate to the portfolio data.
- [ ] Add collection-level JSON schema validation if strict database-side validation is required.

## 10. Verification and local use
- [x] Backend automated tests for URL restrictions, source dates, unchanged/changed versions, evidence isolation, citation rejection, job recovery, history limits, failed refresh, and HTTP serialization.
- [x] Frontend TypeScript/build, lint, and format checks.
- [x] Backend lint/format checks.
- [x] Desktop/mobile browser smoke check with no JavaScript errors.
- [x] Synthetic browser workflow: manual sync → version details → approval → checklist and citation rendering (intercepted test responses; no paid calls).
- [x] README documents three-process startup and remaining setup.
- [ ] Complete credentialed sync → review → approval → cited answer end-to-end run.
- [ ] Evaluate a real source change and interrupted worker against Atlas.
- [ ] Record a portfolio demo after real evidence and answer quality are validated.

## Future enhancements — excluded from v1
- [ ] Scheduled syncing through the same ingestion pipeline.
- [ ] More verified activities, jurisdictions, structures, and application types.
- [ ] Notifications and richer operational dashboards.
- [ ] Authentication/authorization before shared deployment.

## Worker diagnostic fix
- [x] Separate initial connection errors from errors raised inside a connected session.
- [x] Retry temporary queue connection failures; expose safe permanent-error codes.
- [x] Verify live Atlas ping and queue read access without processing jobs or calling OpenAI.
- [x] Add four regression tests for connection scope and queue errors.

## Saved history and console diagnostics
- [x] Saved chats in the left sidebar, reopening, new chat, and cursor pagination for conversations/messages.
- [x] Preserve loaded earlier messages when sending a follow-up; keep existing embedded history readable.
- [x] Keep New chat and saved history available before selection; gate Generate checklist until all five selections are complete.
- [x] Add message-history indexes in the existing Atlas database.
- [x] API request/status/timing logs with X-Request-ID response correlation.
- [x] Timed service/provider/database stages and worker job/source failure diagnostics.
- [x] Frontend API failure console logs without request/response bodies.
- [x] Logging privacy/context and history retention/pagination regression tests.
- [x] Synthetic browser checks for saved-chat reopening, older-message loading, follow-up cache preservation, mandatory gating, and mobile layout.

## Initial real sync fixes — 27 October 2026
- [x] Confirm registered URLs are curated seeds; dropdown selection never searches the web.
- [x] Extract known article/step components from embedded Next.js/Sitecore data instead of discarding them.
- [x] Verify the actual Dubai source yields 2,635 characters across 13 sections.
- [x] Distinguish OpenAI model access, key, quota, permission, and request errors in safe UI messages.
- [x] Preserve embedding checkpoints across failed summaries; never activate incomplete evidence.
- [ ] Resolve generation model availability: current credentials returned 404/model_not_found for gpt-4.1-nano.
- [ ] Complete a successful credentialed sync and approval after model access is resolved.

## Model access diagnostics — 27 October 2026
- [x] Add `scripts.check_models` for safe model listing and opt-in minimal endpoint probes.
- [x] Verify the loaded API key matches root `.env` without exposing it.
- [x] Verify text-embedding-3-small succeeds with 1,536 dimensions.
- [x] Confirm gpt-4.1-nano returns 404 on both Responses and Chat Completions with current credentials.
- [ ] Resolve 403 model-listing permission and generation-model access in the user's API project.

## GPT-5 nano selection — 27 October 2026
- [x] Set generation in root .env, template, and backend fallback to user-selected gpt-5-nano.
- [x] Use supported minimal reasoning and matching diagnostic settings.
- [x] Live probe: text-embedding-3-small succeeds with 1,536 dimensions.
- [x] Live probe: gpt-5-nano Responses generation succeeds and structured output parses.
- [x] All 40 backend tests pass; lint/format checks pass.
- [ ] Restart API/worker and complete full source sync/approval/chat validation with the new model.
Model-list access still returns 403; it does not prevent the successful inference probes. Prior nano-4.1 access blockers above are historical and superseded by this selection.

## Official-source discovery fix — 27 October 2026
- [x] Reproduce HTTP 400: gpt-4.1-mini rejects the required filters parameter.
- [x] Use GPT-5 nano with low reasoning for discovery while preserving chat minimal reasoning and embeddings.
- [x] Retain provider-side official-domain filters and locally validate URLs before the five-result limit.
- [x] Report filter incompatibility explicitly rather than implying key/billing problems.
- [x] Live fixed-adapter check returned five validated official URLs; no documents were registered/ingested/approved during the diagnostic.
- [x] All 43 backend tests pass, including discovery restrictions and completed-search checks.
- [ ] Restart worker and run a new discovery-enabled sync through the UI; review new sources normally.

## Source capture versus approval — 27 October 2026
- [x] Confirm four discovered URLs had failed extraction and no document versions; original two approved sources remain active.
- [x] Show failed capture reasons separately from pending review and registration status.
- [x] Link pending source rows directly to version approval/rejection controls.
- [x] Support embedded SectionDetail, StepCards, AccordionFAQ, and DetailsCardService article content.
- [x] Verify fetched mainland guide: 6,989 characters/23 sections; trade-licence service: 2,092 characters/5 sections.
- [x] Keep non-substantive homepage content non-reviewable; do not invent evidence or auto-approve.
- [x] All 46 backend tests pass; frontend build and lint pass.
- [ ] Restart worker and manually retry registered-source sync to create pending versions from newly supported pages.


## Chat-first workspace — 27 October 2026

- [x] Remove the introductory marketing banner and use “UAE BUSINESS SETUP ASSISTANT” beneath the logo.
- [x] Left sidebar for saved chats and New chat; restore saved business selections when reopening a configured conversation.
- [x] Warm welcome and five reusable dropdowns inside the conversation; allow introductory messages before selecting a profile.
- [x] Persist introductory turns without model calls; bind the selected profile to the same conversation before evidence retrieval.
- [x] Generate checklist only after all five selections; preserve database-only, reviewed-evidence retrieval.
- [x] Verify desktop/mobile behavior with mocked browser API responses and 48 backend tests; frontend build/lint pass.

## Dropdown styling and page scrolling — 27 October 2026

- [x] Modern rounded profile dropdowns with selection indicators, hover states, and keyboard focus styling in both tabs.
- [x] Sticky application header and tabs with responsive offsets.
- [x] One document scrollbar; remove nested scrolling from chat history, saved chats, evidence excerpts, and document comparisons.
- [x] Frontend build/lint pass; browser checks confirm sticky navigation and no nested content scrollbars in both tabs, with mobile overflow checks.

## Compact chat navigation and styled options — 27 October 2026

- [x] Single-line “Business setup assistant” header with the logo's dark green background.
- [x] Single-line saved chat titles with ellipsis; remove preview and timestamp.
- [x] Three-dot menu with inline rename and confirmed delete, persisted through separate routes/controllers/services/repository methods.
- [x] Deleting the active conversation resets the workspace; deletion removes its messages while preserving other conversations.
- [x] Reusable options panel expands below each profile field without overlapping following fields; white background and brand-green hover/selection.
- [x] Keyboard navigation, Enter selection, Escape dismissal, focus restoration, and blur dismissal.
- [x] 49 backend tests pass; frontend build/lint and backend lint pass. Mocked browser checks cover rename/delete, field expansion, keyboard controls, both tabs, and mobile overflow.

## On-demand sync execution — 1 November 2026

- [x] Save job before Azure dispatch; suppress racing launches through a MongoDB reservation.
- [x] Managed-identity ARM adapter preserves the deployed job template and passes the exact MongoDB job ID.
- [x] Targeted worker claims one job, maintains its lease, closes resources, and exits; retain local polling mode.
- [x] Launch failures remain visible and retriable; expose manual worker-launch retry in Knowledge Updates.
- [x] Add optional Azure dependencies, update lockfile, env template, and Azure setup instructions without changing local secrets.
- [x] 54 backend tests pass, including mocked Azure launch/template, retry, duplicate suppression, and one-shot exit checks.
- [ ] Create Azure resources, assign managed identity permissions, and verify live UI → Azure execution → MongoDB completion.

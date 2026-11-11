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

## Conversational workspace refresh — 4 November 2026

- [x] Replace the legacy presentation with a shared emerald/navy design system, refreshed source/review cards and responsive navigation.
- [x] Show a friendly illustrated professional with a gentle wave on new chat; no initial profile form or disabled questions.
- [x] Reply to greetings first; show all five business questions with radio choices together inside a single assistant message after a relevant request.
- [x] Require a complete supported profile before the questionnaire can submit a checklist request; keep Knowledge Updates dropdowns separate.
- [x] Preserve saved-chat navigation, rename/delete, citations, source counts and approval actions.
- [x] Keep chat bounded to the viewport, scroll messages inside it, and retain the composer; Knowledge Updates uses document scrolling.
- [x] Add keyboard Enter-to-send, mobile history toggle, reduced-motion support, and readable text contrast.
- [x] Classify nontrivial requests server-side before retrieval; return scope refusals for unrelated requests and gaps for unsupported evidence.
- [x] Resolve yes/yes please/sure/okay against the preceding setup offer, including older stored offers; handle no thanks without a refusal loop.
- [x] 75 backend tests pass; frontend build/lint/format and backend lint pass. Mocked browser checks cover the conversation flow, radio gating, citations, review, responsive scrolling and selected accessibility rules.
- [ ] Verify scope-classification quality with real model responses in the deployed environment; unit tests use mocks and do not establish perfect semantic classification.
- [ ] Deploy both updated backend and frontend through the normal PR/CI workflow.


### Seven-emirate reference coverage — 5 November 2026

- Seven selectable mainland IT/software profiles, each with two registered official references: federal guidance and an emirate-specific guide or services page.
- Existing Dubai source IDs and approvals are preserved; new source IDs include the profile so shared federal URLs cannot mix evidence between emirates.
- Run `cd backend` then `python -m scripts.setup_db` after activating the virtual environment to register all 14 links in Atlas. This does not fetch documents, call OpenAI, or approve evidence. No new collections are needed.
- Sync and review each emirate manually in Knowledge Updates before expecting an evidence-backed checklist. Uncaptured or insufficient evidence remains a gap.
- RAK uses its official government business-services directory; Umm Al Quwain uses its DED services catalogue. These are starting references, not verified complete software-licensing instructions. Both sites timed out during live verification; capture may fail and require replacement with a reachable official service page.


### Mint workspace refresh — 9 November 2026

- [x] Reference-inspired mint/sage palette, white message cards and deep teal controls.
- [x] Full-screen assistant with saved chats on the left and floating bottom navigation.
- [x] Reusable CSS 3D permit illustration and three-slide looping product introduction.
- [x] Pause/play and direct slide selection; reduced motion and hidden-tab autoplay suspension.
- [x] Consistent 250px desktop rails and content alignment across both workspaces; responsive mobile layout.
- [x] Source network linked to real registered sources, clickable nodes and expandable evidence details.
- [x] Collapsible sync outcomes and document history; existing sync and approval actions retained.
- [x] App sparkle favicon and updated browser theme metadata.
- [x] Frontend build and lint pass. Browser checks use mocked APIs to avoid paid sync/model calls.
- [ ] Deploy frontend changes through the existing GitHub/Azure workflow and verify with live data.


### Palette comparison — 9 November 2026

- [x] Six application-wide palettes: Pearl & Iris, Ivory & Charcoal, Ice & Navy, Burgundy & Blush, Apricot & Clay, Stone & Teal.
- [x] Persistent top switcher updates both workspaces without resetting chat/profile state; validated local storage falls back to Pearl.
- [x] Shared semantic CSS tokens cover controls, messages, evidence maps, watermarks, illustrations and scrollbars.
- [x] Two-row mobile palette controls; desktop/mobile checks and targeted accessibility checks passed across all six palettes.


- [x] Final theme selected: **Pearl & Iris**. Removed the temporary comparison switcher, alternative palettes and browser preference code. Favicon and browser theme metadata now match the final theme.


### Compact guidance and evidence motion — 9 November 2026

- [x] Auto-growing message input without a default scrollbar, separate send icon and tighter message spacing.
- [x] Removed redundant composer/sidebar copy and shortened Knowledge headings and scope notes.
- [x] Five mutually exclusive source-status groups with counts, filtering and 12-at-a-time source disclosure, verified using 100 mocked sources.
- [x] Latest Sync shows a compact raised status badge and a disclosure chevron.
- [x] Curved layered network cables animate connection highlights; decorative sidebar watermarks drift gently.
- [x] Three concise welcome slides use distinct conversation, seven-emirate and evidence animations; existing document sculpture retained for evidence.
- [x] Knowledge empty state reuses the animated evidence sculpture.
- [x] Consistent capitalisation for card/status/dropdown labels without changing backend values.
- [x] Reduced-motion preferences disable decorative motion; frontend build and lint pass.


### Business interface audit and three design previews — 10 November 2026

- [x] Completed `better-interface` audit using all six owning domain guides; ranked report in `docs/design/INTERFACE_AUDIT.md`.
- [x] Three independent agents implemented Executive Desk, Editorial Concierge and Evidence Console.
- [x] Added local preview switcher and shareable `?design=` URLs; backend/API functionality remains shared.
- [x] Corrected draft persistence, citation navigation, composer focus, contrast, source-link targets and profile completion counts.
- [x] Added offline screenshot gallery at `docs/design/DESIGN_COMPARISON.html`.
- [x] Frontend build, lint and formatting pass; browser verification uses mocked API data and includes narrow-width and error states.
- [ ] Choose one design; then remove the two comparison-only variants for the final release.
- [ ] Restore local MongoDB network access and restart the API; saved-chat loading currently returns 503 while database readiness is false.
- [ ] Native screen-reader, actual browser zoom, iOS keyboard and live-provider end-to-end checks remain to be completed.


### Complete UI composition overhaul — 10 November 2026

- [x] Replace the previous skyline/summary-card layout in all three previews.
- [x] Build independent Assistant and Knowledge React views for Glass Workspace, Advisory Journal and Operations Console.
- [x] Share typed chat/knowledge view models rather than duplicate API and Redux behavior.
- [x] Preserve saved chats, unsent drafts, five-question profile selection, citations, manual sync, discovery choice and approval actions.
- [x] Preserve provenance dates, section changes, version browsing and full document comparison.
- [x] Check desktop and 320px layouts, source collections of 100 entries, keyboard selection, reduced motion, errors and active sync states with intercepted fixtures.
- [x] Correct contrast, mobile accessible-name and keyboard-scroll issues identified by browser checks.
- [x] Install all seven requested skill collections: 333 new packages, three existing packages preserved; pinned provenance recorded in docs/design/skills-provenance.json.
- [x] Refresh the offline design comparison and screenshots.
- [ ] Recheck the complete flow against the user's running backend and Atlas. The latest local health request could not reach port 8000; earlier diagnostics identified a MongoDB connection failure. No credentials or Atlas settings were changed.
- [ ] User chooses the preferred direction before removing the other preview implementations.

Verification uses mocked API responses only and does not establish live backend readiness. Screen-reader output, Safari/iOS input behavior and native browser zoom remain unverified.


### Purposeful motion and interaction review — 10 November 2026

- [x] Review navigation, welcome, saved conversations, profile selection, composer, checklist, source library, reader, sync log and failure states across all three designs.
- [x] Add a distinct source → human review → checklist SVG illustration per design, played once per surface per page session.
- [x] Add short pointer-only workspace, drawer, dropdown and source-selection transitions with shared easing tokens.
- [x] Keep keyboard navigation immediate; suppress inherited pointer decoration and cancel selected-document fades on keyboard input.
- [x] Add real-request activity feedback and clearer sync-start/profile-loading/saved-chat-loading labels.
- [x] Copy checklists with conditions, unresolved gaps and source/version links; handle clipboard denial.
- [x] Distinguish unavailable source collections from genuinely empty collections; provide read-only retry without a capture or model call.
- [x] Fix nested Escape behaviour and return focus when business-context/history panels close; focus the composer on New Chat.
- [x] Check finite illustrations, reduced motion, pointer/keyboard timing, source retry HTTP methods and clipboard success/failure with intercepted fixtures.
- [x] Check 21 core desktop/mobile states and 15 motion/interaction states with automated accessibility checks; no reported violations in the tested final states.
- [x] Refresh the comparison gallery images.
- [ ] Verify native screen-reader output, Safari/iOS behaviour, real-device frame performance and live backend integration.

No external animation library, recurring decorative loop, invented progress percentage or automatic paid operation was introduced. Request dots run only during a real pending request. Browser checks use intercepted fixture responses, with no OpenAI calls or database writes.


### Minimal new-chat welcome

- [x] Use one shared welcome component across the three designs: compact illustration, short heading, one sentence and one checklist action.
- [x] Remove the welcome's extra prompt cards, process list and repeated notes.
- [x] Verify the starting button is visible above the composer at 320×568 without initial scrolling; desktop/mobile automated accessibility checks pass.


### Chat spacing and atmosphere

- [x] Widen conversations in all three designs while keeping 28px desktop / 18px mobile side gutters.
- [x] Reduce user-message vertical padding to 6px desktop / 5px mobile; retain multiline wrapping.
- [x] Add six low-opacity edge accents with a persisted pause/resume toggle; pause during typing and when the document is hidden.
- [x] Use static backgrounds on mobile and under reduced motion; keep decoration non-interactive and hidden from assistive technology.
- [x] Verify desktop/mobile geometry, pause persistence, resume, typing pause and reduced motion with mocked API fixtures. Corrected and rechecked dark-theme completion-count contrast. Build, lint and formatting pass.


### Evidence validation and workspace cleanup — 11 November 2026

- [x] Constrain provider output to the IDs from the current retrieval; require non-empty cited checklists and item-free gap/follow-up answers. Keep server-side active-version validation.
- [x] Add safe validation-reason/count logging without model text, retrieved content or arbitrary generated IDs.
- [x] Verify the SDK strict-schema request/response boundary with mocked HTTP; backend suite: 89 tests passed.
- [x] Remove composer footers, country/sector header labels, the background toggle and redundant completed-profile copy.
- [x] Replace the brand/favicon with a business-permit briefcase mark.
- [x] Use Knowledge workspace as the heading; retain subtitles and reduce Glass top spacing to 12px desktop / 10px mobile, including removal of empty notice gaps.
- [x] Add Glass Failed filter using latest capture status; keep old published evidence available independently.
- [x] Display stored/captured source titles with readable URL-path fallback, using existing data without an LLM or additional request.
- [x] Make the decorative chat backdrop settle after three seconds; mobile/reduced-motion backgrounds remain static.
- [x] Verify all three designs with nine desktop/mobile fixture screens, Failed filtering, human-readable search, missing chrome and finite motion. Frontend build/lint/formatting passed.
- [ ] Live provider verification: automatic approval review rejected sending the stored conversation/evidence to OpenAI for a paid check without specific authorization. No such call was executed.

# Three business-interface directions

Mode: **Redesign · Overhaul**, preserving existing API routes, saved chats, five-question scope collection, manual sync, review/approval, source dates and DB-only checklist answers. The user explicitly requested three agents to implement three selectable working versions; these are comparison prototypes, not a forced final selection.

| Version | Design read | System | Dials: variance / motion / density / assets / fidelity |
| --- | --- | --- | --- |
| Executive Desk | Institutional information architecture for task-focused business users | White/slate, navy actions, DM Sans/Manrope, 8px rhythm, restrained 8–12px radii and thin structural rules | 3 / 1 / 7 / 2 / 6 |
| Editorial Concierge | Quiet advisory experience with warm editorial hierarchy | Parchment/white, charcoal and burgundy, Georgia headings/DM Sans body, generous grouped spacing and modest radii | 5 / 1 / 5 / 2 / 5 |
| Evidence Console | Operational workspace for frequent evidence review | Ink/navy shell, restrained cool accent, clear data rows, tabular numbers and compact readable hierarchy | 4 / 1 / 8 / 2 / 5 |

The existing `/favicon.svg` is the retained product mark. No invented authority badges, customer claims, completion rates or live-status indicators are permitted. All three use shared functional components and actual API data. Comparison selection is local; no publishing, deployment or database migration is part of this redesign.

Narrative: immediately show the assistant task and applicable business scope. Viewing distance: laptop and phone. Temperature: authoritative, welcoming or operational respectively. Capacity: preserve the complete primary flows at 320px; use progressive disclosure and internal chat scrolling instead of tiny text.

Motion policy: no looping decoration or moving count labels on operational screens. Use short, interruptible state feedback, honour reduced motion and avoid animating routine keyboard interactions.


## Previewing the three working versions

Run the existing frontend command `npm run dev` from `frontend`, then choose a version in the Design Preview bar. Direct links: `/?design=executive`, `/?design=concierge`, `/?design=console`. A validated browser preference retains the last choice; draft questions and confirmed business profiles are shared across versions. Screenshots and the offline `DESIGN_COMPARISON.html` use labelled sample data. The app itself continues to call the configured backend; it does not replace real sources with fake statistics.

### Shared corrections applied

- Conversation drafts now survive workspace/design changes using per-conversation Redux state.
- Citation links open the exact evidence accordion and focus its summary.
- Composer keyboard focus has a visible indicator in every design.
- Text/link sizes and contrast were corrected; native delete confirmation and reduced-motion handling are preserved.
- Profile selection is normalised to five editable fields, correcting the misleading 7/5 counter.
- A source review is cleared when changing business profile and is hidden if its profile does not match.
- Operational screens have no ambient decorative loops; header and disclosure feedback remain restrained.

## Current local backend issue

The running API reports `database_ready=false`, `openai_configured=true`, and a MongoDB connection failure. A separate read-only ping confirms `ServerSelectionTimeoutError`, categorised as a network timeout or Atlas network-access restriction. Check that the Atlas cluster is running and its Network Access list includes the current local IP. Restart the backend after correction because its failed-startup service state remains unavailable until restart. Dotenv also reports malformed lines in the local configuration; keep entries as KEY=value or # comments. No secret values were printed, no database records were changed, and no paid model probes were made.


## Full composition overhaul — 10 November 2026

The first comparison retained too much of the previous information hierarchy. The current redesign replaces each screen composition rather than restyling that structure. Evidence Skyline, dashboard summary cards and the fixed five-filter sidebar are not carried into these designs.

| Direction | Assistant composition | Knowledge composition | Visual system |
| --- | --- | --- | --- |
| Glass Workspace | Focused conversation with restrained contextual navigation | Document library beside a dedicated reader; business scope opens on demand | Frosted navigation, opaque reading surfaces, crisp institutional type |
| Advisory Journal | An advisory conversation presented as a business casebook | Chronological review journal with contextual evidence inspection | Warm paper, editorial hierarchy, quiet separators |
| Operations Console | Compact working transcript with operational navigation | Searchable source queue and persistent inspector | Dense but readable controls, precise state labels, restrained dark chrome |

The three screens use shared conversation and knowledge view models. API calls, Redux drafts, profile binding, pagination, manual sync and approval behavior remain reusable. Each design owns its React presentation and scoped styles. Glass effects are limited to interface chrome; evidence text uses readable surfaces. Motion communicates state changes and respects reduced-motion preferences.

Design calibration: overhaul; business users on laptop and mobile; visual variance 8/10, motion 2/10, information density 6/10 (console 8), asset dependence 2/10, brand fidelity 7/10. The existing Permit Navigator mark is retained. The two workspaces and their real data remain the complete scope; no invented analytics are added.


### Verification and limits

The completed overhaul was exercised in headless Chrome with intercepted API fixtures, including 100 sources, long titles, long documents, pending review, failed requests and a running sync. Desktop 1440×1000 and mobile 320×568 were checked. Draft retention across workspace changes, citation disclosure, five-field keyboard selection, approval request payloads and explicit registered-source sync were exercised. Corrected automated findings were rechecked. Reduced-motion checks found no running animations.

The screenshots are illustrative fixture data, not production records. No model tokens, database writes or deployment were used for browser verification. VoiceOver, Safari/iOS, native browser zoom and a live OpenAI/Atlas end-to-end run are not verified. On the latest check the local health endpoint on port 8000 was unreachable; earlier diagnostics reported MongoDB unavailable. UI redesign does not repair Atlas networking.

Skills installation details are in SKILLS_INSTALLATION.md with pinned repository commits and skills-provenance.json. A new Codex session refreshes the skill catalog. Skills are selected by task; installing the complete collections does not mean applying every skill to every component.


## Motion and interaction refinement — 10 November 2026

The `animate` recipes and animation-performance guidance informed the implementation. One reusable SVG component provides three illustrations: layered documents and verification for Glass Workspace, an editorial source/review path for Advisory Journal, and a technical pipeline for Operations Console. These explain a real workflow; they are not simulated analytics. Each plays once per design surface per page session and settles in under one second.

| Section | Refinement | Purpose and boundary |
| --- | --- | --- |
| Welcome / empty reader | Design-specific evidence journey | Brief explanation; finite playback, no ambient loop |
| Workspace navigation | 180ms opacity/4px entry | Pointer-only continuity; keyboard changes are instant |
| Context / history / dropdowns | 160–200ms anchored entrances | Show spatial relationship; no animation of field width or list data |
| Source reader | Cancellable 160ms opacity bridge | Pointer selection feedback; cancelled by keyboard input |
| Buttons / profile choices | 160ms press, 100ms release; small selected-check feedback | Immediate confirmation without moving reading content |
| Pending requests | Indeterminate activity dots and explicit text | Actual loading only; no invented percentage or completion estimate |
| Checklist | Copy with conditions, gaps and source/version links | Useful export to clipboard, with an accessible failure message |
| Source errors | Read-only Retry Sources | Recover saved DB content without triggering web capture, search or generation |
| Keyboard / focus | Nested Escape and restored trigger focus; New Chat focuses input | Consistent control of disclosures and conversation state |

Reduced-motion users receive static illustrations and text-based status. Hover motion is gated to fine pointers. Transitions use named properties and the shared strong ease-out/drawer curves. No per-frame React state updates, inherited animated CSS variables, animated blur or new runtime dependency was added. Native disclosure animation is progressive enhancement; unsupported browsers retain instant, usable disclosures.

Rejected candidates: continuously orbiting backgrounds, cursor-following decoration, bouncing source counts, staggered entrances for 100 records, animation of document/checklist text while reading, and animated keyboard navigation. These add distraction or repeated delay to the business tasks.

Verification: Chrome fixture checks covered 1440×1000 and 320×568 layouts, clipboard success/denial, finite illustrations, reduced motion, pointer/keyboard duration differences, read-only retry requests, nested Escape, restored panel focus and New Chat focus. The 21 core states and 15 added interaction states returned no automated accessibility violations. No JavaScript page errors were observed in the successful runs. The gallery screenshots are fixtures, not production data. Real-device GPU/frame behaviour, native screen readers, Safari/iOS and live API/Atlas behaviour remain unverified.


### Chat spacing and background follow-up

Per user feedback, conversation content uses more of the available width, with balanced 28px desktop and 18px mobile gutters. User bubbles use 6px/5px vertical padding. Journal's former 990px column cap and large quotation treatment were removed.

A bounded six-element CSS atmosphere adds low-opacity accents near the chat edges. A visible desktop pause/resume control persists the user's choice. Motion pauses while typing/form controls are focused and when the document is hidden; mobile and reduced-motion presentations are static. It uses transform-only drift, no per-frame React updates or external renderer. This supersedes the earlier rejection of all ambient decoration for the explicitly requested chat background only.

Chrome fixture checks confirmed all three layouts at 1440×1000 and 320×568, persisted pause/resume, typing pause, mobile/reduced-motion static states, compact bubble padding and horizontal fit. Tested final states reported no automated accessibility violations. Physical-device frame performance and native assistive-technology output remain unverified.

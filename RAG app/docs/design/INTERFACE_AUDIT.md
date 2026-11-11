# Permit Navigator interface audit

Reviewed 10 November 2026 with `better-interface`, plus its six upstream domain guides. This is an audit of the existing product, not a branch/diff review. Source references below describe the pre-redesign baseline.

## Scope and coverage

Assistant: introduction, saved chats, five-question profile collection, checklist, citations, draft navigation, loading and provider error. Knowledge: unselected profile, populated 100-source collection, filters, source expansion, version review, partial sync and database error. Viewports: 1440×1000, 320×568 and 720×450 (a 200%-zoom-equivalent layout, not a native browser zoom test).

Stack: React 19, TypeScript, Vite, Redux Toolkit/RTK Query, Lucide and hand-written CSS. Existing conventions found: `TECHNICAL_DECISIONS.md`, `DEVELOPMENT_CHECKLIST.md` and `README.md`; no repository AGENTS.md, CLAUDE.md, CONTRIBUTING.md, CODING_STANDARDS.md or Storybook design-system documents were found. Pearl & Iris, left chat history, five profile questions, explicit manual sync, view-only Evidence Skyline and source-card filters are deliberate product choices, not defects.

| Domain | Evidence inspected | Result |
| --- | --- | --- |
| Accessibility | ChatPanel, SelectField keyboard walk, ProfileQuestions, native details, source review, reduced-motion and full WCAG-tag axe checks | Focus and target-size findings; reduced motion passes |
| Layout | App/ChatPanel lifecycle, AnswerCard anchors; rendered desktop/320px/review/100-source states | Draft loss and citation-navigation findings; tested 320px reflow passes |
| Writing | Onboarding, scope note, source status labels, partial-sync, loading and recovery messages | Onboarding scope finding |
| Typography | Computed source dates 9px, chart labels 9px, scope notes 10px, controls 12px; CSS text scale | Shared metadata/type-system finding |
| Colors | Rendered questionnaire user labels; axe contrast data across all tested states | One confirmed failing rendered text pair |
| UI polish | App view remount/keyframes, watermark and count animations, card/header/control treatments | Continuous motion without a normal-mode pause; frequent view-switch entrance |

## Findings

| Severity | Domain | Location | Before | After | Why |
| --- | --- | --- | --- | --- | --- |
| HIGH | Accessibility | `frontend/src/features/checklist-chat/components/ChatPanel.tsx:31`; `frontend/src/app/App.tsx:24` | Draft lives in local `useState`; switching Knowledge → Assistant returns an empty textarea. | Retain drafts in existing client state across workspace/preview changes. | Checking evidence silently destroys an unsent business question. Verified by typing a draft, changing views and returning. |
| HIGH | Accessibility | `frontend/src/styles/global.css:941`; `frontend/src/styles/theme.css:130` | Focused textarea has `outline: none 0px`; composer border and shadow are identical before/after focus. | Restore a visible high-contrast focus indicator on the composer. | WCAG 2.4.7: keyboard users cannot locate focus in the primary input. Measured actual computed styles. |
| HIGH | Colors | `frontend/src/styles/theme.css:2`; `frontend/src/styles/theme.css:105` | User-message label renders `#62677c` on `#e5e3fa`, 9px: **4.45:1**. | Darken the secondary text role or use the existing primary-text role, then remeasure. | WCAG 1.4.3 requires 4.5:1 for this text. Confirmed in desktop and 320px questionnaire states. |
| MEDIUM | Layout | `frontend/src/features/checklist-chat/components/AnswerCard.tsx:35` | `href="#evidence-…"` updates the hash but the target `<details>` stays closed. | Open the exact citation and focus/scroll within the chat scroller. | The evidence link does not actually reveal the evidence, adding a second search/disclosure step. |
| MEDIUM | Accessibility | `frontend/src/common/components/SourceLink.tsx:9`; `frontend/src/styles/global.css:1282` | Review-source link target is 200.2×20px with a nearest target offset of 20px. | Give the shared link a 24px minimum target/clearance. | Automated WCAG 2.5.8 finding repeated in desktop, 320px and zoom-equivalent review. |
| MEDIUM | Accessibility | `frontend/src/styles/global.css:3560`; `frontend/src/styles/theme.css` (`skyline-float`) | Watermark and numerical count bubbles run indefinitely outside the welcome pause control. | Delete the ambient loops on operational screens; reserve motion for state feedback. | WCAG 2.2.2: movement continues alongside work without a visible pause mechanism. Reduced-motion is implemented correctly and remains preserved. |
| MEDIUM | Typography | `frontend/src/styles/theme.css` (`source-date`, `skyline-label`, `source-stat span`) | Important source dates and statuses render at 9–10px with a scattered fixed-pixel scale. | Use a small shared rem scale; 12px metadata, 14–16px controls/body and tabular numeric metrics. | Weakens scanning and does not adapt with reader font preferences. Exact size is a density choice; the recommendation addresses consistently important metadata. |
| MEDIUM | Writing | `frontend/src/common/components/AssistantWelcome.tsx:5`; `frontend/src/features/business-profile/components/ProfileSelectors.tsx:69` | Broad “business assistant” welcome; the actual mainland IT/software pilot scope appears only in secondary profile copy. | Put “Mainland IT/software · Seven emirates” beside the entry point, without claiming broader licensing coverage. | Users with unrelated business types can start an unsupported path before learning its limits. |
| MEDIUM | Writing | `frontend/src/features/business-profile/components/ProfileSelectors.tsx:25`; `frontend/src/features/business-profile/store/profileSlice.ts:21` | A selected server profile also stores `id` and `coverage_note`; `Object.values(selection)` displays **7/5** answered. | Count only the five configured fields and normalise stored selection fields. | Misrepresents completion in every design after chat binds a profile. Confirmed in rendered Knowledge screens during integration. |
| LOW | UI | `frontend/src/app/App.tsx:24`; `frontend/src/styles/global.css:3372` | Every tab remount starts `workspace-switch .35s`, plus decorative disclosure/entry animations. | Remove routine view entrance animation; keep instant selected-state feedback. | High-frequency navigation repeatedly delays content; the same task is better served by direct response. |

## Verification

Read-only Chrome harness: `node /private/tmp/permit-interface-audit/audit.mjs`; focus probe: `node /private/tmp/permit-interface-audit/focus.mjs`.

- Inspected 13 rendered states with WCAG 2 A/AA, 2.1 AA and 2.2 AA axe tags. No paid model calls or live database writes; API data was mocked.
- Confirmed keyboard dropdown open, arrow navigation, Enter selection and Escape support by source and browser interaction.
- Confirmed native chat-delete confirmation by source inspection. A destructive operation was not executed against live data.
- Confirmed five-profile selections gate checklist generation and source review controls are available.
- Confirmed source results scroll internally; 320px Knowledge and checklist screens have no horizontal overflow in the tested fixtures.
- Confirmed reduced-motion leaves no running animations in the probed Knowledge screen.
- Confirmed draft loss, closed citation targets, composer focus and contrast with browser measurements rather than taste-based inference.
- Evidence retained in `/private/tmp/permit-interface-audit/` (screenshots, axe JSON and interaction JSON).

**Not verified:** native VoiceOver/NVDA operation; native 200% browser zoom and iOS virtual-keyboard behavior; RTL/localisation; external font loading under unrestricted network; live OpenAI/Atlas responses and authoritative licensing completeness. The 720×450 check is only a zoom-equivalent layout check. Mocked workflow success is not proof of backend integration.

## Verdict

**Block** — the draft-loss, invisible-focus and contrast failures require correction. This verdict covers the six inspected domains and the stated runtime boundary; it does not claim live-provider or screen-reader certification.

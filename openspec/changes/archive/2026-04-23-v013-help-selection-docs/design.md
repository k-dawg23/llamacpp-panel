## Context

The panel is a Vite + React SPA served by the FastAPI app. Help must work without a network round-trip after load. Selection styling must match the existing dark, compact control aesthetic.

## Goals / Non-Goals

**Goals:**

- Consistent **selected** vs **unselected** styles for tab navigation and preset (or similar) button groups across Settings, Models, Logs/Monitor, and any other top-level views.
- **Short hints** on hover/focus for inputs, tab triggers, and action buttons; text concise (roughly one or two sentences) with pointers to the Help tab for depth.
- A **single source of truth** Markdown user guide checked into the repo; the Help tab renders that content (or a build-time copy) so GitHub and the app stay in sync.
- Version **0.1.3** surfaced in the UI and tagged **`v0.1.3`**.

**Non-goals:**

- Full i18n / translated strings in this release.
- Context-sensitive help that jumps to arbitrary anchors inside third-party `llama-server` docs (linking to upstream README is fine in the guide).
- Replacing `README.md` entirely; README stays the install/quick-start entry, with a clear link to the user guide.

## Decisions

1. **User guide path:** Add `docs/panel-user-guide.md` at the repository root (easy to browse on GitHub). The Vite app imports it as raw text at build time (for example `?raw`) or copies it into `web/public/` via a small build step—prefer **`import guide from '../../../docs/panel-user-guide.md?raw'`** from `web/src` if path and tooling allow, otherwise place `web/src/docs/panel-user-guide.md` and add a CI or comment that it must stay in sync with `docs/`. *Implementer picks one approach and documents it in tasks.*
2. **Markdown rendering:** Use a lightweight renderer already common in Vite stacks (for example `react-markdown` + `remark-gfm` for tables) or minimal custom rendering if bundle size is a concern—decision at implement time with a default toward **`react-markdown`** for maintainability.
3. **Tooltips:** Native `title` satisfies the spec minimum; if a richer tooltip is used, ensure keyboard focus can surface the same text (for example `aria-describedby` or a focusable wrapper).
4. **Selected buttons:** Define shared styles (e.g. higher contrast border, background tint, `font-weight`, `aria-selected` / `aria-pressed` on tab-like controls) in one place and apply to tab list and preset clusters.

## Risks / Trade-offs

- **Drift:** Two copies of the guide if sync is manual—mitigate with one import path or a lint script.
- **Bundle size:** Markdown + renderer adds weight—acceptable for an operator tool; tree-shake and lazy-load the Help tab chunk if easy.

## Migration Plan

- No config migration. After implementation, tag **`v0.1.3`** and push.

## Open Questions

- Exact file path for the guide if `?raw` import from repo root is awkward in this repo’s Vite config (resolve at implement time).

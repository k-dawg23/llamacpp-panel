## Why

Power users can infer behavior from labels, but many operators need to know what each control does, which values are valid, and how tabs relate to the supervised `llama-server`. Today, selected actions (tabs, presets, and similar controls) do not always read as “active,” and there is no first-class in-app reference. Release **v0.1.3** (git tag **`v0.1.3`**) improves discoverability and confidence without changing core supervisor semantics.

## What Changes

- Bump shipped version to **0.1.3** and document tagging **`v0.1.3`** for the release.
- **Obvious selection:** Primary navigation and other binary/choice controls (for example tab switches, configuration presets, and comparable button groups) SHALL use a consistent visual and programmatic “selected” state so users can tell what is active at a glance on every tab.
- **Contextual help:** Every major field, tab label, and primary button SHALL expose a short explanation suitable for hover or focus (for example `title` / tooltip pattern) covering purpose and typical valid ranges or formats where applicable.
- **User guide artifact:** Add a maintained Markdown document in the repository that expands on the same topics (tabs, fields, buttons, environment notes, limitations). It SHALL stay aligned with the UI as features evolve.
- **Help tab:** The web UI SHALL include a **Help** tab that renders the user guide (or an equivalent bundled copy) as readable formatted content, suitable for offline use after build.

## Capabilities

### Modified Capabilities

- `control-panel-ui`: Selection affordances for tabs and comparable controls; pervasive short help hints; new Help tab backed by the user guide Markdown.

## Impact

- **Frontend:** Tab styling; tooltip/hint wiring; optional dependency for Markdown rendering if not already present; new static/doc asset in the web bundle.
- **Docs:** New or updated `docs/` (or `web/`-adjacent) Markdown; README pointer to the guide; release checklist including **`git tag v0.1.3`**.
- **Compatibility:** Non-breaking; no API or config schema changes required for the core behavior (unless implementation chooses to serve the guide via API—prefer static bundle for simplicity).

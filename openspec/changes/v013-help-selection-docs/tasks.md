## 1. Release metadata

- [ ] 1.1 Bump `pyproject.toml` and `llamacpp_panel/__init__.py` version to **0.1.3**
- [ ] 1.2 Surface version **0.1.3** in the web UI (footer or about line)
- [ ] 1.3 After merge, create and push git tag **`v0.1.3`** (and optional GitHub release notes)

## 2. User guide Markdown

- [ ] 2.1 Add `docs/panel-user-guide.md` covering every tab, major field, and primary button: purpose, valid values/ranges, and links to upstream llama.cpp docs where useful
- [ ] 2.2 Link the guide from `README.md` (one short section or bullet)
- [ ] 2.3 Wire the guide into the web build (single source: import raw, public copy, or documented sync—per `design.md`)

## 3. Help tab

- [ ] 3.1 Add a **Help** top-level tab that renders the guide as formatted content (Markdown → HTML/React)
- [ ] 3.2 Ensure the Help view is readable (typography, code blocks, headings) and scrollable on laptop-sized viewports

## 4. Contextual hints

- [ ] 4.1 Add short hover/focus hints for all primary fields on Settings (including GPU, paths, ports, presets, extra args)
- [ ] 4.2 Add hints for Models tab controls (browse, download, Use, paths)
- [ ] 4.3 Add hints for Server/Logs (or equivalent) actions and any remaining tab actions
- [ ] 4.4 Tab labels themselves include hints where extra clarification helps (e.g. what “Models” vs “Settings” owns)

## 5. Selected control states

- [ ] 5.1 Unify top-level tab styling so the active tab is visually distinct on all tabs (contrast, border, or background per existing design language)
- [ ] 5.2 Apply the same pattern to preset (or similar) button groups and any toggle-style actions that represent a persistent choice within a tab
- [ ] 5.3 Use appropriate ARIA (`aria-selected`, `role="tablist"` / `tab` where applicable, or `aria-pressed` for toggle buttons)

## 6. Verification

- [ ] 6.1 Manual pass: every tab shows clear active state; hints appear on hover/focus; Help tab matches guide content
- [ ] 6.2 `npm run build` succeeds; optional smoke test for bundle including the guide

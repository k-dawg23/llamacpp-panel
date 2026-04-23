## ADDED Requirements

### Requirement: Visible selection for navigation and choice controls

The UI SHALL make the active top-level tab (and comparable persistent choice controls such as configuration presets within a tab) visually obvious using a consistent selected style across all tabs. Assistive technology SHALL reflect the active choice where applicable (for example `aria-selected` on tabs, or `aria-pressed` on toggle-style buttons).

#### Scenario: Switch tabs

- **WHEN** the user moves from one top-level tab to another
- **THEN** the newly active tab SHALL be immediately distinguishable from inactive tabs without relying on color alone

#### Scenario: Preset or mode cluster

- **WHEN** the user selects a preset or similar exclusive option represented as a button group
- **THEN** the selected option SHALL remain visually distinct until another option is chosen

### Requirement: Contextual field and control help

Every primary input field, top-level tab trigger, and primary action button SHALL expose a concise explanation of its purpose and, where relevant, valid value ranges or formats. The explanation SHALL be available on pointer hover and on keyboard focus (for example via a native tooltip, a custom accessible tooltip, or an associated description).

#### Scenario: Focus without mouse

- **WHEN** the user focuses a control using the keyboard
- **THEN** the same explanatory text available on hover SHALL be obtainable without requiring a pointing device

### Requirement: In-app user guide

The UI SHALL provide a **Help** tab that presents the project’s user-guide Markdown (or an equivalent bundled copy) as formatted, readable content, including headings and code samples as appropriate. The guide SHALL describe tabs, major fields, buttons, and common operational notes.

#### Scenario: Open Help

- **WHEN** the user opens the Help tab
- **THEN** the full guide content SHALL be visible without leaving the application and SHALL be scrollable within the panel layout

### Requirement: Maintained user guide document

The repository SHALL include a Markdown user guide file (for example under `docs/`) that expands on the same material as the in-app hints. The in-app Help tab SHALL stay aligned with that document’s intent; implementation MAY use a single build-time source to avoid divergence.

#### Scenario: Browse on GitHub

- **WHEN** a contributor opens the Markdown file in the repository
- **THEN** they SHALL find section coverage comparable to the Help tab (tabs, fields, actions)

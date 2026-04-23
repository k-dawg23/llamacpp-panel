### Requirement: Localhost-first access

The control panel web application SHALL be served on loopback by default and SHALL document how to change the bind address for advanced users. The UI SHALL not require cloud accounts to function.

#### Scenario: Default bind

- **WHEN** the user starts the supervisor with default settings
- **THEN** the web UI SHALL be reachable only from the local machine unless explicitly reconfigured

### Requirement: Server lifecycle controls

The UI SHALL provide clearly labeled actions to start and stop the supervised `llama-server`, with disabled states and inline validation errors when configuration is incomplete (for example missing binary path or model).

#### Scenario: Block start when invalid

- **WHEN** required fields are missing
- **THEN** the start action SHALL be disabled or SHALL show validation messages explaining what is missing

### Requirement: Settings and presets

The UI SHALL expose common `llama-server` options with plain-language labels (for example context length, GPU layers when applicable, host, port, API key) and SHALL support at least one “preset” style quick configuration (balanced vs maximum context) mapped to concrete flag values. The UI SHALL display detected accelerator devices when the supervisor reports them (vendor, model name, and stable identifier) and SHALL provide a dedicated control to choose which device to use when more than one device is reported, persisting the choice in the launch profile.

#### Scenario: Apply preset

- **WHEN** the user selects a preset
- **THEN** the form fields SHALL update to the preset’s values and SHALL be editable afterward

#### Scenario: Multiple GPUs

- **WHEN** the supervisor reports more than one selectable device
- **THEN** the Settings view SHALL show a clear device picker and SHALL indicate which device is currently selected for the next launch

#### Scenario: Zero or one device

- **WHEN** the supervisor reports no devices or exactly one device
- **THEN** the Settings view SHALL summarize hardware honestly (including “none detected”) and SHALL not present a misleading multi-device picker

### Requirement: Logs and status panels

The UI SHALL show a scrollable log view for supervised process output and a status panel combining health and key props or slots. The layout SHALL remain usable on a typical laptop display resolution.

#### Scenario: Live log tail

- **WHEN** the server is running and emitting logs
- **THEN** the log panel SHALL update continuously without requiring a full page reload

### Requirement: Model library integration

The UI SHALL let users browse local GGUF files from configured roots, trigger Hugging Face downloads, and pick the active model for the next launch. After any action that sets the active local model (including **Use** on a table row), the Models tab SHALL immediately show a persistent summary of the current active model (path or HF identifier per mode) and SHALL make the active choice visually obvious (for example row highlight, badge, or dedicated “Current model” region) without requiring the user to open the Settings tab.

#### Scenario: Download then select

- **WHEN** a Hugging Face download completes
- **THEN** the UI SHALL offer to set the new file as the active model or HF identifier according to the chosen launch mode

#### Scenario: Use action confirms selection

- **WHEN** the user clicks **Use** on a local GGUF row
- **THEN** the UI SHALL update the visible current-model summary on the Models tab in the same session and SHALL distinguish the selected row from other rows until the selection changes

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

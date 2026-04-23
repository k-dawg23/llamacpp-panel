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

The UI SHALL expose common `llama-server` options with plain-language labels (for example context length, GPU layers when applicable, host, port, API key) and SHALL support at least one “preset” style quick configuration (balanced vs maximum context) mapped to concrete flag values.

#### Scenario: Apply preset

- **WHEN** the user selects a preset
- **THEN** the form fields SHALL update to the preset’s values and SHALL be editable afterward

### Requirement: Logs and status panels

The UI SHALL show a scrollable log view for supervised process output and a status panel combining health and key props or slots. The layout SHALL remain usable on a typical laptop display resolution.

#### Scenario: Live log tail

- **WHEN** the server is running and emitting logs
- **THEN** the log panel SHALL update continuously without requiring a full page reload

### Requirement: Model library integration

The UI SHALL let users browse local GGUF files from configured roots, trigger Hugging Face downloads, and pick the active model for the next launch.

#### Scenario: Download then select

- **WHEN** a Hugging Face download completes
- **THEN** the UI SHALL offer to set the new file as the active model or HF identifier according to the chosen launch mode

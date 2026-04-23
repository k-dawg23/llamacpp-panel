## MODIFIED Requirements

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

### Requirement: Model library integration

The UI SHALL let users browse local GGUF files from configured roots, trigger Hugging Face downloads, and pick the active model for the next launch. After any action that sets the active local model (including **Use** on a table row), the Models tab SHALL immediately show a persistent summary of the current active model (path or HF identifier per mode) and SHALL make the active choice visually obvious (for example row highlight, badge, or dedicated “Current model” region) without requiring the user to open the Settings tab.

#### Scenario: Download then select

- **WHEN** a Hugging Face download completes
- **THEN** the UI SHALL offer to set the new file as the active model or HF identifier according to the chosen launch mode

#### Scenario: Use action confirms selection

- **WHEN** the user clicks **Use** on a local GGUF row
- **THEN** the UI SHALL update the visible current-model summary on the Models tab in the same session and SHALL distinguish the selected row from other rows until the selection changes

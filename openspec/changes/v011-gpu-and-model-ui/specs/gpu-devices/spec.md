## ADDED Requirements

### Requirement: GPU discovery API

The system SHALL expose an HTTP API that returns a list of detected accelerator devices suitable for user-facing selection. Each device entry SHALL include a stable identifier, a human-readable name, and vendor classification when known.

#### Scenario: NVIDIA GPUs present

- **WHEN** `nvidia-smi` is available on the host and reports one or more GPUs
- **THEN** the API SHALL return at least one device per GPU with distinct identifiers and SHALL indicate the discovery source in the response metadata

#### Scenario: No enumerator available

- **WHEN** no supported discovery command succeeds
- **THEN** the API SHALL return an empty device list and SHALL NOT fail with a server error; the response SHALL include a brief reason for operators

### Requirement: Persisted device selection

The launch profile SHALL store an optional GPU device identifier chosen by the user. The identifier SHALL be persisted with the rest of the launch profile and SHALL round-trip through the existing configuration save and load paths.

#### Scenario: User selects second GPU

- **WHEN** the user selects a specific device from a multi-device list and saves settings
- **THEN** subsequent configuration reads SHALL return the same identifier until the user changes it

### Requirement: Documented application to llama-server

The project documentation SHALL state how a saved device identifier is applied when starting `llama-server` (for example which environment variables are set for CUDA), and the implementation SHALL follow that documented mapping for supported backends.

#### Scenario: CUDA mapping

- **WHEN** the active backend uses CUDA and a device identifier is saved
- **THEN** the documented environment mapping SHALL be applied to the supervised child process for that identifier format

## ADDED Requirements

### Requirement: GPU device selection applied at launch

When the launch profile contains a non-empty GPU device identifier and the implementation supports the active backend, the supervised `llama-server` child process SHALL inherit environment variables (or additional arguments, if documented) so that inference targets the selected device. When the identifier is empty or unsupported, the system SHALL behave as in prior releases without failing validation solely due to GPU fields.

#### Scenario: CUDA device constrained

- **WHEN** a CUDA-style device identifier is saved and the user starts the server
- **THEN** the child environment SHALL include the documented CUDA visibility constraint for that identifier

#### Scenario: No GPU selection saved

- **WHEN** the GPU device identifier is unset or blank
- **THEN** the supervisor SHALL not inject GPU-restricting environment variables beyond existing bundle `LD_LIBRARY_PATH` behavior

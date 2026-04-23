## ADDED Requirements

### Requirement: Configurable llama.cpp binary directory

The system SHALL allow the user to configure an absolute path to a directory that contains the `llama-server` executable (or an explicit path to the executable). The system SHALL persist this setting across restarts.

#### Scenario: Validate binary on save

- **WHEN** the user saves a new binary directory
- **THEN** the system SHALL verify that `llama-server` exists at the resolved path and is executable, and SHALL surface a clear error if validation fails

#### Scenario: Default first-run path

- **WHEN** no binary path has been configured yet
- **THEN** the system SHALL prompt the user to select a directory before starting the server

### Requirement: Bundled shared library discovery

When the configured directory contains shared objects required by `llama-server` (for example `libllama.so` siblings in the same folder), the system SHALL set `LD_LIBRARY_PATH` for the supervised child process so that directory is searched first, without modifying the user’s global shell environment.

#### Scenario: Launch with bundle layout

- **WHEN** the user starts the server from a Vulkan or portable bundle directory that includes `llama-server` and required `.so` files
- **THEN** the supervised process SHALL inherit an `LD_LIBRARY_PATH` that includes that directory and SHALL start successfully when the upstream binary is otherwise compatible with the host

### Requirement: Start and stop supervised server

The system SHALL start `llama-server` as a child process using arguments derived from the active launch profile (model source, flags, host, port, and optional extra CLI tokens). The system SHALL support graceful stop (SIGTERM) and SHALL detect unexpected exit and record the last exit code.

#### Scenario: Start succeeds

- **WHEN** the user requests start with valid configuration and resources
- **THEN** the system SHALL spawn `llama-server`, mark the supervised state as running, and begin capturing stdout and stderr

#### Scenario: Stop while running

- **WHEN** the user requests stop while the server is running
- **THEN** the system SHALL terminate the child process and mark the supervised state as stopped

### Requirement: Log capture and retention

The system SHALL capture a bounded rolling buffer of the supervised process stdout and stderr for display in the control UI. The buffer size SHALL be configurable with a safe default.

#### Scenario: Stream logs to UI

- **WHEN** the supervised server emits log lines
- **THEN** the system SHALL append those lines to the in-memory buffer and make them available to the UI in near real time

### Requirement: Persisted launch profiles

The system SHALL persist at least one named launch profile containing the argument template used to start `llama-server`, including host, port, model selection mode (local path or Hugging Face identifier), and common options (for example context size and GPU layer count when exposed by the UI).

#### Scenario: Restore last profile

- **WHEN** the supervisor restarts
- **THEN** the system SHALL reload the last active profile and binary configuration from persistent storage

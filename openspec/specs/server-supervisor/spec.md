### Requirement: Configurable llama.cpp binary directory

The system SHALL allow the user to configure an absolute path to a directory that contains the `llama-server` executable (or an explicit path to the executable). The system SHALL persist this setting across restarts. On Microsoft Windows, the system SHALL resolve the primary server executable using Windows naming conventions (at minimum `llama-server.exe` in the configured directory). On POSIX hosts, the system SHALL continue to resolve `llama-server` in that directory. Validation SHALL verify that the resolved executable exists and is runnable on the host without relying on POSIX execute bits when running on Windows.

#### Scenario: Validate binary on save

- **WHEN** the user validates or saves a new binary directory
- **THEN** the system SHALL verify that the resolved `llama-server` executable exists for the current platform and SHALL surface a clear error if validation fails

#### Scenario: Default first-run path

- **WHEN** no binary path has been configured yet
- **THEN** the system SHALL prompt the user to select a directory before starting the server

#### Scenario: Windows executable present

- **WHEN** the host runs Windows and the bundle directory contains `llama-server.exe`
- **THEN** validation and start SHALL resolve that executable without requiring a file named exactly `llama-server` with no extension

### Requirement: Bundled shared library discovery

When the configured directory contains native libraries required by `llama-server` (for example `libllama.so` siblings on POSIX or `.dll` siblings on Windows), the system SHALL apply host-appropriate dynamic library search rules for the supervised child process only, without modifying the user’s global environment. On POSIX, the system SHALL prepend the bundle directory to `LD_LIBRARY_PATH` (with the platform’s path separator convention). On Windows, the system SHALL prepend the bundle directory to the child process `PATH` (with `;` as the separator) and SHALL document that many layouts rely on DLLs colocated with `llama-server.exe`.

#### Scenario: Launch with bundle layout on POSIX

- **WHEN** the user starts the server from a portable bundle directory that includes `llama-server` and required native libraries for Linux
- **THEN** the supervised process SHALL inherit an `LD_LIBRARY_PATH` that includes that directory first and SHALL start successfully when the upstream binary is otherwise compatible with the host

#### Scenario: Launch with bundle layout on Windows

- **WHEN** the user starts the server from a portable bundle directory on Windows that includes `llama-server.exe` and required `.dll` files
- **THEN** the supervised process SHALL inherit a `PATH` whose first segment is the bundle directory (in addition to any system PATH) and SHALL start successfully when the upstream binary is otherwise compatible with the host

### Requirement: Start and stop supervised server

The system SHALL start `llama-server` as a child process using arguments derived from the active launch profile (model source, flags, host, port, and optional extra CLI tokens). On POSIX hosts, the system SHALL support graceful stop via `SIGTERM` (or equivalent) before forced termination. On Windows, the system SHALL support best-effort termination consistent with Python’s process API (which may not deliver POSIX-style graceful shutdown). The system SHALL detect unexpected exit and record the last exit code on all supported hosts.

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

### Requirement: GPU device selection applied at launch

When the launch profile contains a non-empty GPU device identifier and the implementation supports the active backend, the supervised `llama-server` child process SHALL inherit environment variables (or additional arguments, if documented) so that inference targets the selected device. When the identifier is empty or unsupported, the system SHALL behave as in prior releases without failing validation solely due to GPU fields.

#### Scenario: CUDA device constrained

- **WHEN** a CUDA-style device identifier is saved and the user starts the server
- **THEN** the child environment SHALL include the documented CUDA visibility constraint for that identifier

#### Scenario: No GPU selection saved

- **WHEN** the GPU device identifier is unset or blank
- **THEN** the supervisor SHALL not inject GPU-restricting environment variables beyond existing bundle library search behavior (`LD_LIBRARY_PATH` on POSIX; bundle `PATH` prepend on Windows as specified above)

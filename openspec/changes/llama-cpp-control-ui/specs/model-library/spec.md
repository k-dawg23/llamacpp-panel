## ADDED Requirements

### Requirement: Local GGUF discovery

The system SHALL scan user-configured directories for files ending in `.gguf` and SHALL expose each file’s path, size, and modified time to the UI for selection as the active model.

#### Scenario: User adds model root

- **WHEN** the user adds a directory to the model library roots
- **THEN** the system SHALL index `.gguf` files under that directory (respecting reasonable depth limits) and list them in the UI

#### Scenario: Select local model for launch

- **WHEN** the user selects a listed GGUF file
- **THEN** the system SHALL update the active launch profile to pass that path to `llama-server` using the appropriate upstream flag (for example `-m`)

### Requirement: Hugging Face GGUF download

The system SHALL support downloading GGUF weights from Hugging Face using a repository identifier and file selection, storing files in the standard Hugging Face cache layout so they are compatible with upstream `-hf` workflows and shared tooling.

#### Scenario: Download requested file

- **WHEN** the user requests download of a specific GGUF file from a Hugging Face repo
- **THEN** the system SHALL download the artifact with resumable behavior where supported and SHALL report progress and final path or cache location to the UI

#### Scenario: Network or auth failure

- **WHEN** download fails due to network error or missing credentials for a gated model
- **THEN** the system SHALL surface a clear error and SHALL leave no inconsistent partial state without user visibility

### Requirement: Disk visibility

The system SHALL display human-readable size information for local models and SHALL avoid blocking the UI thread during long scans or downloads.

#### Scenario: Large library scan

- **WHEN** the model root contains many large files
- **THEN** the system SHALL perform scanning asynchronously and SHALL show a loading state until results are ready

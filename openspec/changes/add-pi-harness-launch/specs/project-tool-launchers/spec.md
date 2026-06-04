## ADDED Requirements

### Requirement: Persist project folders for tool launch
The system SHALL allow the user to save one or more absolute local project folders for host-side tool launch workflows and SHALL persist both the saved folder list and the currently selected project folder across restarts.

#### Scenario: Save and restore project folders
- **WHEN** the user saves project folder paths and chooses one as the selected project folder
- **THEN** the system SHALL store that folder list and selected folder in persisted configuration and SHALL restore them on the next application start

#### Scenario: Reject invalid selected folder
- **WHEN** the selected project folder is empty, missing, or not a directory at launch time
- **THEN** the system SHALL reject the launch request with a clear validation error

### Requirement: Launch pi from selected project folder
The system SHALL provide a host-side launch action for `pi` that starts the `pi` command with the selected project folder as the process working directory and SHALL report immediate success or startup failure to the caller.

#### Scenario: Launch succeeds
- **WHEN** the user starts `pi` from a valid selected project folder and the `pi` command is available on the host
- **THEN** the system SHALL start a `pi` process using that folder as `cwd` and SHALL return a success response that identifies the folder used

#### Scenario: pi command unavailable
- **WHEN** the user starts `pi` from a valid selected project folder but the `pi` command cannot be resolved or executed
- **THEN** the system SHALL return a clear launch error explaining that `pi` could not be started

### Requirement: pi launch remains independent from llama supervisor
The system SHALL keep `pi` launch behavior separate from the supervised `llama-server` lifecycle so that launching or stopping one does not implicitly start, stop, or reconfigure the other.

#### Scenario: Start pi while llama-server is stopped
- **WHEN** the user launches `pi` while `llama-server` is not running
- **THEN** the system SHALL attempt the `pi` launch without requiring the llama supervisor to start first

#### Scenario: Stop llama-server after pi launch
- **WHEN** the user stops the supervised `llama-server` after `pi` was launched
- **THEN** the system SHALL stop only the supervised `llama-server` process and SHALL not treat `pi` as part of that stop action

## ADDED Requirements

### Requirement: Project folder selection for pi launch
The UI SHALL let the user enter and persist one or more project folder paths, indicate which folder is currently selected for tool launch, and show the selected folder near the `pi` launch action.

#### Scenario: Choose saved project folder
- **WHEN** the user selects a different saved project folder in the UI
- **THEN** the UI SHALL persist the new selection and SHALL update the visible selected-folder summary without requiring a page reload

#### Scenario: No project folder configured
- **WHEN** the user has not saved any project folder yet
- **THEN** the UI SHALL explain that a project folder must be configured before `pi` can be launched

### Requirement: pi launch action feedback
The UI SHALL provide a clearly labeled action to start `pi` from the selected project folder and SHALL present immediate success or error feedback from the backend without implying that `pi` is managed by the llama supervisor.

#### Scenario: Successful pi launch
- **WHEN** the user clicks the `Start pi harness` action and the backend accepts the launch
- **THEN** the UI SHALL show that `pi` launch was requested successfully and SHALL display the project folder used

#### Scenario: Launch error shown inline
- **WHEN** the backend rejects the `pi` launch request
- **THEN** the UI SHALL display the returned error in the same workflow area so the user can correct the project folder or host setup

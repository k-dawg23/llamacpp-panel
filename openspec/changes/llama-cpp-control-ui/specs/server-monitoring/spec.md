## ADDED Requirements

### Requirement: Health visibility

The system SHALL query the supervised `llama-server` HTTP `/health` (or equivalent documented health route for the configured server version) on the user-configured host and port and SHALL expose up/down status to the UI.

#### Scenario: Server responds healthy

- **WHEN** `llama-server` is running and `/health` returns success
- **THEN** the UI SHALL show a healthy status

#### Scenario: Server not listening

- **WHEN** no process is listening on the configured port or `/health` fails
- **THEN** the UI SHALL show an unhealthy or unreachable status without crashing the supervisor

### Requirement: Properties and slots

When the upstream server exposes `GET /props` and `GET /slots`, the system SHALL fetch and display summarized fields useful for operators (for example model id, context, and slot activity). If an endpoint is disabled in the running server, the system SHALL indicate that the endpoint is unavailable rather than failing fatally.

#### Scenario: Slots endpoint disabled

- **WHEN** `/slots` is not enabled on the running `llama-server`
- **THEN** the monitoring view SHALL show that slot metrics are unavailable for this instance

### Requirement: Optional metrics

When `llama-server` is started with metrics enabled and `GET /metrics` is available, the system SHALL offer a basic metrics view or raw text panel in the UI. When metrics are not enabled, the system SHALL omit or disable that panel.

#### Scenario: Metrics enabled

- **WHEN** `/metrics` returns Prometheus-compatible text
- **THEN** the UI SHALL display the metrics content or a parsed subset suitable for quick glance (for example request counters)

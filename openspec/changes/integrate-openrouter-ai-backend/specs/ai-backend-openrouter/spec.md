## ADDED Requirements

### Requirement: OpenRouter Backend Gateway
The system SHALL provide a backend gateway that calls OpenRouter's Chat Completions endpoint using server-side API keys and model identifiers. Client applications MUST NOT call OpenRouter directly.

#### Scenario: Secure configuration
- **WHEN** the service starts with AI enabled
- **THEN** the system MUST read `OPENROUTER_API_KEY` from environment and fail startup if the key is missing when `OPENROUTER_ENABLED=true`.

#### Scenario: Normalized response
- **WHEN** an authorized client invokes a backend AI workflow
- **THEN** the backend SHALL return a normalized JSON envelope containing `workflow`, `status`, `model`, `content`, and optional `structured_output`/`usage` fields

### Requirement: Provider Reliability and Safety
The system SHALL apply timeouts, bounded retries, and return controlled error payloads when OpenRouter is unavailable.

#### Scenario: Transient failure
- **WHEN** OpenRouter returns a transient 5xx or rate-limit error
- **THEN** the backend SHALL retry according to configuration and return a sanitized error if retries are exhausted

### Requirement: Access Control and Auditing
The system SHALL enforce role-based access to AI workflows and log AI usage with audit metadata.

#### Scenario: Unauthorized access
- **WHEN** a user without the required role calls a workflow
- **THEN** the backend SHALL respond with HTTP 403 and record the denied action in audit logs

### Requirement: No Frontend Provider Calls
The system SHALL NOT expose provider API keys or allow client-side calls to OpenRouter; the integration is backend-only.

#### Scenario: Frontend request
- **WHEN** frontend calls the AI assistant endpoint
- **THEN** the request is processed on the server and no provider secrets are sent to the client

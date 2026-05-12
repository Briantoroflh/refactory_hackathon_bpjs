## ADDED Requirements

### Requirement: Standard success response envelope
The backend MUST return successful API responses using a consistent JSON envelope with the keys `status`, `message`, and `data`.

#### Scenario: Successful endpoint response
- **WHEN** a client calls a successful API endpoint
- **THEN** the response body MUST contain `status`, `message`, and `data`
- **AND** `status` MUST indicate success
- **AND** `data` MUST contain the endpoint payload

### Requirement: Standard error response envelope
The backend MUST return error responses using the same JSON envelope keys `status`, `message`, and `data`.

#### Scenario: Validation or business error
- **WHEN** a request fails validation or a business rule rejects the request
- **THEN** the response body MUST contain `status`, `message`, and `data`
- **AND** `status` MUST indicate error
- **AND** `message` MUST describe the failure
- **AND** `data` MUST contain error details or be null when no structured details are available

### Requirement: Consistent response contract across API routes
The backend MUST apply the standard response envelope across the implemented API routes so clients can consume the same response structure regardless of endpoint.

#### Scenario: Different API modules return the same shape
- **WHEN** a client calls endpoints from auth, users, projects, tasks, workers, teams, audit, or KPI routes
- **THEN** each route MUST use the same `status`, `message`, and `data` response contract

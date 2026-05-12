## ADDED Requirements

### Requirement: Route handlers remain thin
The backend MUST keep route handlers focused on HTTP concerns only, including request parsing, dependency injection, and returning responses.

#### Scenario: Route delegates to controller
- **WHEN** a client calls an API endpoint
- **THEN** the route handler MUST delegate business logic to a controller function
- **AND** the route handler MUST not contain domain-specific business rules

### Requirement: Controller layer owns business logic
The backend MUST place endpoint business logic in controller modules instead of route modules.

#### Scenario: Business logic moved out of routes
- **WHEN** an endpoint needs to query data, validate domain rules, or orchestrate services
- **THEN** that logic MUST execute in a controller module
- **AND** the route layer MUST only bridge HTTP input and output to the controller

### Requirement: Existing API behavior is preserved
The backend MUST preserve existing endpoint paths, methods, status codes, and response contract while refactoring route logic into controllers.

#### Scenario: Refactor does not change external API behavior
- **WHEN** a client calls an existing endpoint after the refactor
- **THEN** the endpoint MUST still resolve at the same URL and method
- **AND** the response behavior MUST remain compatible for existing frontend consumers

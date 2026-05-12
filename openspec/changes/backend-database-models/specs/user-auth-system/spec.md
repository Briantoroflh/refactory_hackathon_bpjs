## ADDED Requirements

### Requirement: User registration with email validation
The system SHALL allow new users to register with email and password. Email addresses SHALL be unique and validated for correct format.

#### Scenario: Successful user registration
- **WHEN** user submits registration form with valid email and password (8+ chars)
- **THEN** system creates user account, hashes password with bcrypt, sends confirmation email

#### Scenario: Duplicate email rejection
- **WHEN** user attempts registration with email already in database
- **THEN** system returns 409 Conflict with message "Email already registered"

#### Scenario: Invalid email format
- **WHEN** user submits registration with malformed email
- **THEN** system returns 422 Unprocessable Entity with validation error

---

### Requirement: User login and JWT token generation
The system SHALL authenticate users with email/password and issue JWT tokens for subsequent requests. Tokens SHALL expire after 15 minutes; refresh tokens SHALL last 7 days.

#### Scenario: Successful login
- **WHEN** user submits valid email and correct password
- **THEN** system returns access_token (JWT), refresh_token, and token_type="Bearer"

#### Scenario: Invalid password
- **WHEN** user submits valid email but incorrect password
- **THEN** system returns 401 Unauthorized

#### Scenario: Non-existent user
- **WHEN** user submits email not in database
- **THEN** system returns 401 Unauthorized (no email enumeration)

#### Scenario: Token refresh
- **WHEN** user submits valid refresh_token
- **THEN** system returns new access_token with fresh expiration

---

### Requirement: Role-based access control (RBAC)
The system SHALL enforce permissions based on user roles. Users SHALL have at least one role (e.g., engineer, project_manager, team_lead, admin). Roles are combinations of permissions.

#### Scenario: User has project manager role
- **WHEN** project manager user attempts to create project
- **THEN** system grants permission and creates project

#### Scenario: Engineer without permission
- **WHEN** engineer user attempts to delete project
- **THEN** system returns 403 Forbidden

#### Scenario: Multi-role assignment
- **WHEN** user has both "team_lead" and "engineer" roles
- **THEN** user gets union of all permissions from both roles

---

### Requirement: Permission definition and role assignment
The system SHALL allow admin users to define granular permissions (read, create, update, delete per resource type) and assign them to roles. Changes SHALL be logged in audit trail.

#### Scenario: Admin assigns permission to role
- **WHEN** admin creates role with permissions [project:create, project:read]
- **THEN** system stores role and permission mappings; logs to audit trail with timestamp and admin user ID

#### Scenario: User assignment to role
- **WHEN** admin assigns user to role
- **THEN** user immediately gains all permissions from that role

---

### Requirement: Password hashing and security
Passwords SHALL be hashed using bcrypt with salt rounds ≥10. Plain-text passwords SHALL never be stored or logged. Passwords SHALL NOT be returned in API responses.

#### Scenario: Password hashing on registration
- **WHEN** user registers with password "MyPassword123"
- **THEN** system hashes password (e.g., $2b$10$...) and stores only hash in database

#### Scenario: API response security
- **WHEN** API returns user object
- **THEN** response includes user_id, email, roles BUT NOT password or password_hash

---

### Requirement: Token validation on protected endpoints
All protected API endpoints SHALL validate JWT token and extract user identity. Invalid or expired tokens SHALL return 401 Unauthorized.

#### Scenario: Valid token on protected endpoint
- **WHEN** request includes valid Authorization header "Bearer <token>"
- **THEN** system verifies token signature, extracts user_id, and allows request to proceed

#### Scenario: Expired token
- **WHEN** request uses JWT token past expiration time
- **THEN** system returns 401 Unauthorized with message "Token expired"

#### Scenario: Missing authorization header
- **WHEN** request to protected endpoint has no Authorization header
- **THEN** system returns 401 Unauthorized

## ADDED Requirements

### Requirement: Audit logging for sensitive operations
The system SHALL log all sensitive operations including: user creation, role assignment, permission changes, project creation, KPI adjustments, and task deadline changes. Each log includes timestamp, user, action, and affected resource.

#### Scenario: Log user creation
- **WHEN** admin creates new user account
- **THEN** system creates audit_system_logs record: action="user_created", user_id={admin_id}, timestamp, details={new_user_id, email}

#### Scenario: Log permission assignment
- **WHEN** admin assigns permission to role
- **THEN** system logs: action="permission_assigned", role_id, permission_id, assigned_by={admin_id}, timestamp

#### Scenario: Log KPI adjustment
- **WHEN** PM manually adjusts worker KPI score
- **THEN** system logs: action="kpi_adjusted", worker_id, project_id, old_score, new_score, reason, pm_user_id, timestamp

---

### Requirement: User activity logging
The system SHALL log user activity including: login, logout, API calls (success and failures), failed authentication attempts, and permission denials.

#### Scenario: Log successful login
- **WHEN** user successfully authenticates
- **THEN** system creates user_logs record: action="login", user_id, timestamp, ip_address (if captured)

#### Scenario: Log failed login
- **WHEN** user submits invalid password
- **THEN** system logs: action="failed_login", email, timestamp, ip_address; helps detect brute force attacks

#### Scenario: Log unauthorized access attempt
- **WHEN** user attempts operation without permission
- **THEN** system logs: action="unauthorized_access", user_id, requested_resource, timestamp

#### Scenario: API call logging
- **WHEN** user calls protected API endpoint
- **THEN** system logs: action="api_call", endpoint, method, user_id, status_code, timestamp (can be high-volume; consider sampling)

---

### Requirement: Commit change logging
The system SHALL log all commit-related operations including: sync job results, attribution changes, and anomalies.

#### Scenario: Log commit sync
- **WHEN** commit sync job completes for project
- **THEN** system creates commit_change_logs record: action="commit_sync", project_id, commits_fetched, commits_failed, timestamp, sync_duration

#### Scenario: Log attribution correction
- **WHEN** admin corrects commit attribution to different worker
- **THEN** system logs: action="commit_attribution_corrected", commit_id, old_worker_id, new_worker_id, admin_id, timestamp

---

### Requirement: Change history for core entities
The system SHALL maintain change history for projects, tasks, and teams. History tracks field changes with before/after values.

#### Scenario: Track project status change
- **WHEN** project status changes from "planning" to "active"
- **THEN** system logs to project_task_histories: action="status_changed", field="status", old_value="planning", new_value="active", user_id, timestamp

#### Scenario: Task deadline update
- **WHEN** PM changes task deadline from 2024-02-15 to 2024-02-20
- **THEN** system logs: field="deadline", old_value="2024-02-15", new_value="2024-02-20", user_id, timestamp

#### Scenario: View entity history
- **WHEN** user requests GET /projects/{project_id}/history
- **THEN** system returns chronological list of all changes with timestamps and users

---

### Requirement: Audit log retention and archival
Audit logs SHALL be retained per data retention policy (e.g., 1 year for user_logs, 3 years for audit_system_logs). Logs SHALL be archived to cold storage when aged.

#### Scenario: Archive old logs
- **WHEN** archival job runs and audit_system_logs older than 3 years exist
- **THEN** system moves logs to archive storage (S3, cold storage); retains metadata for search

#### Scenario: Retrieve archived log
- **WHEN** admin requests to search logs from 2021
- **THEN** system retrieves from archive; logs search action

---

### Requirement: Audit log security and immutability
Audit logs SHALL not be editable or deletable by regular users. Only system admins can view logs. Log records shall be immutable (no UPDATE operations after INSERT).

#### Scenario: Prevent audit log modification
- **WHEN** any user attempts to UPDATE or DELETE audit_system_logs record
- **THEN** system returns error; operations are blocked at database level (no soft deletes)

#### Scenario: Admin-only access
- **WHEN** engineer attempts to query GET /audit-logs
- **THEN** system returns 403 Forbidden; only admin role can access

---

### Requirement: Audit log querying and filtering
Admins SHALL be able to query audit logs by date range, user, action type, and affected resource for investigation and compliance.

#### Scenario: Query logs by action
- **WHEN** admin requests GET /audit-logs?action=permission_assigned&date_from=2024-01-01&date_to=2024-01-31
- **THEN** system returns matching audit records with details

#### Scenario: Query logs by user
- **WHEN** admin requests GET /audit-logs?user_id={id}
- **THEN** system returns all actions performed by that user in chronological order

#### Scenario: Search affected resource
- **WHEN** admin requests GET /audit-logs?resource_id={project_id}&resource_type=project
- **THEN** system returns all changes to that project

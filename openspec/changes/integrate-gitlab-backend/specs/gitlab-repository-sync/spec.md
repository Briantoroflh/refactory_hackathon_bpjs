# GitLab Repository Sync Specification

## ADDED Requirements

### Requirement: Link GitLab repository to project

The system SHALL allow administrators to link a GitLab repository to a platform project, establishing a one-to-one mapping. The system SHALL store the GitLab project ID, repository URL, and API credentials securely.

#### Scenario: Successfully link repository
- **WHEN** an admin calls `POST /api/v1/repositories/gitlab/link` with a valid project ID and GitLab project ID
- **THEN** the system creates a `GitLabRepository` record, encrypts and stores the API credentials, and returns the repository metadata with status code 201

#### Scenario: Fail to link with invalid project
- **WHEN** an admin attempts to link a repository with a non-existent project ID
- **THEN** the system returns a 404 error with message "Project not found"

#### Scenario: Fail to link with invalid GitLab credentials
- **WHEN** an admin attempts to link a repository with invalid GitLab API credentials
- **THEN** the system validates credentials against GitLab API and returns a 401 error if invalid

#### Scenario: Prevent duplicate links
- **WHEN** an admin attempts to link a project that is already linked to another GitLab repository
- **THEN** the system returns a 409 error with message "Project already linked to a GitLab repository"

### Requirement: Retrieve linked repository metadata

The system SHALL provide an endpoint to retrieve metadata for a GitLab repository linked to a project, including GitLab project ID, repository URL, and last sync timestamp.

#### Scenario: Get repository metadata for linked project
- **WHEN** a user calls `GET /api/v1/repositories/{project_id}/gitlab`
- **THEN** the system returns repository metadata (GitLab project ID, URL, last sync time) with status code 200

#### Scenario: Get repository for unlinked project
- **WHEN** a user calls the endpoint for a project without a linked repository
- **THEN** the system returns a 404 error

### Requirement: Unlink GitLab repository from project

The system SHALL allow administrators to unlink a GitLab repository from a project, effectively disabling further commit synchronization for that project.

#### Scenario: Successfully unlink repository
- **WHEN** an admin calls `DELETE /api/v1/repositories/{project_id}/gitlab`
- **THEN** the system soft-deletes the `GitLabRepository` record, prevents future syncs, and returns status code 204

#### Scenario: Audit logging for unlink operation
- **WHEN** a repository is unlinked
- **THEN** the system logs this action to the audit log with the admin's user ID and timestamp

### Requirement: Automatic repository creation on project creation

The system SHALL support automatic GitLab repository creation when a new project is created (optional). If enabled, the system SHALL create a GitLab repository via API and auto-link it.

#### Scenario: Create project with auto GitLab repository
- **WHEN** a user creates a new project with `create_gitlab_repo=true` in the request
- **THEN** the system calls GitLab API to create a repository, auto-links it, and returns the project with repository metadata

#### Scenario: Graceful failure if GitLab creation fails
- **WHEN** GitLab repository creation fails due to API issues
- **THEN** the system creates the project anyway, logs the error, and returns a warning in the response

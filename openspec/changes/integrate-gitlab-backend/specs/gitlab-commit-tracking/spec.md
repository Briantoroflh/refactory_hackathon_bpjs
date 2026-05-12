# GitLab Commit Tracking Specification

## ADDED Requirements

### Requirement: Synchronize commits from GitLab repository

The system SHALL periodically fetch commits from linked GitLab repositories and store them in the database. The system SHALL implement incremental sync using the last sync timestamp to avoid re-fetching historical data.

#### Scenario: Successful commit sync
- **WHEN** the background sync job runs for a linked repository
- **THEN** the system fetches commits since the last sync timestamp, stores them in the `Commit` table, and updates the `last_sync_timestamp`

#### Scenario: Handle empty commits on first sync
- **WHEN** a repository is first linked and sync runs
- **THEN** the system fetches commits from a default lookback period (e.g., 90 days) and stores all of them

#### Scenario: Graceful handling of GitLab API errors
- **WHEN** GitLab API returns an error during sync (e.g., 429 rate limit, 500 server error)
- **THEN** the system retries with exponential backoff (1s, 2s, 4s), logs the error to the audit log, and skips the repository for this sync cycle without crashing

#### Scenario: Pagination support for large repositories
- **WHEN** a repository has more than the API page limit of commits (e.g., 100+ commits per page)
- **THEN** the system automatically pages through all results and stores all commits

### Requirement: Store commit metadata

The system SHALL store detailed commit metadata including git hash, author, committer, message, timestamp, and branch information.

#### Scenario: Store commit with full metadata
- **WHEN** a commit is fetched from GitLab API
- **THEN** the system stores: `git_hash`, `author_name`, `author_email`, `message`, `committed_at` timestamp, `branch`, and `repository_id`

#### Scenario: Handle commits with missing optional fields
- **WHEN** a commit lacks optional fields like committer email
- **THEN** the system stores available fields and uses NULL for missing optional data

### Requirement: Query commits by project and filters

The system SHALL provide endpoints to query commits by project with optional filters (date range, author, branch).

#### Scenario: Get commits for a project
- **WHEN** a user calls `GET /api/v1/commits?project_id=X`
- **THEN** the system returns a paginated list of commits for that project sorted by timestamp descending

#### Scenario: Filter commits by date range
- **WHEN** a user calls `GET /api/v1/commits?project_id=X&days=30`
- **THEN** the system returns commits from the last 30 days

#### Scenario: Filter commits by author
- **WHEN** a user calls `GET /api/v1/commits?project_id=X&author=john@example.com`
- **THEN** the system returns commits authored by that email

#### Scenario: Combine multiple filters
- **WHEN** a user calls with multiple filter parameters
- **THEN** the system applies all filters (AND logic) and returns matching commits

### Requirement: Prevent duplicate commits

The system SHALL ensure that commits are not duplicated in the database, even if sync runs multiple times.

#### Scenario: Skip already-synced commit
- **WHEN** a sync job runs and encounters a commit that already exists (matched by git hash and repository ID)
- **THEN** the system skips it and does not insert a duplicate record

#### Scenario: Detect hash collisions
- **WHEN** a commit with an identical hash is attempted to be inserted (should be extremely rare)
- **THEN** the system treats it as a duplicate and logs the anomaly to audit log

### Requirement: Background sync scheduling

The system SHALL run commit synchronization automatically on a configurable schedule without requiring manual intervention.

#### Scenario: Sync runs automatically every 15 minutes
- **WHEN** the application starts
- **THEN** the system initializes a background job that syncs all linked repositories every 15 minutes (configurable via `GITLAB_SYNC_INTERVAL_MINUTES`)

#### Scenario: Manual sync trigger
- **WHEN** an admin calls `POST /api/v1/repositories/gitlab/sync?project_id=X`
- **THEN** the system immediately syncs that project and returns the number of new commits

#### Scenario: No crash on concurrent sync
- **WHEN** multiple sync jobs attempt to run concurrently
- **THEN** the system uses database-level locks or row-level locking to prevent race conditions and ensure data consistency

## ADDED Requirements

### Requirement: Commit tracking data storage
The system SHALL store commits fetched from linked Git repositories. Each commit record includes: commit_hash, author, timestamp, message, file_changes, and project_id.

#### Scenario: Store new commit
- **WHEN** commit sync job fetches new commit from GitHub with hash "abc123def456", author "john@example.com", message "Fix: Handle null pointer exception"
- **THEN** system creates project_commit_tracking record with all details, prevents duplicate on re-sync

#### Scenario: Commit with file metadata
- **WHEN** commit includes changes to 5 files (3 modified, 1 added, 1 deleted)
- **THEN** system stores file change summary in commit record for analytics

---

### Requirement: Commit synchronization from Git platforms
The system SHALL periodically sync commits from linked GitHub/GitLab repositories. Sync job queries repository since last sync timestamp, avoiding duplicates.

#### Scenario: Scheduled sync job
- **WHEN** sync job runs at hourly interval for all active projects
- **THEN** system queries GitHub API for new commits since last_sync_timestamp, inserts new records, logs sync result

#### Scenario: Sync failure handling
- **WHEN** GitHub API returns 401 Unauthorized (token expired)
- **THEN** system logs error to audit trail, skips that project, continues with others, retries on next cycle

#### Scenario: Commit deduplication
- **WHEN** commit "abc123" already exists in database and sync fetches it again
- **THEN** system skips insertion (idempotent)

---

### Requirement: Commit attribution to workers
Each commit SHALL be matched to a worker based on Git author email. Unmatched commits are logged for manual review.

#### Scenario: Successful commit attribution
- **WHEN** commit has author_email="alice@company.com" matching worker email in database
- **THEN** system links commit to worker_id; makes commit queryable per worker

#### Scenario: Unmatched author
- **WHEN** commit has author_email="contractor@external.com" not in worker database
- **THEN** system stores commit with null worker_id, logs to audit trail for investigation

#### Scenario: Email alias matching
- **WHEN** worker has primary email "alice@company.com" and GitHub email "alice.smith@github.com"
- **THEN** system matches commits from GitHub email to worker if admin configured alias mapping

---

### Requirement: Commit analytics and metrics
The system SHALL calculate commit frequency, file change statistics, and contribution metrics per worker per project.

#### Scenario: Commit frequency calculation
- **WHEN** evaluating worker over 4-week project period with 45 commits
- **THEN** system calculates frequency as 45 commits, average 11 commits/week

#### Scenario: File change distribution
- **WHEN** aggregating commits from worker over project
- **THEN** system calculates: total_files_changed=120, avg_files_per_commit=2.67, file_types=[.py: 80, .js: 30, .sql: 10]

#### Scenario: Contribution metrics
- **WHEN** evaluating project team commits
- **THEN** system shows per-worker: total_commits, lines_added, lines_removed, files_changed

---

### Requirement: Commit query and filtering
The system SHALL support querying commits by project, worker, date range, file path, and commit message.

#### Scenario: Commits by worker
- **WHEN** user requests GET /projects/{project_id}/commits?worker_id={id}&date_from=2024-01-01&date_to=2024-01-31
- **THEN** system returns commits by that worker in date range

#### Scenario: Search commits by message
- **WHEN** user requests GET /commits?message_search="bugfix"
- **THEN** system returns commits with "bugfix" in message across accessible projects

#### Scenario: File history
- **WHEN** user requests GET /projects/{project_id}/commits?file_path="app/models.py"
- **THEN** system returns all commits touching that file, in reverse chronological order

---

### Requirement: Commit data retention and privacy
Commit data SHALL be retained per data retention policy. Sensitive information (credentials, keys) in commit messages SHALL be masked.

#### Scenario: Mask sensitive data in commit message
- **WHEN** commit message contains "password=abc123" or "API_KEY=xyz"
- **THEN** system masks sensitive patterns before storage and display

#### Scenario: Data retention enforcement
- **WHEN** commit older than retention period (e.g., 2 years) and purge job runs
- **THEN** system archives commit to cold storage or deletes per policy; logs action

---

### Requirement: Commit access control
Workers SHALL view commits for projects they're members of. Non-members cannot see project commits.

#### Scenario: Team member views project commits
- **WHEN** engineer who is project team member requests GET /projects/{project_id}/commits
- **THEN** system returns all commits for that project

#### Scenario: Non-member access denied
- **WHEN** user not in project team requests commits
- **THEN** system returns 403 Forbidden

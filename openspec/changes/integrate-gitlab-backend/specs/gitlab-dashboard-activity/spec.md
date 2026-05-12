# GitLab Dashboard Activity Specification

## ADDED Requirements

### Requirement: Display commit activity on main dashboard

The system SHALL display commit activity metrics on the main dashboard, including commit frequency trends, contributor counts, and recent activity visualization.

#### Scenario: Show commit count over time
- **WHEN** a user opens the main dashboard
- **THEN** the system displays a line or bar chart showing commits per day or week for the selected time period (e.g., last 30 days)

#### Scenario: Display top contributors
- **WHEN** a user views the dashboard
- **THEN** the system shows a list or chart of top contributors by commit count, with their names and email addresses

#### Scenario: Show recent commits
- **WHEN** a user views the dashboard activity section
- **THEN** the system displays the 10 most recent commits with git hash (short form), author, commit message, and timestamp

#### Scenario: Filter activity by project
- **WHEN** a user selects a specific project from a dropdown
- **THEN** the system updates all dashboard charts and lists to show activity only for that project

#### Scenario: Configurable time range
- **WHEN** a user selects a different time range (e.g., 7 days, 30 days, 90 days)
- **THEN** the system updates all dashboard metrics to reflect the selected period

### Requirement: Calculate commit frequency metrics

The system SHALL compute commit frequency metrics (commits per day, average commits per contributor) and display them as KPI cards on the dashboard.

#### Scenario: Display average commits per day
- **WHEN** a user views the dashboard
- **THEN** the system displays a KPI card showing average commits per day for the selected time range (calculated as total commits / days in range)

#### Scenario: Display active contributors metric
- **WHEN** a user views the dashboard
- **THEN** the system displays the count of unique contributors in the selected time range

#### Scenario: Display commit velocity
- **WHEN** a user views the dashboard
- **THEN** the system displays a trend indicator (up/down/stable) showing whether commit activity is increasing, decreasing, or stable compared to the previous period

### Requirement: Real-time dashboard updates

The system SHALL refresh dashboard metrics after each commit sync operation, ensuring data is no more than sync interval stale (e.g., 15 minutes).

#### Scenario: Metrics update after sync
- **WHEN** the background sync job completes successfully
- **THEN** the system updates pre-computed metrics in the database (or cache) for fast dashboard queries

#### Scenario: Dashboard reflects latest commits
- **WHEN** a user refreshes the dashboard page
- **THEN** the system displays metrics computed from all synced commits, with a "last updated" timestamp

#### Scenario: Handle missing data gracefully
- **WHEN** a project has no commits yet
- **THEN** the dashboard displays "No commits" and shows default empty states, not errors

### Requirement: Branch activity visualization

The system SHALL display per-branch commit activity, allowing users to understand development on different branches.

#### Scenario: Show commits per branch
- **WHEN** a user views the dashboard activity section
- **THEN** the system displays a breakdown of commits by branch (main, develop, feature branches, etc.)

#### Scenario: Highlight active branches
- **WHEN** a user views the dashboard
- **THEN** the system highlights the 5 most active branches by commit count in the last period

#### Scenario: Filter by branch
- **WHEN** a user selects a specific branch from the branch list
- **THEN** the system updates all dashboard metrics to show activity only for that branch

### Requirement: Access control for dashboard data

The system SHALL enforce access control such that users can only view commit activity for projects they have access to.

#### Scenario: User sees only accessible projects
- **WHEN** a user with limited project access opens the dashboard
- **THEN** the system displays only projects the user has `view` permission for

#### Scenario: Audit log dashboard access
- **WHEN** a user accesses the dashboard
- **THEN** the system logs this access to the audit log (non-sensitive view log, not per metric)

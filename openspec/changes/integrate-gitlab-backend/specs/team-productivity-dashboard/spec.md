# Team Productivity Dashboard Specification

## ADDED Requirements

### Requirement: Integrate GitLab commit metrics into main dashboard

The system SHALL enhance the existing team productivity dashboard to display GitLab commit activity metrics alongside existing KPI data.

#### Scenario: Dashboard displays GitLab section
- **WHEN** a user with linked GitLab repositories opens the dashboard
- **THEN** the dashboard displays a new "GitLab Activity" section with commit metrics, contributor info, and health status

#### Scenario: Dashboard omits GitLab section for unlinked projects
- **WHEN** a user views a project without a linked GitLab repository
- **THEN** the GitLab Activity section is either hidden or shows "Not linked to GitLab"

#### Scenario: Dashboard integrates existing KPI with new GitLab data
- **WHEN** a user views the productivity dashboard
- **THEN** existing KPIs (engineer scores, team metrics) are displayed alongside new GitLab commit data in the same view (not separated into tabs)

#### Scenario: Consistent time period filtering
- **WHEN** a user selects a time period filter (7 days, 30 days, 90 days)
- **THEN** both existing KPI metrics and GitLab commit metrics use the same time period

### Requirement: Display consolidated metrics

The system SHALL present a unified view of team productivity combining traditional KPIs with GitLab activity metrics.

#### Scenario: Show total commits in period
- **WHEN** a user views the dashboard for a team
- **THEN** the system displays total commits across all linked projects in the selected time period

#### Scenario: Show active contributors from GitLab
- **WHEN** a user views the dashboard
- **THEN** the system displays the count of unique contributors making commits (can differ from team member count due to external contributors)

#### Scenario: Correlate KPI scores with commit activity
- **WHEN** a user views an engineer's KPI score
- **THEN** the system can link to their commit activity on the dashboard (future enhancement for deeper insights)

### Requirement: Project-level dashboard widgets

The system SHALL provide dashboard widgets that show project-specific GitLab activity in the context of existing project metrics.

#### Scenario: Project card includes commit badge
- **WHEN** a user views a project card on the dashboard
- **THEN** it displays the number of commits in the selected period and a health indicator (e.g., "15 commits • Healthy")

#### Scenario: Recent commits listed on dashboard
- **WHEN** a user views the dashboard
- **THEN** they see a "Recent Activity" section listing the 5 most recent commits across all projects with author and timestamp

#### Scenario: Branch activity summary
- **WHEN** a user views the dashboard
- **THEN** they see which branches have been most active (e.g., "main: 45 commits, develop: 32 commits, feature/x: 10 commits")

### Requirement: Dashboard performance with GitLab data

The system SHALL ensure dashboard load times remain acceptable even with new GitLab metrics by using pre-computed or cached data.

#### Scenario: Dashboard loads in under 2 seconds
- **WHEN** a user opens the productivity dashboard
- **THEN** the page renders within 2 seconds using cached/pre-computed metrics (not real-time calculations)

#### Scenario: Metrics update on sync completion
- **WHEN** a GitLab commit sync job completes
- **THEN** the system updates cached metrics so the dashboard reflects new data within the next sync cycle (max 15 minutes stale)

#### Scenario: Lazy load charts for performance
- **WHEN** a user opens the dashboard
- **THEN** charts below the fold are loaded lazily to improve initial page load time

### Requirement: Dashboard customization

The system SHALL allow users to customize which metrics appear on their dashboard.

#### Scenario: Toggle GitLab activity visibility
- **WHEN** a user opens dashboard settings
- **THEN** they can toggle the "GitLab Activity" section on/off for their personal view

#### Scenario: Save dashboard preferences
- **WHEN** a user customizes dashboard widgets and saves
- **THEN** the system persists their preferences and shows the same layout on next login

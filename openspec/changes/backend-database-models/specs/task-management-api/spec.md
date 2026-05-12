## ADDED Requirements

### Requirement: Task creation and assignment
The system SHALL allow creation of tasks within projects. Each task has title, description, story points, assignee, and deadline. Tasks belong to exactly one project.

#### Scenario: Create task
- **WHEN** PM or team lead submits task creation with title, description, story_points (1-21), assignee_id, and deadline
- **THEN** system creates task with status="backlog", version=1, and returns task object with task_id

#### Scenario: Invalid story points
- **WHEN** user submits task with story_points=0 or story_points=22
- **THEN** system returns 422 Unprocessable Entity with validation error

#### Scenario: Assign to non-existent user
- **WHEN** user attempts to assign task to user not in project team
- **THEN** system returns 400 Bad Request with message "User not in project team"

---

### Requirement: Task status workflow
Tasks SHALL progress through statuses: backlog → in_progress → in_review → completed → closed. Status changes SHALL log timestamp, user, and reason in project_task_histories.

#### Scenario: Move task to in_progress
- **WHEN** engineer changes task status from "backlog" to "in_progress"
- **THEN** system updates status, increments version, logs change with user_id and timestamp

#### Scenario: Review completion
- **WHEN** engineer moves task from "in_review" to "completed"
- **THEN** system updates status, validates completion time, triggers KPI recalculation for worker

#### Scenario: Invalid status transition
- **WHEN** user attempts transition "completed" → "backlog"
- **THEN** system returns 400 Bad Request

---

### Requirement: Task workload tracking
The system SHALL track time spent on each task. Workload entries include date, hours_worked, description, and user. Multiple entries allowed per task per day.

#### Scenario: Log work hours
- **WHEN** engineer submits workload entry with date, hours_worked=4, description="Implementation phase 1"
- **THEN** system creates project_task_workloads record, updates cumulative task_effort

#### Scenario: Workload exceeds daily maximum
- **WHEN** engineer submits workload entry exceeding 8 hours for same day
- **THEN** system logs warning in audit trail but allows submission (prevents hard-blocking legitimate work)

---

### Requirement: Task comments and collaboration
The system SHALL allow team members to add comments to tasks. Comments include author, timestamp, and text. Comments support @mentions of team members.

#### Scenario: Add comment to task
- **WHEN** engineer submits comment text on task with @team_lead mention
- **THEN** system creates comment record, sends notification to mentioned user, stores comment

#### Scenario: Comment history
- **WHEN** user queries GET /tasks/{task_id}/comments
- **THEN** system returns all comments sorted by timestamp, including author and creation time

---

### Requirement: Task deadline and priority management
Tasks have deadline dates and priority levels (high, medium, low). System SHALL warn when tasks approach deadline with insufficient progress.

#### Scenario: Set task priority
- **WHEN** PM updates task priority to "high"
- **THEN** system updates task, reflects priority in task lists and dashboard

#### Scenario: Deadline warning
- **WHEN** task deadline is 2 days away and status is still "in_progress"
- **THEN** system logs warning event in audit trail (for dashboard alerts)

---

### Requirement: Concurrent task updates with optimistic locking
The system SHALL prevent concurrent modifications conflicts using version columns. Client must send current version; updates fail if version mismatch.

#### Scenario: Successful update with matching version
- **WHEN** client sends PATCH /tasks/{task_id} with version=5 matching database
- **THEN** system updates task, increments version to 6, returns updated task with new version

#### Scenario: Update conflict (stale version)
- **WHEN** client sends PATCH /tasks/{task_id} with version=4 but database has version=6
- **THEN** system returns 409 Conflict with current version; client retries with fresh version

---

### Requirement: Task summary and history
The system SHALL generate summaries of task activity. Summaries include completion date, total effort, contributors, and status changes.

#### Scenario: Generate task summary
- **WHEN** task transitions to "completed"
- **THEN** system auto-generates project_task_summaries record with total_effort, completion_date, contributors list

#### Scenario: View task history
- **WHEN** user requests GET /tasks/{task_id}/history
- **THEN** system returns all status changes, worklog entries, and comments in chronological order

---

### Requirement: Task listing and filtering
The system SHALL provide paginated task lists with filtering by project, assignee, status, priority, and date range.

#### Scenario: List tasks in project
- **WHEN** user requests GET /projects/{project_id}/tasks?status=in_progress&page=1
- **THEN** system returns paginated tasks filtered by status, with assignee and deadline visible

#### Scenario: My assigned tasks
- **WHEN** engineer requests GET /tasks/assigned-to-me
- **THEN** system returns all tasks assigned to current user across all accessible projects

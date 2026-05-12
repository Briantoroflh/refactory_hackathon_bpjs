## ADDED Requirements

### Requirement: Project creation with team assignment
The system SHALL allow project managers to create new projects with name, description, and link them to teams. Each project belongs to one workspace.

#### Scenario: Create project with team
- **WHEN** project manager submits project name, description, and team_id
- **THEN** system creates project, links to team, sets status to "planning", and returns project object with project_id

#### Scenario: Prevent duplicate project names in workspace
- **WHEN** project manager attempts to create project with name already in use in same workspace
- **THEN** system returns 409 Conflict with message "Project name already exists in workspace"

#### Scenario: Permission enforcement on creation
- **WHEN** engineer (non-PM) attempts to create project
- **THEN** system returns 403 Forbidden

---

### Requirement: Project status workflow
The system SHALL enforce project status progression: planning → active → completed → archived. Status changes SHALL be logged in project history.

#### Scenario: Transition from planning to active
- **WHEN** project manager changes project status from "planning" to "active"
- **THEN** system updates status, logs change with timestamp and PM user_id in project_task_histories

#### Scenario: Invalid status transition
- **WHEN** project manager attempts invalid transition (e.g., "completed" to "planning")
- **THEN** system returns 400 Bad Request with message "Invalid status transition"

---

### Requirement: Project repository linking
Each project SHALL support linking to exactly one Git repository (GitHub/GitLab). Repository URL and credentials SHALL be stored for commit monitoring.

#### Scenario: Link repository to project
- **WHEN** project manager provides repository URL and access token
- **THEN** system stores repository details and validates connectivity by fetching repo metadata

#### Scenario: Repository validation failure
- **WHEN** provided repository URL is invalid or token lacks permissions
- **THEN** system returns 400 Bad Request with validation error

---

### Requirement: Project read operations
Project managers, team leads, and team members SHALL be able to read project details. Details SHALL include project name, description, status, team, repository, and creation date.

#### Scenario: PM reads project details
- **WHEN** project manager requests GET /projects/{project_id}
- **THEN** system returns project object with full details

#### Scenario: Team member reads project
- **WHEN** engineer who is member of project team requests GET /projects/{project_id}
- **THEN** system returns project object (same details as PM)

#### Scenario: Unauthorized read attempt
- **WHEN** user not in project team attempts to read project
- **THEN** system returns 403 Forbidden

---

### Requirement: Project update operations
Project managers SHALL be able to update project name, description, team assignment, and status. Updates SHALL be logged in project history.

#### Scenario: Update project metadata
- **WHEN** PM sends PATCH /projects/{project_id} with new description
- **THEN** system updates project, logs change to project_task_histories with timestamp and user_id

#### Scenario: Prevent concurrent updates
- **WHEN** PM updates project with stale version number
- **THEN** system returns 409 Conflict (optimistic locking)

---

### Requirement: Project list and filtering
The system SHALL return paginated list of projects accessible to authenticated user. Filtering by status, team, and date range SHALL be supported.

#### Scenario: List user's projects
- **WHEN** PM requests GET /projects?page=1&limit=20
- **THEN** system returns paginated list of projects where user has access (via team membership or PM role)

#### Scenario: Filter by status
- **WHEN** user requests GET /projects?status=active&limit=50
- **THEN** system returns only projects with status="active"

---

### Requirement: Project workspace management
The system SHALL organize projects within workspaces. A workspace contains multiple projects and their associated data (teams, KPIs, analytics).

#### Scenario: Create project in workspace
- **WHEN** PM creates project and specifies workspace_id
- **THEN** system creates project_workspaces link and isolates project data to workspace

#### Scenario: List projects in workspace
- **WHEN** user requests GET /workspaces/{workspace_id}/projects
- **THEN** system returns all projects in that workspace user can access

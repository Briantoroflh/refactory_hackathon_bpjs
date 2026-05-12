## ADDED Requirements

### Requirement: Team creation and management
The system SHALL allow admins to create teams with name, description, and category. Teams are organizational units containing multiple workers.

#### Scenario: Create team
- **WHEN** admin submits team creation with name="Backend Team", description="Python microservices", category_id={category}
- **THEN** system creates team record; team_id is returned; team status defaults to "active"

#### Scenario: Update team details
- **WHEN** admin updates team description
- **THEN** system updates team record; logs change to audit trail

#### Scenario: Deactivate team
- **WHEN** admin sets team status to "inactive"
- **THEN** system prevents new project assignments to team but preserves historical data

---

### Requirement: Team member management
The system SHALL allow team leads and admins to add/remove workers to/from teams. Team membership tracks join date and role.

#### Scenario: Add worker to team
- **WHEN** team lead requests to add engineer to team
- **THEN** system creates project_team_members record linking worker_id to team; logs action

#### Scenario: Remove worker from team
- **WHEN** team lead removes worker from team
- **THEN** system marks record inactive or deletes; preserves historical data for KPI calculations

#### Scenario: Worker has multiple team memberships
- **WHEN** worker is added to 3 different teams
- **THEN** system maintains separate project_team_members records per team; worker can be assigned from any team

---

### Requirement: Division and category organization
The system SHALL support organizational hierarchies using divisions (e.g., Engineering, Product, Operations) and categories (e.g., Backend, Frontend, QA).

#### Scenario: Create division
- **WHEN** admin creates division "Engineering" with description and status="active"
- **THEN** system creates division record; can be referenced when organizing teams

#### Scenario: Create category
- **WHEN** admin creates category "Backend" under division "Engineering"
- **THEN** system creates category record; teams can be tagged with category for filtering

#### Scenario: Team hierarchy query
- **WHEN** user requests teams by division "Engineering"
- **THEN** system returns all teams and their members in that division

---

### Requirement: Team member roles within teams
Team members have roles (e.g., member, lead) defining their responsibilities and permissions within the team context.

#### Scenario: Assign team lead role
- **WHEN** admin assigns worker role="lead" in team
- **THEN** system grants team lead permissions (approve worklog, adjust KPI, manage members)

#### Scenario: Regular member permissions
- **WHEN** worker with role="member" attempts to remove another member
- **THEN** system returns 403 Forbidden (insufficient team role)

---

### Requirement: Team availability and capacity tracking
The system SHALL track team capacity (total available effort per sprint) and utilization (assigned effort vs available).

#### Scenario: Set team capacity
- **WHEN** team lead sets capacity=160 hours for 4-week sprint (40 hours/week × 4)
- **THEN** system stores capacity; available_effort=160 initially

#### Scenario: Track utilization
- **WHEN** tasks are assigned to team members with total 145 hours
- **THEN** system shows utilization_rate=90.6%, remaining_capacity=15 hours

#### Scenario: Capacity warning
- **WHEN** new task assignment would exceed team capacity
- **THEN** system logs warning but allows assignment; warns in UI

---

### Requirement: Team listing and filtering
The system SHALL support querying teams by division, category, status, and membership.

#### Scenario: List teams by division
- **WHEN** user requests GET /teams?division=Engineering
- **THEN** system returns all teams in Engineering division with member counts

#### Scenario: My teams
- **WHEN** worker requests GET /teams/my-teams
- **THEN** system returns teams where user is member

#### Scenario: Team details with members
- **WHEN** user requests GET /teams/{team_id}
- **THEN** system returns team info, all members with roles, and team capacity metrics

---

### Requirement: Team access control
Admins and team leads can manage team membership. Regular members can view team details. Non-members cannot see team members or capacity.

#### Scenario: Team lead manages members
- **WHEN** team lead requests GET /teams/{team_id}/members and PUT to add/remove
- **THEN** system grants access; logs changes

#### Scenario: Non-member access denied
- **WHEN** user not in team attempts to view members list
- **THEN** system returns 403 Forbidden

---

### Requirement: Worker profile and metadata
Workers have profiles including name, email, contact info, skills, and employment status. Workers can be active or inactive.

#### Scenario: Create worker profile
- **WHEN** admin creates worker with name="Alice", email="alice@company.com", status="active"
- **THEN** system creates worker record; worker can be assigned to teams and projects

#### Scenario: Update skills
- **WHEN** worker updates profile with skills=["Python", "FastAPI", "PostgreSQL"]
- **THEN** system stores skills; used for project matching and AI recommendations

#### Scenario: Inactive worker
- **WHEN** admin deactivates worker (status="inactive")
- **THEN** system prevents new assignments; preserves historical data for KPI review

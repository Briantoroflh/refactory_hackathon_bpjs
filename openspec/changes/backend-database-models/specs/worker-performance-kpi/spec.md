## ADDED Requirements

### Requirement: KPI definition per project
The system SHALL allow project managers to define measurable KPIs for each project. KPI definitions include name, metric type, calculation formula, target value, and weighting.

#### Scenario: Create KPI definition
- **WHEN** PM creates KPI "Task Completion Rate" with metric_type="percentage", formula="completed_tasks / assigned_tasks", target=85, weight=0.3
- **THEN** system stores KPI definition in project context, applies to all workers in project

#### Scenario: KPI with calculation formula
- **WHEN** PM defines KPI "Code Quality Score" with custom formula using variables [bugs_fixed, tests_written, reviews_approved]
- **THEN** system stores formula for later evaluation against worker metrics

#### Scenario: Update KPI definition
- **WHEN** PM modifies KPI target from 85% to 90%
- **THEN** system updates definition; new evaluations use updated target; historical evaluations unchanged

---

### Requirement: Worker performance scoring per project
The system SHALL calculate performance scores for each worker per project after project completion. Score is weighted sum of KPI metrics. Score range: 0-100.

#### Scenario: Calculate worker KPI score
- **WHEN** project completes and worker has metrics [completion_rate=90%, code_quality=85%, timeliness=88%] with weights [0.3, 0.4, 0.3]
- **THEN** system calculates score = (90*0.3 + 85*0.4 + 88*0.3) = 87.2; stores in worker_kpi table

#### Scenario: Worker with incomplete metrics
- **WHEN** worker_kpi calculation references missing metric (e.g., incomplete code reviews)
- **THEN** system uses default value (0 or weighted skip) and logs to audit trail for PM review

#### Scenario: Multiple projects
- **WHEN** worker completes projects A, B, C with scores 85, 92, 78
- **THEN** system stores separate worker_kpi record per project; summary shows all scores

---

### Requirement: KPI calculation metrics
KPI calculations SHALL use metrics including: task_completion_rate, average_task_effort, commit_frequency, code_review_participation, and timeliness.

#### Scenario: Task completion metric
- **WHEN** evaluating worker with 15 completed tasks out of 20 assigned
- **THEN** system calculates metric as 15/20 = 75%

#### Scenario: Commit frequency metric
- **WHEN** evaluating worker with 45 commits over 4-week project
- **THEN** system calculates metric as 45 commits; PM defines threshold (e.g., ≥10/week is good)

#### Scenario: Timeliness metric
- **WHEN** evaluating worker with 18 on-time completions out of 20 tasks
- **THEN** system calculates metric as 18/20 = 90%

---

### Requirement: Worker KPI summary report
The system SHALL generate summary reports showing worker performance across all completed projects. Summary includes average score, trend analysis, and peer comparison.

#### Scenario: Generate worker performance summary
- **WHEN** user requests summary for worker across last 3 months of projects
- **THEN** system returns average_score=87.5, trend=[Q1: 82, Q2: 89, Q3: 88], peer_percentile=75th

#### Scenario: Peer comparison
- **WHEN** PM views worker KPI against team average
- **THEN** system shows worker_score=90, team_average=82, difference=+8 (above average)

---

### Requirement: KPI evaluation trigger
KPI scoring SHALL auto-trigger when project transitions to "completed" status. Manual re-evaluation by PM SHALL also be supported.

#### Scenario: Auto-score on project completion
- **WHEN** project status changes to "completed"
- **THEN** system calculates and stores worker_kpi scores for all project members; logs to audit trail

#### Scenario: Manual KPI adjustment
- **WHEN** PM manually updates worker KPI score with notes "Exceptional performance on architecture"
- **THEN** system stores override score, logs adjustment with PM user_id and reason

---

### Requirement: KPI data persistence and auditability
All KPI calculations and adjustments SHALL be logged with timestamp, user, and calculation inputs (for reproducibility). Historical KPI records SHALL not be deleted.

#### Scenario: Audit trail for KPI calculation
- **WHEN** worker_kpi record is created
- **THEN** system logs to audit trail: calculation_date, metrics_used, final_score, calculated_by (system or PM)

#### Scenario: KPI adjustment audit
- **WHEN** PM adjusts KPI score
- **THEN** system logs: old_score, new_score, adjustment_reason, pm_user_id, timestamp

---

### Requirement: Worker KPI access control
Workers SHALL view their own KPI scores. Team leads and PMs SHALL view KPI scores for their team members. Admins can view all scores.

#### Scenario: Worker views own score
- **WHEN** engineer requests GET /workers/{my_id}/kpi-scores
- **THEN** system returns KPI scores for projects where user is/was member

#### Scenario: PM views team scores
- **WHEN** PM requests GET /projects/{project_id}/worker-kpi
- **THEN** system returns KPI scores for all workers in that project

#### Scenario: Non-team-member access denied
- **WHEN** engineer attempts to view KPI score of worker in different project
- **THEN** system returns 403 Forbidden

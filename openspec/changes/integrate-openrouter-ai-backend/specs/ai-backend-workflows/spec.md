## ADDED Requirements

### Requirement: Backend Planning Workflow
The system SHALL provide a backend workflow that generates project plans from structured context and a natural-language prompt.

#### Scenario: Generate project plan
- **WHEN** a project manager issues a planning request with project context
- **THEN** the backend SHALL return a structured plan including milestones, risks, and recommended actions

### Requirement: Backend Sprint Summary Workflow
The system SHALL provide a sprint summary workflow returning completed work, blockers, and next steps.

#### Scenario: Sprint summary generation
- **WHEN** sprint activity context is provided
- **THEN** the backend SHALL return a concise sprint summary

### Requirement: Additional Workflows
The system SHALL provide backend workflows for standup recap, task recommendation, workload suggestion, ticket explanation, documentation helper, bug analysis, and kanban/jobdesk generation.

#### Scenario: Task recommendation
- **WHEN** team workload and task context are provided
- **THEN** the backend SHALL return prioritized recommendations and rationale

#### Scenario: Standup recap
- **WHEN** standup notes are submitted
- **THEN** the backend SHALL return a concise recap with blockers and owners

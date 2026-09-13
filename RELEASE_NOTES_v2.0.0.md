# top-journal-figure-pro v2.0.0

## Unified autonomous workflow

v2.0 integrates the v1.1–v1.9 modules into a resumable fail-closed state machine.

### Added
- `workflow_project.yaml`
- `WORKFLOW_STATE.json`
- unified orchestrator
- stage checkpointing
- resume support
- dry-run/status/reset
- pending-agent-action tracking
- pending-human-review tracking
- workflow handoff generator

### State governance
The workflow distinguishes:
- AUTOMATED completion;
- AGENT_ACTION_REQUIRED;
- HUMAN_REVIEW_REQUIRED;
- BLOCKED;
- COMPLETE.

It cannot self-certify benchmark retrieval, evidence interpretation, manual visual review, or final journal upload-contract closure.

### Final state
`FIGURE_PACKAGE_SUBMISSION_READY`

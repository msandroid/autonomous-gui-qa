# Autonomous Mobile GUI QA - Claude Code Guidelines

This workspace supports autonomous mobile GUI testing, VLM visual assertion, and UI/UX defect detection.

## Available Workflows

1. **Run Autonomous Goal Exploration**:
   `python -m cli.main explore --goal "<Natural Language Goal>" --bundle-id "<Bundle ID>" --platform ios`
2. **Execute Declarative Scenarios**:
   `python -m cli.main scenario --file examples/scenarios/smoke_test.yaml`
3. **Inspect Screenshot**:
   `python -m cli.main inspect --image /path/to/screenshot.png`

## Defect Severity Standards
- **CRITICAL**: App crashes, total blocker, unclickable primary CTA.
- **HIGH**: Text truncation in primary controls, layout overlapping, visual corruption.
- **MEDIUM**: Contrast degradation, slight padding mismatch.
- **LOW**: Minor spacing inconsistency.

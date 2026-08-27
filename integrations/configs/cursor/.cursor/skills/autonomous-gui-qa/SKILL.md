---
name: autonomous-gui-qa
description: Autonomous Mobile GUI Exploration, VLM-Driven Visual Oracle & Defect Detection for iOS and Android apps.
---

# Autonomous GUI QA Skill

## Capabilities
- Operates iOS Simulators and Android devices via natural language goals.
- Audits screenshots using Multimodal VLMs (Gemini / Claude / OpenAI).
- Highlights bounding boxes on defects with severity ratings.
- Generates interactive HTML reports.

## Command Execution
- Autonomous Exploration: `python -m cli.main explore --goal "<Goal>" --platform ios`
- Scenario Testing: `python -m cli.main scenario --file <scenario.yaml>`
- MCP Server: `python -m autonomous_gui_qa.integrations.mcp_server`

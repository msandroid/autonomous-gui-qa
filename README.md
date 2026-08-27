# Autonomous Mobile GUI QA & Visual Oracle System

> **Autonomous GUI Exploration, Semantic Defect Detection & Self-Healing Loop for Mobile Apps (iOS & Android).**

---

## Key Highlights

- **VLM Visual Oracle**: Automatically detects text truncation, layout clipping, z-index overlaps, dark mode contrast issues, and placeholder leaks without writing brittle assertions.
- **Autonomous Agent Loop**: Operates mobile applications naturally via natural language goals (Perceive -> Reason -> Act -> Observe).
- **Multi-Platform Drivers**: Native support for iOS Simulators (`simctl` + System Events) and Android Devices/Emulators (`adb`).
- **Multi-AI Assistant Integrations**: Native support for **Claude Code/Desktop**, **Cursor IDE**, **Google Antigravity**, and **OpenAI Codex**.
- **Visual Annotations**: Bounding boxes with severity labels generated on screenshots using Pillow.
- **HOTL (Human-on-the-Loop) Reporting**: Interactive HTML reports and automatic GitHub Actions PR comments.

---

## Quick Setup

```bash
# Clone & install
git clone https://github.com/msandroid/autonomous-gui-qa.git
cd autonomous-gui-qa
pip install -e ".[all]"

# Set your preferred VLM key
export GEMINI_API_KEY="your-gemini-key"
```

---

## Multi-AI Integrations (Claude / Cursor / Antigravity / Codex)

You can automatically install rules, skills, and configuration schemas into your project workspace with a single command:

```bash
# Install integrations for all supported AI assistants
python -m cli.main setup --target all --dest /path/to/your/project

# Or install for a specific assistant:
python -m cli.main setup --target cursor --dest .
python -m cli.main setup --target claude --dest .
python -m cli.main setup --target antigravity --dest .
python -m cli.main setup --target codex --dest .
```

### Model Context Protocol (MCP) Server
Launch the standard stdio MCP server for Claude Desktop, Cursor, or Antigravity:
```bash
python -m cli.main mcp
# or
python -m autonomous_gui_qa.integrations.mcp_server
```

---

## CLI Usage

### 1. Run Autonomous Goal
```bash
python -m cli.main explore \
  --goal "Change target language to Spanish and verify main screen updates" \
  --bundle-id "Translate.Blue" \
  --platform ios
```

### 2. Run Declarative YAML Scenario
```bash
python -m cli.main scenario \
  --file examples/scenarios/smoke_test.yaml \
  --platform ios \
  --output-dir reports
```

### 3. Inspect a Single Screenshot
```bash
python -m cli.main inspect \
  --image /tmp/screenshot.png
```

---

## Repository Structure

```
autonomous-gui-qa/
├── autonomous_gui_qa/
│   ├── engine/          # VLM Engine, Visual Oracle, Autonomous Agent Loop
│   ├── drivers/         # iOS Simulator Driver & Android ADB Driver
│   ├── reporting/       # Visual Annotator (Pillow) & HTML/MD Reporter
│   ├── scenarios/       # YAML Scenario Schema & Execution Runner
│   └── integrations/    # Standard MCP Server, OpenAI Schemas & Multi-AI Installer
├── cli/                 # Unified CLI Entrypoint (explore, scenario, inspect, mcp, setup)
├── integrations/
│   └── configs/         # Config templates for Claude, Cursor, Antigravity, and Codex
├── examples/            # Example YAML Scenarios
├── docs/                # Architecture & Integration Guides
└── .github/workflows/   # GitHub Actions CI Workflow
```

---

## License
MIT License.

# Autonomous Mobile GUI QA & Visual Oracle System

> **Autonomous GUI Exploration, Semantic Defect Detection & Self-Healing Loop for Mobile Apps (iOS & Android).**

---

## 🌟 Key Highlights

- 👁️ **VLM Visual Oracle**: Automatically detects text truncation, layout clipping, z-index overlaps, dark mode contrast issues, and placeholder leaks without writing brittle assertions.
- 🤖 **Autonomous Agent Loop**: Operates mobile applications naturally via natural language goals (Perceive -> Reason -> Act -> Observe).
- 📱 **Multi-Platform Drivers**: Native support for iOS Simulators (`simctl` + System Events) and Android Devices/Emulators (`adb`).
- 🎨 **Visual Annotations**: Bounding boxes with severity labels generated on screenshots using Pillow.
- 📊 **HOTL (Human-on-the-Loop) Reporting**: Interactive HTML reports and automatic GitHub Actions PR comments.

---

## 🚀 Quick Setup

```bash
# Clone & install
git clone https://github.com/msandroid/autonomous-gui-qa.git
cd autonomous-gui-qa
pip install -e ".[all]"

# Set your preferred VLM key
export GEMINI_API_KEY="your-gemini-key"
```

---

## 🕹️ CLI Usage

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

## 📁 Repository Structure

```
autonomous-gui-qa/
├── autonomous_gui_qa/
│   ├── engine/          # VLM Engine, Visual Oracle, Autonomous Agent Loop
│   ├── drivers/         # iOS Simulator Driver & Android ADB Driver
│   ├── reporting/       # Visual Annotator (Pillow) & HTML/MD Reporter
│   └── scenarios/       # YAML Scenario Schema & Execution Runner
├── cli/                 # Unified CLI Entrypoint (explore, scenario, inspect)
├── examples/            # Example YAML Scenarios
├── docs/                # Architecture & Loop Engineering Guide
└── .github/workflows/   # GitHub Actions CI Workflow
```

---

## 📄 License
MIT License.

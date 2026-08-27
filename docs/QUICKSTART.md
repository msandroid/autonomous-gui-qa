# Quickstart Guide

## 1. Installation

```bash
git clone https://github.com/msandroid/autonomous-gui-qa.git
cd autonomous-gui-qa
pip install -e ".[all]"
```

## 2. Set API Keys

```bash
export GEMINI_API_KEY="your-gemini-key"
# or
export ANTHROPIC_API_KEY="your-anthropic-key"
# or
export OPENAI_API_KEY="your-openai-key"
```

## 3. Usage Examples

### 3.1 Autonomous Exploration Mode
```bash
python -m cli.main explore --goal "Open language picker and select Spanish" --bundle-id "Translate.Blue"
```

### 3.2 Declarative Scenario Mode
```bash
python -m cli.main scenario --file examples/scenarios/smoke_test.yaml
```

### 3.3 Single Screenshot Inspection
```bash
python -m cli.main inspect --image /path/to/screenshot.png
```

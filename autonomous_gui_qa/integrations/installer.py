"""
Installer module: configures Claude, Cursor, Antigravity, and Codex integrations into target workspace.
"""

import os
import shutil
import json

CONFIG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "integrations", "configs"))

def install_integration(target: str, dest_dir: str = ".") -> None:
    """Installs configurations for the specified AI assistant target."""
    dest_dir = os.path.abspath(dest_dir)
    target = target.lower()
    print(f"Installing integration for [{target}] into: {dest_dir}")

    targets = ["claude", "cursor", "antigravity", "codex"] if target == "all" else [target]

    for t in targets:
        src_path = os.path.join(CONFIG_ROOT, t)
        if not os.path.exists(src_path):
            print(f"Warning: Config directory not found: {src_path}")
            continue

        if t == "claude":
            shutil.copy(os.path.join(src_path, "CLAUDE.md"), os.path.join(dest_dir, "CLAUDE_AUTONOMOUS_QA.md"))
            print("Installed Claude configuration (CLAUDE_AUTONOMOUS_QA.md)")

        elif t == "cursor":
            os.makedirs(os.path.join(dest_dir, ".cursor", "rules"), exist_ok=True)
            os.makedirs(os.path.join(dest_dir, ".cursor", "skills", "autonomous-gui-qa"), exist_ok=True)
            shutil.copy(
                os.path.join(src_path, ".cursor", "rules", "autonomous-gui-qa.mdc"),
                os.path.join(dest_dir, ".cursor", "rules", "autonomous-gui-qa.mdc")
            )
            shutil.copy(
                os.path.join(src_path, ".cursor", "skills", "autonomous-gui-qa", "SKILL.md"),
                os.path.join(dest_dir, ".cursor", "skills", "autonomous-gui-qa", "SKILL.md")
            )
            print("Installed Cursor rules & skills (.cursor/rules/autonomous-gui-qa.mdc, .cursor/skills/)")

        elif t == "antigravity":
            os.makedirs(os.path.join(dest_dir, ".agents", "skills", "autonomous-gui-qa"), exist_ok=True)
            shutil.copy(
                os.path.join(src_path, ".agents", "skills", "autonomous-gui-qa", "SKILL.md"),
                os.path.join(dest_dir, ".agents", "skills", "autonomous-gui-qa", "SKILL.md")
            )
            print("Installed Google Antigravity skill (.agents/skills/autonomous-gui-qa/SKILL.md)")

        elif t == "codex":
            os.makedirs(os.path.join(dest_dir, "schemas"), exist_ok=True)
            shutil.copy(
                os.path.join(src_path, "openai_tools.json"),
                os.path.join(dest_dir, "schemas", "openai_tools.json")
            )
            print("Installed OpenAI Codex schemas (schemas/openai_tools.json)")

    print(f"Integration setup complete.")

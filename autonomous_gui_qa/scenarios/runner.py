"""
Scenario Runner: Executes declarative YAML scenarios against a device driver.
"""

import time
import yaml
from typing import List, Dict, Any
from .schema import Scenario
from ..drivers.base import BaseDeviceDriver
from ..engine.oracle import VisualOracle

class ScenarioRunner:
    """Executes structured YAML scenarios."""

    def __init__(self, driver: BaseDeviceDriver, oracle: VisualOracle):
        self.driver = driver
        self.oracle = oracle

    def run_scenario(self, yaml_path: str) -> List[Dict[str, Any]]:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        scenario = Scenario(**data)

        print(f"\n📋 [Scenario] Starting execution: \"{scenario.name}\"")
        results = []

        for idx, step in enumerate(scenario.steps, 1):
            print(f"\n▶️ [Step {idx}/{len(scenario.steps)}] {step.name}")
            for act in step.actions:
                if act.action == "tap" and act.coordinates:
                    self.driver.tap(act.coordinates[0], act.coordinates[1])
                elif act.action == "type" and act.text:
                    self.driver.type_text(act.text)
                elif act.action == "swipe" and act.direction:
                    self.driver.swipe(act.direction)
                elif act.action == "set_appearance" and act.mode:
                    self.driver.set_appearance(act.mode)
                elif act.action == "sleep" and act.duration:
                    time.sleep(act.duration)

            if step.assert_screen:
                img_path = self.driver.take_screenshot(f"{step.name}.png")
                audit = self.oracle.audit_screen(img_path, context_prompt=step.description)
                results.append({
                    "step_name": step.name,
                    "screen_name": step.assert_screen,
                    "image_path": img_path,
                    "is_passed": audit.is_passed,
                    "confidence": audit.confidence,
                    "summary": audit.summary,
                    "defects": [d.dict() for d in audit.defects]
                })

        return results

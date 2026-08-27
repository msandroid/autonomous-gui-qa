"""
Autonomous Mobile GUI Agent: Perceive -> Reason -> Act -> Observe Loop.
"""

import time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .vlm import VLMEngine
from .oracle import VisualOracle, VisualAuditResult
from ..drivers.base import BaseDeviceDriver

class AgentAction(BaseModel):
    thought: str = Field(..., description="Chain of thought reasoning for the next step")
    action_type: str = Field(..., description="TAP | TYPE | SWIPE | BACK | SLEEP | FINISH")
    target_description: str = Field(..., description="Description of the target element")
    coordinates: Optional[List[int]] = Field(None, description="[x, y] in 0-1000 scale for TAP")
    text_input: Optional[str] = Field(None, description="Text string if action_type is TYPE")
    swipe_direction: Optional[str] = Field(None, description="UP | DOWN | LEFT | RIGHT")
    is_goal_achieved: bool = Field(False, description="True if goal is accomplished or exploration step is complete")

SYSTEM_PROMPT_AGENT = """
You are an Autonomous Mobile GUI Exploration Agent.
Your task is to operate the mobile app to achieve a specific goal or perform exploratory quality audit.
Observe the screenshot, reason about the next best interaction, and output your action.

Coordinate space is 0 to 1000:
- (0, 0) is top-left
- (1000, 1000) is bottom-right
- Center is (500, 500)

Action types:
- TAP: Requires coordinates [x, y]
- TYPE: Requires text_input
- SWIPE: Requires swipe_direction (UP, DOWN, LEFT, RIGHT)
- BACK: Tap back or dismiss modal
- SLEEP: Wait for transitions
- FINISH: When goal is achieved or exploration budget reached
"""

class AutonomousGUIAgent:
    """Agent loop orchestrator."""

    def __init__(self, driver: BaseDeviceDriver, vlm_engine: Optional[VLMEngine] = None):
        self.driver = driver
        self.vlm = vlm_engine or VLMEngine()
        self.oracle = VisualOracle(self.vlm)

    def run_goal(self, goal: str, max_steps: int = 10, audit_each_step: bool = True) -> List[Dict[str, Any]]:
        """Runs the agent loop toward a target goal."""
        trajectory = []
        print(f"\n🤖 [Agent] Starting autonomous run for goal: \"{goal}\" (Max steps: {max_steps})")

        for step in range(1, max_steps + 1):
            print(f"\n--- Step {step}/{max_steps} ---")
            screenshot_path = self.driver.take_screenshot(f"step_{step}.png")

            # 1. Visual Oracle Audit (if enabled)
            audit_result = None
            if audit_each_step:
                print("🔍 [Oracle] Auditing current screen state...")
                audit_result = self.oracle.audit_screen(screenshot_path, context_prompt=f"Goal: {goal}, Step: {step}")
                status = "🟢 PASS" if audit_result.is_passed else f"🔴 FAIL ({len(audit_result.defects)} defects)"
                print(f"   Oracle verdict: {status} - {audit_result.summary}")

            # 2. Reason & Decide Action
            prompt = f"Goal: {goal}\nPrevious Steps: {len(trajectory)}\nDecide next action."
            action_data = self.vlm.analyze_image(
                image_path=screenshot_path,
                prompt=prompt,
                system_instruction=SYSTEM_PROMPT_AGENT,
                response_schema=AgentAction
            )
            action = AgentAction(**action_data)
            print(f"🧠 [Reasoning] {action.thought}")
            print(f"🎯 [Action] {action.action_type}: {action.target_description} (Coords: {action.coordinates})")

            # 3. Record Trajectory
            trajectory.append({
                "step": step,
                "screenshot": screenshot_path,
                "audit": audit_result.dict() if audit_result else None,
                "action": action.dict()
            })

            if action.is_goal_achieved or action.action_type == "FINISH":
                print("🎉 [Agent] Goal achieved or finished!")
                break

            # 4. Act
            self._execute_action(action)
            time.sleep(1.5)

        return trajectory

    def _execute_action(self, action: AgentAction):
        if action.action_type == "TAP" and action.coordinates:
            self.driver.tap(action.coordinates[0], action.coordinates[1])
        elif action.action_type == "TYPE" and action.text_input:
            self.driver.type_text(action.text_input)
        elif action.action_type == "SWIPE" and action.swipe_direction:
            self.driver.swipe(action.swipe_direction)
        elif action.action_type == "BACK":
            self.driver.press_back()
        elif action.action_type == "SLEEP":
            time.sleep(2.0)

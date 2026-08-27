"""
Scenario Definitions and Validation Schema.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class StepAction(BaseModel):
    action: str = Field(..., description="launch_app | tap | type | swipe | sleep | set_appearance")
    target: Optional[str] = Field(None, description="Semantic description of target")
    coordinates: Optional[List[int]] = Field(None, description="[x, y] normalized (0-1000)")
    text: Optional[str] = None
    direction: Optional[str] = None
    mode: Optional[str] = None
    duration: Optional[float] = None

class ScenarioStep(BaseModel):
    name: str
    description: str = ""
    actions: List[StepAction]
    assert_screen: Optional[str] = None

class Scenario(BaseModel):
    name: str
    description: str = ""
    bundle_id: Optional[str] = None
    platform: str = "ios"  # "ios" | "android"
    steps: List[ScenarioStep]

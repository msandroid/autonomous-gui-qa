"""
Visual Oracle Module: Analyzes screenshots for visual, structural, and UX defects.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .vlm import VLMEngine

class DefectItem(BaseModel):
    category: str = Field(..., description="TEXT_TRUNCATION | OVERFLOW | LAYOUT_CORRUPTION | VISIBILITY_CONTRAST | CONTEXT_CONTRADICTION | PLACEHOLDER_LEAK")
    severity: str = Field(..., description="CRITICAL | HIGH | MEDIUM | LOW")
    element_description: str = Field(..., description="Target UI element name or description")
    bounding_box: List[int] = Field(..., description="[ymin, xmin, ymax, xmax] in 0-1000 scale")
    detail: str = Field(..., description="Specific description of why this is a defect")
    recommendation: str = Field(..., description="Actionable fix recommendation")

class VisualAuditResult(BaseModel):
    is_passed: bool = Field(..., description="True if no CRITICAL or HIGH defects are found")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")
    summary: str = Field(..., description="Executive summary of the screen state")
    defects: List[DefectItem] = Field(default_factory=list)

SYSTEM_PROMPT_ORACLE = """
You are an expert Mobile UI/UX Quality Assurance Auditor (Visual Oracle).
Examine the attached mobile screenshot with extreme precision and audit for:
1. TEXT_TRUNCATION / OVERFLOW: Text clipped, wrapped awkwardly, or overflowing buttons/containers.
2. LAYOUT_CORRUPTION: Overlapping views, misaligned elements, broken padding/margins, z-index glitches.
3. VISIBILITY_CONTRAST: Text or icons blending into background (especially in Dark Mode or high brightness).
4. CONTEXT_CONTRADICTION: State indicators showing wrong info (e.g. connected status with error icon).
5. PLACEHOLDER_LEAK: Raw dev tokens (e.g. {{user_name}}, LOREM_IPSUM, null, undefined).

Bounding boxes MUST use [ymin, xmin, ymax, xmax] normalized to 0-1000.
"""

class VisualOracle:
    """Visual assertion oracle powered by VLM."""

    def __init__(self, vlm_engine: Optional[VLMEngine] = None):
        self.vlm = vlm_engine or VLMEngine()

    def audit_screen(self, image_path: str, context_prompt: str = "") -> VisualAuditResult:
        """Audits a screenshot and returns structured defect analysis."""
        user_prompt = f"Audit this mobile screenshot for UI/UX defects.\nContext: {context_prompt}"
        data = self.vlm.analyze_image(
            image_path=image_path,
            prompt=user_prompt,
            system_instruction=SYSTEM_PROMPT_ORACLE,
            response_schema=VisualAuditResult
        )
        return VisualAuditResult(**data)

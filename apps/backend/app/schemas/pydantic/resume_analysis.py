from typing import List, Optional
from pydantic import BaseModel, Field


class ImprovementSuggestion(BaseModel):
    """Individual improvement suggestion"""
    suggestion: str = Field(..., description="Specific actionable improvement")
    lineNumber: Optional[str] = Field(None, description="Optional reference to line number or section", alias="lineNumber")
    
    class Config:
        populate_by_name = True


class ResumeAnalysisModel(BaseModel):
    """Resume analysis report model"""
    details: str = Field(..., description="Brief summary of match quality (1-2 sentences)")
    commentary: str = Field(..., description="Professional feedback on strengths and improvements (2-3 sentences)")
    improvements: List[ImprovementSuggestion] = Field(default_factory=list, description="List of specific actionable improvements")
    
    class Config:
        populate_by_name = True


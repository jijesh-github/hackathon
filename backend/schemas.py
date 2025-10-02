"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# Amendment schemas
class AmendmentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Amendment title")
    description: str = Field(..., min_length=1, description="Amendment description")


class AmendmentCreate(AmendmentBase):
    pass


class Amendment(AmendmentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AmendmentWithFeedbacks(Amendment):
    feedbacks: List['Feedback'] = []


# Feedback schemas
class FeedbackBase(BaseModel):
    amendment_id: int = Field(..., gt=0, description="Amendment ID to link feedback to")
    original_text: str = Field(..., min_length=1, max_length=5000, description="Feedback text")


class FeedbackCreate(FeedbackBase):
    pass


class Feedback(FeedbackBase):
    id: int
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_confidence: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackWithAmendment(Feedback):
    amendment: Amendment


# Response schemas
class APIResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[dict] = None


class AmendmentListResponse(BaseModel):
    success: bool = True
    message: str = "Amendments retrieved successfully"
    amendments: List[Amendment]


class FeedbackListResponse(BaseModel):
    success: bool = True
    message: str = "Feedback retrieved successfully"  
    feedback: List[Feedback]


class AnalysisResult(BaseModel):
    """Schema for ML analysis results"""
    original_text: str
    summary: str
    sentiment: str
    sentiment_confidence: float
    word_cloud_base64: Optional[str] = None
"""
Pydantic schemas for API requests and responses.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class PatientBase(BaseModel):
    """Base patient fields."""
    name: str = Field(..., description="Patient name")
    age: Optional[int] = Field(default=None, description="Patient age")
    notes: Optional[str] = Field(default=None, description="Patient notes")


class PatientCreate(PatientBase):
    """Schema for creating or updating a patient."""
    id: Optional[int] = Field(default=None, description="Optional patient id for upsert")


class PatientOut(PatientBase):
    """Schema for patient response."""
    id: int = Field(..., description="Patient ID")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Update time")

    class Config:
        from_attributes = True


class ChatMessageOut(BaseModel):
    """Schema representing a chat message output."""
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatThreadOut(BaseModel):
    """Schema representing a chat thread with messages."""
    id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SendChatRequest(BaseModel):
    """Payload to send a chat message."""
    patientId: int = Field(..., description="ID of the patient")
    message: str = Field(..., description="User input message")


class SendChatResponse(BaseModel):
    """Response after sending a chat message including both agents."""
    threadId: int
    user: ChatMessageOut
    agent1: ChatMessageOut
    agent2: ChatMessageOut

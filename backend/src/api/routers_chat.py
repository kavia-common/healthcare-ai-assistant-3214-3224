"""
Chat endpoints for sending messages and receiving dual-agent responses.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .db import get_db_session
from . import models
from .schemas import SendChatRequest, SendChatResponse, ChatMessageOut
from .openai_client import get_dual_agent_responses

router = APIRouter(prefix="/chat", tags=["Chat"])


def _ensure_thread_for_patient(db: Session, patient_id: int) -> models.ChatThread:
    """Get an existing latest thread or create a new one if none exists."""
    thread = (
        db.query(models.ChatThread)
        .filter(models.ChatThread.patient_id == patient_id)
        .order_by(models.ChatThread.updated_at.desc())
        .first()
    )
    if not thread:
        thread = models.ChatThread(patient_id=patient_id)
        db.add(thread)
        db.flush()
    return thread


# PUBLIC_INTERFACE
@router.post("/send", response_model=SendChatResponse, summary="Send chat message", description="Send a user message and receive responses from Agent 1 and Agent 2.")
async def send_chat(payload: SendChatRequest, db: Session = Depends(get_db_session)):
    """Store user message, get AI responses from two agents, store them and return all."""
    patient = db.query(models.Patient).filter(models.Patient.id == payload.patientId).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Ensure a thread exists
    thread = _ensure_thread_for_patient(db, patient.id)

    # Store user message
    user_msg = models.ChatMessage(thread_id=thread.id, role="user", content=payload.message)
    db.add(user_msg)
    db.flush()
    db.refresh(user_msg)

    # Get AI responses
    agent1_text, agent2_text = await get_dual_agent_responses(payload.message)

    # Store agent messages
    agent1_msg = models.ChatMessage(thread_id=thread.id, role="agent1", content=agent1_text)
    agent2_msg = models.ChatMessage(thread_id=thread.id, role="agent2", content=agent2_text)
    db.add(agent1_msg)
    db.add(agent2_msg)
    db.flush()
    db.refresh(agent1_msg)
    db.refresh(agent2_msg)

    # Return structured response
    return SendChatResponse(
        threadId=thread.id,
        user=ChatMessageOut.model_validate(user_msg),
        agent1=ChatMessageOut.model_validate(agent1_msg),
        agent2=ChatMessageOut.model_validate(agent2_msg),
    )

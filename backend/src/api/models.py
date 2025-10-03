"""
SQLAlchemy ORM models for Patients, ChatThreads, and ChatMessages.
"""

from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .db import Base


class TimestampMixin:
    """Common created_at and updated_at timestamp columns."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Patient(Base, TimestampMixin):
    """Patient entity storing basic info and notes."""
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship to chat threads
    threads: Mapped[List["ChatThread"]] = relationship(
        "ChatThread",
        back_populates="patient",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="desc(ChatThread.updated_at)",
    )


class ChatThread(Base, TimestampMixin):
    """A chat thread that groups messages for a patient."""
    __tablename__ = "chat_threads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    patient: Mapped[Patient] = relationship("Patient", back_populates="threads")
    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="thread",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base, TimestampMixin):
    """Individual chat message within a thread."""
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    thread_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chat_threads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # "user", "agent1", "agent2"
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationship
    thread: Mapped[ChatThread] = relationship("ChatThread", back_populates="messages")

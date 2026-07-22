"""Core data models - shared across all modules."""

import uuid
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


class CallStatus(str, Enum):
    INITIATING = "initiating"
    RINGING = "ringing"
    CONNECTED = "connected"
    SPEAKING = "speaking"
    LISTENING = "listening"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TopicStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class ConversationMessage:
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    language: str = "en"


@dataclass
class TopicState:
    topic_id: str
    topic_name: str
    status: TopicStatus = TopicStatus.ACTIVE
    key_points: list[str] = field(default_factory=list)
    paused_at: Optional[datetime] = None


@dataclass
class ConversationContext:
    conversation_id: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    business_context: str = ""
    current_goal: str = ""
    current_language: str = "en"
    messages: list[ConversationMessage] = field(default_factory=list)
    topic_stack: list[TopicState] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def active_topic(self) -> Optional[TopicState]:
        for t in reversed(self.topic_stack):
            if t.status == TopicStatus.ACTIVE:
                return t
        return None

    @property
    def paused_topics(self) -> list[TopicState]:
        return [t for t in self.topic_stack if t.status == TopicStatus.PAUSED]

    def add_message(self, role: MessageRole, content: str, language: str = "en"):
        self.messages.append(ConversationMessage(role=role, content=content, language=language))

    def get_recent_messages(self, count: int = 20) -> list[dict]:
        return [{"role": m.role.value, "content": m.content} for m in self.messages[-count:]]


@dataclass
class VoiceCallState:
    call_id: str
    conversation: ConversationContext
    status: CallStatus = CallStatus.INITIATING
    phone_number: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    audio_buffer: bytes = b""
    is_interrupted: bool = False

"""Memory Service - Topic stack, context tracking, never loses context."""

import uuid
from typing import Optional
from datetime import datetime
from ..core.models import ConversationContext, TopicState, TopicStatus, MessageRole


class MemoryService:
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self._conversations: dict[str, ConversationContext] = {}

    def create_conversation(self, **kwargs) -> ConversationContext:
        cid = f"conv_{uuid.uuid4().hex[:12]}"
        ctx = ConversationContext(conversation_id=cid, **kwargs)
        self._conversations[cid] = ctx
        return ctx

    def get_conversation(self, cid: str) -> Optional[ConversationContext]:
        return self._conversations.get(cid)

    def add_message(self, cid: str, role: MessageRole, content: str, language: str = "en"):
        ctx = self._conversations.get(cid)
        if ctx:
            ctx.add_message(role, content, language)
            if language != ctx.current_language:
                ctx.current_language = language

    def get_llm_messages(self, cid: str) -> list[dict]:
        ctx = self._conversations.get(cid)
        return ctx.get_recent_messages(self.window_size) if ctx else []

    def get_context_summary(self, cid: str) -> str:
        ctx = self._conversations.get(cid)
        if not ctx:
            return ""
        parts = []
        if ctx.customer_name:
            parts.append(f"Customer: {ctx.customer_name}")
        if ctx.current_goal:
            parts.append(f"Goal: {ctx.current_goal}")
        active = ctx.active_topic
        if active:
            parts.append(f"Current Topic: {active.topic_name}")
        paused = ctx.paused_topics
        if paused:
            parts.append(f"Paused Topics: {', '.join(t.topic_name for t in paused)}")
        parts.append(f"Language: {ctx.current_language}")
        return "\n".join(parts)

    def push_topic(self, cid: str, topic_name: str):
        ctx = self._conversations.get(cid)
        if not ctx:
            return
        active = ctx.active_topic
        if active:
            active.status = TopicStatus.PAUSED
            active.paused_at = datetime.utcnow()
        ctx.topic_stack.append(TopicState(
            topic_id=f"t_{uuid.uuid4().hex[:8]}",
            topic_name=topic_name,
        ))

    def resume_topic(self, cid: str, name: str):
        ctx = self._conversations.get(cid)
        if not ctx:
            return
        active = ctx.active_topic
        if active:
            active.status = TopicStatus.PAUSED
        for t in ctx.topic_stack:
            if t.topic_name.lower() == name.lower() and t.status == TopicStatus.PAUSED:
                t.status = TopicStatus.ACTIVE
                t.paused_at = None
                break

    def detect_topic_switch(self, cid: str, msg: str) -> Optional[str]:
        ctx = self._conversations.get(cid)
        if not ctx:
            return None
        msg_lower = msg.lower()
        signals = ["continue about", "back to", "return to", "regarding", "about the"]
        for t in ctx.topic_stack:
            if t.status != TopicStatus.PAUSED:
                continue
            if t.topic_name.lower() in msg_lower:
                return t.topic_name
            for s in signals:
                if s in msg_lower and any(w in msg_lower for w in t.topic_name.lower().split()):
                    return t.topic_name
        return None

    def end_conversation(self, cid: str):
        return self._conversations.pop(cid, None)

    def get_active_conversations(self) -> list[str]:
        return list(self._conversations.keys())

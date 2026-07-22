"""Workflow Engine - Configurable conversation flows."""

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class WorkflowState:
    current_node: str = "greet"
    turns: int = 0
    collected: dict = field(default_factory=dict)
    done: bool = False


class WorkflowService:
    def __init__(self):
        self._states: dict[str, WorkflowState] = {}
        self._graphs: dict[str, dict] = {}

    def start(self, cid: str, workflow_id: str = "default"):
        self._states[cid] = WorkflowState()

    def get_instructions(self, cid: str) -> str:
        state = self._states.get(cid)
        if not state or state.done:
            return ""
        nodes = {
            "greet": "STEP: Greeting. Say hello, confirm who you're speaking to. Keep brief.",
            "qualify": "STEP: Qualification. Understand their needs. Ask what they're looking for.",
            "pitch": "STEP: Present solution. Based on their needs, explain how you can help. Brief.",
            "faq": "STEP: Answer questions from company knowledge.",
            "book": "STEP: Book appointment. Ask what day/time works for them.",
            "end": "STEP: End call gracefully. Thank them.",
        }
        return nodes.get(state.current_node, "")

    def process_turn(self, cid: str, user_msg: str, ai_msg: str):
        state = self._states.get(cid)
        if not state:
            return
        state.turns += 1
        msg = user_msg.lower()

        if state.current_node == "greet" and state.turns >= 2:
            state.current_node = "qualify"
        elif state.current_node == "qualify" and state.turns >= 5:
            state.current_node = "pitch"
        elif "appointment" in msg or "schedule" in msg or "book" in msg or "demo" in msg:
            state.current_node = "book"
        elif "bye" in msg or "thank" in msg:
            state.current_node = "end"
            state.done = True

    def end(self, cid: str) -> Optional[dict]:
        state = self._states.pop(cid, None)
        return {"collected": state.collected} if state else None

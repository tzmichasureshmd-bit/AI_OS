"""Conversation Engine - The brain. Orchestrates everything."""

from typing import AsyncGenerator, Optional
from ..core.interfaces import LLMProvider
from ..core.models import MessageRole
from .memory import MemoryService
from .language import LanguageService
from .knowledge import KnowledgeService
from .workflow import WorkflowService
from .voice_enhancer import VoiceEnhancer

SYSTEM = """You are {name}, a {role} at {company}.
{personality}
- Talk like a REAL human on a phone call
- MAX 2-3 sentences per response
- Use natural fillers occasionally
- Never sound robotic
- If interrupted, address it immediately
- Remember everything discussed
{lang}
{workflow}
CONTEXT:
{context}
{knowledge}"""


class ConversationService:
    def __init__(self, llm: LLMProvider, memory: MemoryService, language: LanguageService,
                 knowledge: KnowledgeService = None, workflow: WorkflowService = None,
                 enhancer: VoiceEnhancer = None, name: str = "Alex", role: str = "AI Assistant",
                 company: str = "", personality: str = "friendly, professional"):
        self.llm = llm
        self.memory = memory
        self.language = language
        self.knowledge = knowledge
        self.workflow = workflow
        self.enhancer = enhancer or VoiceEnhancer()
        self.name = name
        self.role = role
        self.company = company
        self.personality = personality
        self._interrupts: dict[str, bool] = {}
        self._kb_collection: Optional[str] = None

    def set_knowledge_base(self, collection: str):
        self._kb_collection = collection

    async def process_message(self, cid: str, user_msg: str) -> str:
        ctx = self.memory.get_conversation(cid)
        if not ctx:
            return "Sorry, no conversation context."

        lang = await self.language.detect(user_msg)
        self.memory.add_message(cid, MessageRole.USER, user_msg, lang)

        is_return = False
        resume = self.memory.detect_topic_switch(cid, user_msg)
        if resume:
            self.memory.resume_topic(cid, resume)
            is_return = True

        knowledge = ""
        if self.knowledge and self._kb_collection:
            knowledge = await self.knowledge.get_context(self._kb_collection, user_msg)

        workflow_inst = self.workflow.get_instructions(cid) if self.workflow else ""

        prompt = SYSTEM.format(
            name=self.name, role=self.role, company=self.company,
            personality=self.personality,
            lang=self.language.get_language_instruction(),
            workflow=workflow_inst,
            context=self.memory.get_context_summary(cid),
            knowledge=knowledge,
        )

        messages = self.memory.get_llm_messages(cid)
        response = await self.llm.generate(messages=messages, system_prompt=prompt, max_tokens=120)

        response = self.enhancer.enhance(response, is_return=is_return, is_interrupt=self._interrupts.get(cid, False))
        self._interrupts[cid] = False

        self.memory.add_message(cid, MessageRole.ASSISTANT, response, lang)
        if self.workflow:
            self.workflow.process_turn(cid, user_msg, response)
        return response

    async def process_message_stream(self, cid: str, user_msg: str) -> AsyncGenerator[str, None]:
        ctx = self.memory.get_conversation(cid)
        if not ctx:
            yield "Sorry, no context."
            return
        self._interrupts[cid] = False
        lang = await self.language.detect(user_msg)
        self.memory.add_message(cid, MessageRole.USER, user_msg, lang)

        knowledge = ""
        if self.knowledge and self._kb_collection:
            knowledge = await self.knowledge.get_context(self._kb_collection, user_msg)

        prompt = SYSTEM.format(
            name=self.name, role=self.role, company=self.company,
            personality=self.personality,
            lang=self.language.get_language_instruction(),
            workflow=self.workflow.get_instructions(cid) if self.workflow else "",
            context=self.memory.get_context_summary(cid),
            knowledge=knowledge,
        )

        full = ""
        async for chunk in self.llm.generate_stream(messages=self.memory.get_llm_messages(cid), system_prompt=prompt, max_tokens=120):
            if self._interrupts.get(cid):
                break
            full += chunk
            yield chunk

        self.memory.add_message(cid, MessageRole.ASSISTANT, full, lang)

    def interrupt(self, cid: str):
        self._interrupts[cid] = True

    async def start_conversation(self, customer_name=None, customer_phone=None,
                                  business_context="", goal="", language="en") -> tuple[str, str]:
        ctx = self.memory.create_conversation(
            customer_name=customer_name, customer_phone=customer_phone,
            business_context=business_context, current_goal=goal, current_language=language,
        )
        if goal:
            self.memory.push_topic(ctx.conversation_id, goal)
        if self.workflow:
            self.workflow.start(ctx.conversation_id)

        opening = f"Hello! This is {self.name} from {self.company}. How can I help you today?"
        self.memory.add_message(ctx.conversation_id, MessageRole.ASSISTANT, opening, language)
        return ctx.conversation_id, opening

    async def end_conversation(self, cid: str) -> dict:
        ctx = self.memory.get_conversation(cid)
        if not ctx:
            return {"error": "Not found"}
        wf = self.workflow.end(cid) if self.workflow else None
        self.memory.end_conversation(cid)
        return {"conversation_id": cid, "messages": len(ctx.messages), "topics": [t.topic_name for t in ctx.topic_stack], "workflow": wf}

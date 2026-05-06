"""LangChain logic for the Pathwise AI Career Coach (ADA module 7 final assignment).

Three ChatPromptTemplates + three LCEL chains with structured (Pydantic) outputs,
plus a ConversationBufferMemory helper.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from langchain_classic.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

DEFAULT_MODEL = "gpt-4o-mini"


def build_llm(model: str = DEFAULT_MODEL, temperature: float = 0.7) -> ChatOpenAI:
    return ChatOpenAI(model=model, temperature=temperature)


# --- Pydantic schemas (structured chain outputs) -----------------------------


class ResumeBullets(BaseModel):
    """Five ATS-aware resume bullets, action-led, quantified where plausible."""

    bullets: List[str] = Field(min_length=5, max_length=5)


class InterviewQuestion(BaseModel):
    q: str = Field(description="The question.")
    hint: str = Field(description="One short hint of what a strong answer covers.")
    tags: List[str] = Field(
        description="1-2 short labels like 'Behavioral', 'Technical', 'Strategy'.",
        min_length=1,
        max_length=3,
    )


class Interview(BaseModel):
    questions: List[InterviewQuestion] = Field(min_length=5, max_length=5)


class Course(BaseModel):
    name: str
    weeks: str = Field(description="Duration, e.g. '8 wks' or 'ongoing'.")
    price: Optional[str] = Field(default=None, description="Price label, optional.")
    priority: str = Field(description="Single-word category like 'Anchor' or 'Skill gap'.")


class NetworkAction(BaseModel):
    name: str
    cadence: str = Field(description="e.g. '2/wk', '1 event', '1/wk → 1/mo'.")
    priority: str


class PortfolioProject(BaseModel):
    name: str
    cadence: str = Field(description="When to ship, e.g. 'M1–M2'.")
    priority: str


class Milestone(BaseModel):
    m: str = Field(description="M1..M6")
    title: str = Field(description="Short noun phrase, 1-2 words.")
    text: str = Field(description="One sentence describing the milestone.")


class Roadmap(BaseModel):
    courses: List[Course] = Field(min_length=3, max_length=3)
    networking: List[NetworkAction] = Field(min_length=3, max_length=3)
    projects: List[PortfolioProject] = Field(min_length=3, max_length=3)
    milestones: List[Milestone] = Field(min_length=6, max_length=6)


# --- Prompts ----------------------------------------------------------------


RESUME_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a career coach for {audience}. Tone: {tone}. "
            "Be concrete, ATS-aware, and avoid generic filler.",
        ),
        (
            "human",
            "Generate 5 resume bullet points for someone targeting the role of "
            "{job_title}. Their key skills are: {skills}. "
            "Each bullet must start with an action verb and include a quantified "
            "impact where plausible (use realistic placeholders if unknown).",
        ),
    ]
)

INTERVIEW_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior interviewer hiring for {audience}. Tone: {tone}. "
            "Tailor questions tightly to the candidate and the job description.\n\n"
            "Use the conversation history below as context. Reference earlier outputs "
            "where relevant.\n\n"
            "Conversation history:\n{history}",
        ),
        (
            "human",
            "Resume bullets:\n{resume_bullets}\n\n"
            "Job description:\n{job_description}\n\n"
            "Produce 5 interview questions: mix behavioural and technical/role-specific. "
            "Each question must include a one-sentence answer hint and 1-2 short tags "
            "(e.g. Behavioral, Technical, Strategy, Metrics, Influence).",
        ),
    ]
)

ROADMAP_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a long-term career strategist for {audience}. Tone: {tone}. "
            "Be specific: name real courses, communities, and project ideas.\n\n"
            "Use the conversation history below as context. Reference earlier outputs "
            "where relevant.\n\n"
            "Conversation history:\n{history}",
        ),
        (
            "human",
            "Earlier coaching outputs:\n\n"
            "RESUME BULLETS:\n{resume_bullets}\n\n"
            "INTERVIEW PREP:\n{interview_prep}\n\n"
            "Career goal: {career_goal}\n"
            "Current skills: {skills}\n\n"
            "Produce a 6-month growth roadmap with three lanes (3 items each) and "
            "six monthly milestones (M1..M6). Lighter on M1 by design — momentum first.",
        ),
    ]
)


# --- Chain assembly ---------------------------------------------------------


@dataclass
class CareerCoachChains:
    resume: Runnable
    interview: Runnable
    roadmap: Runnable


def _format_history(messages) -> str:
    """Render BaseMessage list (or string) as a flat text log for prompt injection."""
    if not messages:
        return "(no prior turns yet)"
    if isinstance(messages, str):
        return messages or "(no prior turns yet)"
    parts = []
    for m in messages:
        role = "User" if getattr(m, "type", "") == "human" else "Coach"
        parts.append(f"{role}: {m.content}")
    return "\n".join(parts) if parts else "(no prior turns yet)"


def build_chains(
    memory: ConversationBufferMemory | None = None,
    llm: ChatOpenAI | None = None,
) -> CareerCoachChains:
    llm = llm or build_llm()

    def _history_loader(_):
        if memory is None:
            return "(no prior turns yet)"
        return _format_history(memory.load_memory_variables({}).get("history", ""))

    inject_history = RunnablePassthrough.assign(history=_history_loader)

    return CareerCoachChains(
        resume=RESUME_PROMPT | llm.with_structured_output(ResumeBullets),
        interview=inject_history | INTERVIEW_PROMPT | llm.with_structured_output(Interview),
        roadmap=inject_history | ROADMAP_PROMPT | llm.with_structured_output(Roadmap),
    )


# --- Memory -----------------------------------------------------------------


def new_memory() -> ConversationBufferMemory:
    return ConversationBufferMemory(return_messages=True)


def remember(memory: ConversationBufferMemory, human: str, ai: str) -> None:
    memory.save_context({"input": human}, {"output": ai})

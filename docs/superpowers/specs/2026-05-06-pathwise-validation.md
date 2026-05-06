# Pathwise — Validation report

**Date:** 2026-05-06
**Project:** ADA AI Professional · Module 7 · Final assignment
**Repo:** `~/ClubVentureProjects/Langchain_Playground`
**Author:** Vincent Blokker

This report maps every ADA assignment requirement to the actual implementation,
with file:line references that an evaluator (or you) can spot-check in minutes.

---

## 1. Quick verification

### Boot test (already passed locally)

```bash
.venv/bin/streamlit run app.py
# → http://localhost:8501  · HTTP 200  · no Python errors
```

Or via Docker:

```bash
docker compose up --build
# → http://localhost:8501
```

### Files delivered

| File | Lines | Purpose |
|---|---:|---|
| `app.py` | 623 | Streamlit driver — wizard state, chain calls, screen routing |
| `chains.py` | 165 | 3 PromptTemplates · 3 LCEL chains · Pydantic schemas · memory |
| `ui.py` | 326 | Brand HTML/SVG helpers (lockup, glyph, stepper, coach, milestone path) |
| `static/brand.css` | 757 | Brand tokens + Streamlit overrides |
| `requirements.txt` | 9 | Pinned deps |
| `Dockerfile` + `docker-compose.yml` | — | Containerised run on port 8501 |
| `README.md` | 96 | Setup, file map, reflection (300-500 words) |
| `docs/superpowers/specs/2026-05-06-pathwise-design.md` | — | Locked design spec + Claude Design prompts |
| `.design-handoff/` | — | Original Claude Design output (HTML/CSS/JSX) |

---

## 2. ADA requirement → implementation matrix

> Source of truth: `wiki/concepts/Eindopdracht ADA.md` and `raw/ada-langchain-assignment.md`.

| # | Requirement | Status | Evidence |
|---|---|---|---|
| **R1** | Define a target audience | ✅ | `app.py::PERSONAS` (5 options); selectable in welcome form `app.py:188-191`; default persona "Career Switcher · Marketing → Tech" in `DEFAULT_PROFILE` |
| **R2** | Use 3+ `PromptTemplate` / `ChatPromptTemplate` | ✅ | `chains.py:82` (RESUME), `chains.py:99` (INTERVIEW), `chains.py:117` (ROADMAP) — all `ChatPromptTemplate.from_messages([...])` with system + human |
| **R3** | Multi-step LCEL chain (3+ steps) | ✅ | `chains.py:148-154` — `prompt \| llm.with_structured_output(Schema)` for each step. Sequential composition lives in `app.py` (resume → interview → roadmap), with each step receiving prior outputs |
| **R4** | Use `ConversationBufferMemory` | ✅ | `chains.py:11` import (via `langchain-classic`), `chains.py:160-161` factory, `chains.py:164-165` `remember()` helper |
| **R5** | Memory: store earlier responses, reference them later, reset option | ✅ | Stored: `app.py:240,346,427` (`remember(...)`). Referenced: step 2/3 prompts include earlier outputs (`app.py:333-336, 411-417`). Reset: top shell New-session button `ui.py:131-134` and recap "Start a new session" `app.py:478-484` |
| **R6** | Streamlit UI with input forms | ✅ | Welcome form `app.py:175-205`, JD textarea `app.py:294-298`, persona/tone/skills fields all native Streamlit widgets |
| **R7** | Step-by-step output display | ✅ | Five-screen wizard with router `app.py:608-617`, stepper visible on every screen `ui.py::stepper`, navigation buttons (`Back`, `Continue to ...`) on every screen |
| **R8** | Chat history panel (memory tonen) | ✅ | Collapsible "💬 Memory log" expander on the recap screen `app.py:487-495`, iterates over `st.session_state.memory.chat_memory.messages` |
| **R9** | "New Session" reset | ✅ | Two affordances: top-shell button `ui.py:127-134` (every screen) and recap button `app.py:478-484` |
| **R10** | Deliverables: `app.py`, `chains.py`, `requirements.txt` | ✅ | All present at project root; bonus split into `ui.py` for clarity |
| **R11** | Reflection 300-500 words (design + scaling) | ✅ | `README.md` "Reflection" section, two subsections "Design approach & trade-offs" and "Scaling the app" |

---

## 3. LangChain technical evidence

### 3.1 Three ChatPromptTemplates

```python
# chains.py:82
RESUME_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a career coach for {audience}. Tone: {tone}. ..."),
    ("human",  "Generate 5 resume bullet points for someone targeting {job_title}. ..."),
])
# chains.py:99
INTERVIEW_PROMPT = ChatPromptTemplate.from_messages([...])
# chains.py:117
ROADMAP_PROMPT = ChatPromptTemplate.from_messages([...])
```

### 3.2 LCEL composition with structured outputs

```python
# chains.py:148
def build_chains(llm=None):
    llm = llm or build_llm()
    return CareerCoachChains(
        resume=    RESUME_PROMPT    | llm.with_structured_output(ResumeBullets),
        interview= INTERVIEW_PROMPT | llm.with_structured_output(Interview),
        roadmap=   ROADMAP_PROMPT   | llm.with_structured_output(Roadmap),
    )
```

> The `|` operator is LCEL. `with_structured_output()` is the modern replacement for output parsers — the chains return typed Pydantic objects, so the UI never parses markdown.

### 3.3 Pydantic schemas (typed chain outputs)

```python
# chains.py:27-79
class ResumeBullets(BaseModel):       # 5 strings
class InterviewQuestion(BaseModel):   # q + hint + tags
class Interview(BaseModel):           # 5 questions
class Course / NetworkAction / PortfolioProject / Milestone   # roadmap pieces
class Roadmap(BaseModel):             # 3 + 3 + 3 + 6
```

### 3.4 ConversationBufferMemory

```python
# chains.py:160
def new_memory() -> ConversationBufferMemory:
    return ConversationBufferMemory(return_messages=True)

# chains.py:164
def remember(memory, human, ai):
    memory.save_context({"input": human}, {"output": ai})
```

> `langchain-classic` preserves this class on LangChain 1.x; warning is expected.

### 3.5 Multi-step composition (lives in app.py)

| Step | Inputs | Output written to | Memory call |
|---|---|---|---|
| 1 (resume) | persona, tone, target role, skills | `outputs["resume"]` | `app.py:238` |
| 2 (interview) | persona, tone, **prior resume bullets**, JD | `outputs["interview"]` | `app.py:344` |
| 3 (roadmap) | persona, tone, goal, skills, **prior bullets**, **prior interview** | `outputs["roadmap"]` | `app.py:425` |

Each step receives every relevant earlier output — that is the "multi-step memory-aware" coupling the assignment asks for.

---

## 4. UI / wizard structure

### 4.1 Five screens, one router

```python
# app.py:608
SCREENS = {
    0: screen_welcome,
    1: screen_resume,
    2: screen_interview,
    3: screen_roadmap,
    4: screen_recap,
}
SCREENS[st.session_state.step]()
```

### 4.2 State

```python
# app.py:92-104
defaults = {
    "step": 0,
    "memory": new_memory(),
    "outputs": {},
    "profile": dict(DEFAULT_PROFILE),
    "expanded_qs": set(),
    "practiced_qs": set(),
    "job_description": SAMPLE_JD,
}
```

### 4.3 Persistent shell on every screen

`ui.py::top_shell` renders: Pathwise lockup · stepper (Welcome → Resume → Interview → Roadmap → Recap) · persona chip · New-session button.

### 4.4 Memory log

```python
# app.py:487-495 — inside the recap aside
with st.expander("💬 Memory log", expanded=False):
    messages = st.session_state.memory.chat_memory.messages
    for m in messages:
        role = "🧑 You" if m.type == "human" else "🤖 Coach"
        st.markdown(f"**{role}**"); st.markdown(m.content)
```

---

## 5. Brand & design fidelity

The visual system was designed in **Claude Design** (handoff in `.design-handoff/pathwise/`) and re-implemented with custom CSS in `static/brand.css`.

| Brand token | CSS var | Source |
|---|---|---|
| Sage green | `--pw-sage: #6F8F73` | spec §2.1 |
| Cream | `--pw-cream: #F7F3EC` | spec §2.1 |
| Ink | `--pw-ink: #1F2A24` | spec §2.1 |
| Amber | `--pw-amber: #E0A24B` | spec §2.1 |
| Display font | Manrope 600/700 | spec §2.2 |
| Body font | Inter 400/500 | spec §2.2 |
| Mono font | JetBrains Mono | for nums (Q01, M1) |

Logo: `ui.py::path_glyph` (3 sage pills + amber summit dot), `ui.py::lockup` (wordmark), `ui.py::monogram` (rounded-square app icon).

---

## 6. Bonus / extras

The assignment lists optional bonuses; we shipped some structural support:

| Bonus | Status | Notes |
|---|---|---|
| Multi-LLM keuze | ⚪ Not shipped | `build_llm()` is parametric on model — easy switch |
| PDF/Word resume upload | ⚪ Not shipped | Listed in README "future work" |
| Voice input | ⚪ Not shipped | Listed in README "future work" |
| HF Spaces / Streamlit Cloud deploy | ⚪ Not deployed | App is deploy-ready |
| **Polished branded UI** (beyond spec) | ✅ Extra | Pathwise brand system, custom logo, 5-screen wizard, hover states, milestone path SVG |

---

## 7. Known limitations / honest disclosure

1. **Pixel-perfect fidelity is not Streamlit-native.** The original Pathwise design is React/HTML/CSS. We chose a Streamlit + heavy CSS approach (~80% visual fidelity, 100% structural fidelity). Discussed and approved in chat 2026-05-06.
2. **`ConversationBufferMemory` deprecation warning.** LangChain 1.x deprecated this class. We pulled it back via `langchain-classic` because the assignment names it explicitly; warning is expected.
3. **PDF export on the recap is a stub** — clicks show a toast. Real export would need `weasyprint` or similar.
4. **No git repo.** This folder is not git-initialised. If you want to inleveren via git/GitHub, run `git init` and a first commit before pushing.

---

## 8. Validation checklist (for the evaluator / yourself)

- [ ] Run `streamlit run app.py` and reach the Welcome screen
- [ ] Submit the welcome form → Step 1 generates 5 bullets
- [ ] Continue to Step 2 → 5 questions with tags + expand-hint
- [ ] Toggle 1+ "Mark as practiced"
- [ ] Continue to Step 3 → roadmap shows 3 lanes (3 items each) + 6-month path
- [ ] Continue to Recap → all artefacts visible, sticky TOC works, memory log expander shows turns
- [ ] Click "↻ New session" in the top shell → state resets, returns to Welcome
- [ ] Confirm `app.py`, `chains.py`, `requirements.txt`, `README.md` exist at project root
- [ ] Confirm `README.md` has a Reflection section between 300-500 words

---

## 9. How an evaluator can run a code-only audit

```bash
# Verify all requirements file lines are present
grep -n ChatPromptTemplate chains.py            # → 3 hits
grep -n with_structured_output chains.py        # → 3 hits
grep -n ConversationBufferMemory chains.py      # → 4 hits
grep -n "def screen_" app.py                    # → 5 screens
grep -nc "remember(" app.py                     # → 3+ memory writes
```

Expected:
- `chains.py` exposes `ResumeBullets`, `Interview`, `Roadmap` (Pydantic models) and a `build_chains()` returning a `CareerCoachChains` dataclass.
- `app.py` defines `screen_welcome`, `screen_resume`, `screen_interview`, `screen_roadmap`, `screen_recap` and routes via `st.session_state.step`.

---

*Generated 2026-05-06.*

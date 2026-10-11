# Agentic AI SDLC — AI Career Mentor & Skill-Gap Agent

> **Project:** AI Career Mentor and Skill-Gap Agentic Application  
> **Stack:** Python · Streamlit · Groq API (Qwen3 32B)  
> **Document Type:** Software Development Life Cycle (SDLC) — All 9 Phases

---

## Phase 1 · Problem Definition

### 1.1 Background
The modern job market evolves faster than traditional education can keep pace with. Professionals at every level face a persistent challenge: they know the role they want but lack a clear, personalised map from where they are today to where they need to be. Generic advice online is overwhelming, outdated, or too abstract to act on.

### 1.2 Problem Statement
> **How can we give every professional access to an expert career mentor that understands their unique background, identifies their skill gaps with precision, and builds them a concrete, actionable learning roadmap — on demand and at zero cost?**

### 1.3 Why Agentic AI?
A static form or rule-based system cannot reason about the relationship between skills, roles, and learning trajectories. An agentic AI approach allows the system to:
- **Observe** the user's profile autonomously
- **Reason** about what skills are required vs. possessed
- **Plan** a multi-step learning roadmap adapted to the user's constraints
- **Act** interactively as a coach across multiple conversation turns

### 1.4 Scope
| In Scope | Out of Scope |
|---|---|
| Skill-gap analysis for any knowledge-work role | Guaranteed job placement |
| 30-day week-by-week roadmap generation | Legal or contract advice |
| Interactive career coaching chat | Salary benchmarking |
| Mock interview practice (Q&A loop) | Real-time job search / ATS integration |
| Resume bullet-point review | Persistent user accounts / database |

### 1.5 Success Criteria
1. Agent correctly identifies ≥ 80 % of canonical skills for a target role in blind testing.
2. Roadmap is coherent, week-by-week, and references only free publicly accessible resources.
3. Chat coach responds helpfully and within domain on ≥ 95 % of sampled queries.
4. All guardrails pass: no false employment guarantees appear in output.
5. Application loads and runs in under 3 seconds (excluding LLM call latency).

---

## Phase 2 · Requirements Analysis

### 2.1 Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | User must supply a Groq API key at runtime via a secure masked input field. |
| FR-02 | User profile form must collect: target role, experience level, current skills, weekly hours. |
| FR-03 | Tab 1 must perform full skill-gap analysis and return a structured 30-day roadmap. |
| FR-04 | Roadmap must include: required skills, gap labels (✅/🔶/❌), prioritised gaps, week-by-week plan, and success metrics. |
| FR-05 | Tab 2 must provide a persistent multi-turn chat with full history. |
| FR-06 | Chat must support: mock interview mode, resume bullet review, and general career Q&A. |
| FR-07 | Download button must export the roadmap as a Markdown file. |
| FR-08 | Chat history must be clearable within the session. |

### 2.2 Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | **Security** — API key must never be written to disk, logged, or leaked in any error message. |
| NFR-02 | **Performance** — LLM calls must be capped at max_tokens=1000 to control latency and cost. |
| NFR-03 | **Reliability** — All Groq API errors must be caught and surfaced as friendly user messages. |
| NFR-04 | **Usability** — UI must be navigable by a non-technical user with zero prior setup knowledge. |
| NFR-05 | **Ethics** — No false promises about employment; disclaimer appended to every formal output. |
| NFR-06 | **Maintainability** — Logic separated into `app.py`, `agent/`, and `utils/` layers. |
| NFR-07 | **Portability** — Runs on Windows, macOS, and Linux with a single `pip install`. |

### 2.3 User Stories

- **As a career changer**, I want to see exactly which skills I am missing for my target role so that I can prioritise my learning time.
- **As a working professional with limited time**, I want a week-by-week plan that fits my schedule so that I do not feel overwhelmed.
- **As an interview candidate**, I want to practice role-specific interview questions and receive feedback so that I build confidence before the real thing.
- **As a resume writer**, I want AI feedback on my bullet points so that I can make them more impactful.

### 2.4 Constraints
- LLM is accessed via Groq cloud API — internet connectivity required.
- `max_tokens=1000` per call to manage cost and latency; very detailed plans may be truncated.
- Free-tier Groq accounts have rate limits; the application does not implement retry logic (planned as a future enhancement).

---

## Phase 3 · Agent Design

### 3.1 Agent Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        app.py (UI Layer)                    │
│  Sidebar: API key + profile form                            │
│  Tab 1: Roadmap trigger → run_gap_analysis()                │
│  Tab 2: Chat input → run_chat_turn()                        │
└───────────────────────┬────────────────────────────────────┘
                        │  user_profile dict + messages
                        ▼
┌─────────────────────────────────────────────────────────────┐
│               agent/mentor_agent.py (Agent Layer)           │
│                                                             │
│  build_system_prompt()  ←  guardrails + user context        │
│                                                             │
│  run_gap_analysis()                                         │
│    Observe → Think → Act (ReAct-style single-pass)          │
│    Injects structured prompt with 5 reasoning steps         │
│                                                             │
│  run_chat_turn()                                            │
│    Stateful multi-turn: history passed on every call        │
│    Coach-mode system prompt variant                         │
└───────────────────────┬────────────────────────────────────┘
                        │  messages list
                        ▼
┌─────────────────────────────────────────────────────────────┐
│               utils/groq_client.py (LLM Layer)              │
│  call_llm() — model, max_tokens, temperature, error wrap    │
│  get_client() — fresh Groq client per call (no key storage) │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Agentic Reasoning Pattern — ReAct
The gap-analysis agent follows a simplified **ReAct** (Reason + Act) pattern:

| Step | Agent Behaviour |
|------|----------------|
| **Observe** | Ingests full user profile (role, experience, skills, time) via system prompt |
| **Reason Step 1** | Enumerates all required skills for the target role |
| **Reason Step 2** | Compares required skills against possessed skills; labels each |
| **Reason Step 3** | Ranks and prioritises the top gaps |
| **Act** | Generates a concrete week-by-week roadmap + success metrics |

### 3.3 Chat Agent Pattern
The chat coach uses a **Conversational ReAct** pattern where the full message history is passed on every turn, enabling:
- Context accumulation across turns
- Mode detection (interview / resume / general)
- Coherent follow-up responses

### 3.4 State Management
All state is held in `st.session_state` (Streamlit's in-memory store):
- `chat_history` — list of `{"role", "content"}` dicts
- `roadmap_result` — cached markdown string from last roadmap run
- `profile_ready` — boolean gate preventing premature agent calls

---

## Phase 4 · LLM and Capability Selection

### 4.1 Model Selection Rationale

| Criterion | Evaluation |
|-----------|-----------|
| **Model** | `qwen/qwen3-32b` via Groq API |
| **Reasoning quality** | Qwen3 32B delivers strong instruction-following, structured output, and multi-step reasoning |
| **Inference speed** | Groq's LPU hardware delivers 300–500 tokens/second — low latency for interactive chat |
| **Cost** | Groq free tier is sufficient for development and light production use |
| **Context window** | 128 K tokens — ample for full chat history + system prompt |
| **Instruction following** | Strong compliance with markdown formatting, structured lists, and multi-step reasoning chains |

### 4.2 Alternative Models Considered

| Model | Reason not selected |
|-------|-------------------|
| GPT-4o | Requires OpenAI key; higher cost |
| Claude 3.5 Sonnet | Requires Anthropic key |
| Gemma 2 9B | Smaller; weaker structured output |
| Mixtral 8×7B | Good but superseded by Qwen3 32B on structured reasoning benchmarks |

### 4.3 Token Budget
- `max_tokens=1000` per call
- System prompt: ~400–500 tokens
- User message (roadmap): ~250 tokens
- Remaining for output: ~750–800 tokens
- Chat turns: shorter prompts leave more room for response

### 4.4 Temperature Settings
| Mode | Temperature | Rationale |
|------|-------------|-----------|
| Gap Analysis / Roadmap | 0.6 | More deterministic, structured output |
| Career Coach Chat | 0.75 | Slightly more natural conversational tone |

---

## Phase 5 · Prompt and Guardrail Design

### 5.1 System Prompt Architecture
The system prompt is composed of two layers:
1. **Base prompt** (`build_system_prompt`) — injected in all calls; defines role, user context, and hard guardrails.
2. **Mode addendum** (`build_chat_system_prompt`) — appended for chat mode; defines conciseness and interaction patterns.

### 5.2 Guardrail Implementation (Three-Layer Defence)

```
Layer 1 — LLM Instruction (System Prompt)
   "You ONLY discuss career development..."
   "Never promise or imply guaranteed employment..."
   "Append disclaimer after every formal advice block..."

Layer 2 — Output Post-Processing (Python Code)
   if "Disclaimer" not in result:
       result += DISCLAIMER
   (Applied after every run_gap_analysis() call)

Layer 3 — Contextual Detection (Chat Mode)
   if any(kw in reply.lower() for kw in formal_keywords):
       reply += DISCLAIMER
   (Formal keywords: roadmap, plan, recommend, guidance, strategy, advice)
```

### 5.3 Disclaimer Text
> ⚠️ **Disclaimer:** This AI-generated career guidance is for educational and planning purposes only and does not guarantee job placement or professional hiring outcomes.

### 5.4 Prompt Engineering Patterns Used

| Pattern | Application |
|---------|------------|
| **Role assignment** | "You are CareerMentorAI, an expert AI Career Mentor…" |
| **Context injection** | User profile dynamically embedded in every system prompt |
| **Chain-of-thought scaffolding** | Roadmap prompt breaks reasoning into 5 explicit steps |
| **Output format specification** | Markdown headers, bullet types, and week labels defined in prompt |
| **Few-shot via description** | Chat modes described with expected behaviour patterns |
| **Constraint specification** | Domain restrictions and forbidden topics explicitly listed |

### 5.5 Adversarial Prompt Resilience
The system prompt uses explicit prohibition language ("ONLY discuss", "Refuse any request outside this domain") which raises the bar for successful jailbreaks. Combined with the post-processing disclaimer layer, the system is robust against common prompt-injection attempts within the Streamlit input fields.

---

## Phase 6 · Application Development

### 6.1 Project Structure

```
career_mentor_agent/
├── app.py                  ← Streamlit UI
├── agent/
│   ├── __init__.py
│   └── mentor_agent.py     ← Agent logic, prompts, guardrails
├── utils/
│   ├── __init__.py
│   └── groq_client.py      ← LLM wrapper
├── SDLC.md                 ← This document
├── requirements.txt        ← Dependencies
├── run.bat                 ← Windows launcher
└── README.md               ← Setup guide
```

### 6.2 Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `app.py` | UI layout, user input collection, session state management, rendering |
| `mentor_agent.py` | Prompt construction, reasoning chain design, guardrail enforcement |
| `groq_client.py` | API key handling, LLM call execution, error normalisation |

### 6.3 Key Design Decisions

1. **No custom HTML/CSS** — Pure Streamlit components only for portability and security.
2. **Stateless API key** — Key passed as parameter per call; never stored in any variable outside the function scope.
3. **Cached roadmap in session state** — Prevents unnecessary re-generation on tab switch.
4. **`st.rerun()` after chat** — Forces clean re-render so the new message appears at the correct position.
5. **Download button** — Allows users to save roadmaps for offline reference.

### 6.4 Security Design

- API key field uses `type="password"` — masked in UI, not stored in session state.
- Key is passed at call time to `call_llm()`; scope is limited to the function frame.
- No `.env` file usage in production paths — key lives only in memory.
- Error messages from the Groq SDK are caught and re-formatted to never echo the key.

---

## Phase 7 · Testing and Evaluation

### 7.1 Test Scenarios

| Test ID | Scenario | Expected Outcome |
|---------|----------|-----------------|
| T-01 | Submit form without API key | Sidebar shows error: "Please fill in: Groq API Key" |
| T-02 | Submit form without target role | Error: "Please fill in: Target Job Role" |
| T-03 | Generate roadmap for "Senior Data Scientist" | Output contains all 5 sections: required skills, gap labels, priorities, week-by-week plan, success metrics |
| T-04 | Roadmap output always contains disclaimer | Disclaimer string present in every output |
| T-05 | Chat: ask "What stocks should I buy?" | Agent refuses politely; stays in career domain |
| T-06 | Chat: ask "Start a mock interview" | Agent asks one interview question relevant to target role |
| T-07 | Chat: paste resume bullet for review | Agent rewrites using STAR method with explanation |
| T-08 | Clear chat history | `chat_history` empties; welcome message reappears |
| T-09 | Invalid API key | Friendly error: "⚠️ Error communicating with Groq API: …" |
| T-10 | Tab switch after roadmap generation | Roadmap still displayed (session state preserved) |

### 7.2 Evaluation Criteria for LLM Outputs

| Dimension | Evaluation Method |
|-----------|------------------|
| **Relevance** | Human review: are skills listed appropriate for the target role? |
| **Completeness** | Does the roadmap include all 5 required sections? |
| **Realism** | Are resource URLs real and free? Are time estimates reasonable? |
| **Safety** | Does any output contain employment guarantees? (should be zero) |
| **Formatting** | Is Markdown rendered cleanly in Streamlit? |

### 7.3 Known Limitations and Mitigations

| Limitation | Mitigation |
|-----------|-----------|
| `max_tokens=1000` may truncate detailed roadmaps | Prompt instructs model to be concise; user can ask follow-up questions in chat |
| Groq free-tier rate limits | Friendly error message; user can retry after cooldown |
| LLM may hallucinate resource URLs | Prompt instructs model to use only well-known free platforms |
| No internet access by LLM | Resources are from training data; user should verify links independently |

---

## Phase 8 · Deployment

### 8.1 Local Deployment (Primary)

```bash
# 1. Clone or extract the project
cd career_mentor_agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
streamlit run app.py
```

Windows users can double-click `run.bat` for a one-click launch.

### 8.2 Cloud Deployment Options

#### Streamlit Community Cloud (Free)
1. Push the project to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo.
3. Set `app.py` as the entry point.
4. No secrets file needed — users supply their own API key at runtime.

#### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

```bash
docker build -t career-mentor-ai .
docker run -p 8501:8501 career-mentor-ai
```

#### Railway / Render / Hugging Face Spaces
- These platforms support Streamlit natively.
- No environment variable injection needed (API key is user-supplied at runtime).

### 8.3 Environment Requirements

| Requirement | Version |
|------------|---------|
| Python | ≥ 3.9 |
| streamlit | ≥ 1.32 |
| groq | ≥ 0.9.0 |
| python-dotenv | ≥ 1.0 |

### 8.4 Production Hardening Checklist
- [ ] Add `try/except` retry logic with exponential backoff for rate-limit errors
- [ ] Implement input length validation (max characters per field)
- [ ] Add session timeout to clear API key from memory
- [ ] Enable Streamlit's `--server.headless true` flag for server deployments
- [ ] Set `STREAMLIT_SERVER_MAX_UPLOAD_SIZE` if file upload is added in future

---

## Phase 9 · Documentation

### 9.1 Inline Code Documentation
All three source files contain:
- Module-level docstring explaining purpose, responsibilities, and security notes
- Function-level docstrings with `Parameters`, `Returns`, and design rationale
- Inline comments on non-obvious logic (guardrail layers, ReAct reasoning steps)

### 9.2 User-Facing Documentation
- `README.md` — setup guide, architecture overview, and usage walkthrough
- In-app help text (`help=` parameters on every sidebar widget)
- In-app captions and info boxes guiding first-time users

### 9.3 Architecture Documentation
This SDLC document serves as the primary architecture and design reference. Phase 3 includes an ASCII architecture diagram and Phase 5 documents all prompt engineering patterns.

### 9.4 Ethics and Responsible AI Statement
This application is built with the following responsible AI principles:

| Principle | Implementation |
|-----------|---------------|
| **Transparency** | The application clearly identifies itself as an AI; all outputs carry a disclaimer |
| **Honesty** | The system is explicitly prohibited from making false employment guarantees |
| **User Autonomy** | Users supply their own API key and data; nothing is stored server-side |
| **Privacy** | No user data, API keys, or conversation history is persisted beyond the session |
| **Non-maleficence** | Domain guardrails prevent the system from giving advice outside its competence (legal, financial) |
| **Beneficence** | Designed to empower professionals with actionable, free-resource-based learning paths |

### 9.5 Future Enhancement Roadmap

| Priority | Enhancement |
|----------|------------|
| High | PDF export of the roadmap |
| High | Retry logic with backoff for Groq rate limits |
| Medium | Progress tracking: user marks completed weeks |
| Medium | Multiple saved profiles / comparison |
| Low | Integration with LinkedIn Learning / Coursera APIs for live course data |
| Low | RAG (Retrieval-Augmented Generation) with a curated career resource database |

---

*Document version: 1.0 · Generated for AI Career Mentor Agent project*

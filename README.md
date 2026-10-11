# 🎯 AI Career Mentor & Skill-Gap Agent

> An **Agentic AI** application that analyses your skill gaps, builds a personalised 30-day learning roadmap, and coaches you towards your target career role — powered by **Groq** and **Qwen3 32B**.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Skill Gap Analysis** | Agent observes your profile, reasons about required vs. possessed skills, and labels each gap |
| 📋 **30-Day Roadmap** | Week-by-week learning plan with free resources, exercises, and time allocations |
| 💬 **AI Career Coach Chat** | Interactive multi-turn coach for mock interviews, resume review, and career Q&A |
| ⬇️ **Roadmap Export** | Download your personalised roadmap as a Markdown file |
| 🔒 **Privacy First** | API key never stored — used only in-memory per call |

---

## 🏗️ Architecture Overview

```
career_mentor_agent/
├── app.py               ← Streamlit UI (sidebar + two-tab interface)
├── agent/
│   └── mentor_agent.py  ← ReAct-style agent: prompts, gap analysis, chat logic, guardrails
├── utils/
│   └── groq_client.py   ← Groq API wrapper: call_llm(), error handling
├── SDLC.md              ← Full 9-phase Agentic AI SDLC documentation
├── requirements.txt     ← Python dependencies
├── run.bat              ← One-click Windows launcher
└── README.md            ← This file
```

### Agent Flow (ReAct Pattern)

```
User Profile (Observe)
        │
        ▼
  Required Skills for Role (Reason Step 1)
        │
        ▼
  Compare vs. Current Skills — label ✅ 🔶 ❌ (Reason Step 2)
        │
        ▼
  Prioritise Top Gaps (Reason Step 3)
        │
        ▼
  Week-by-Week Roadmap + Success Metrics (Act)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- A free [Groq API key](https://console.groq.com) (sign up in < 2 minutes)

### Installation

```bash
# Navigate to the project directory
cd career_mentor_agent

# Install dependencies
pip install -r requirements.txt

# Launch the application
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**

### Windows One-Click Launch

Double-click **`run.bat`** — it installs dependencies and starts the app automatically.

---

## 📖 Usage Guide

### Step 1 — Fill in Your Profile (Sidebar)

| Field | Example |
|-------|---------|
| Groq API Key | `gsk_...` (masked) |
| Target Job Role | `Senior Data Scientist` |
| Experience Level | `Intermediate` |
| Current Core Skills | `Python, SQL, Excel, Basic ML` |
| Weekly Time | `10 hours/week` |

Click **💾 Save Profile** to activate the agent.

### Step 2 — Generate Your Roadmap (Tab 1)

Click **🔍 Analyse & Generate Roadmap**. The agent will:
1. List all required skills for your target role
2. Compare them against your current skills
3. Identify and prioritise your gaps
4. Build a 30-day week-by-week learning plan
5. Define measurable success metrics

Download the result with **⬇️ Download Roadmap as Markdown**.

### Step 3 — Chat with Your Career Coach (Tab 2)

Start a conversation. Try:
- *"Start a mock interview for a Senior Data Scientist role"*
- *"Review this resume bullet: Managed data pipelines"*
- *"What should I focus on in Week 1 of my plan?"*
- *"What are the most important soft skills for my target role?"*

---

## 🛡️ Guardrails & Ethics

This application implements **three layers of safety guardrails**:

1. **LLM System Prompt** — The model is explicitly instructed to:
   - Stay within career mentorship, skill development, and interview prep only
   - Never guarantee employment or job placement
   - Refuse legal and financial advice

2. **Python Post-Processing** — The disclaimer is programmatically appended to every roadmap and formal advice block, regardless of LLM output.

3. **Contextual Detection** — In chat mode, keyword detection triggers the disclaimer on any response containing roadmap, plan, recommendation, or strategy content.

**Disclaimer appended to every formal output:**
> ⚠️ This AI-generated career guidance is for educational and planning purposes only and does not guarantee job placement or professional hiring outcomes.

---

## ⚙️ Configuration

| Parameter | Value | Location |
|-----------|-------|----------|
| LLM Model | `qwen/qwen3-32b` | `utils/groq_client.py` |
| Max Tokens | `1000` per call | `utils/groq_client.py` |
| Roadmap Temperature | `0.6` | `agent/mentor_agent.py` |
| Chat Temperature | `0.75` | `agent/mentor_agent.py` |

---

## 🔒 Security Notes

- The Groq API key is entered via a **password-type masked input** field
- The key is **not stored** in `st.session_state`, environment variables, or any file
- Each LLM call receives the key as a function parameter scoped to that call frame
- No user data is logged, transmitted, or persisted beyond the browser session

---

## 📦 Dependencies

```
streamlit>=1.32.0
groq>=0.9.0
python-dotenv>=1.0.0
```

---

## 🗺️ SDLC Documentation

Full 9-phase Agentic AI SDLC is documented in [`SDLC.md`](./SDLC.md), covering:

1. Problem Definition
2. Requirements Analysis
3. Agent Design
4. LLM and Capability Selection
5. Prompt and Guardrail Design
6. Application Development
7. Testing and Evaluation
8. Deployment
9. Documentation

---

## 🤝 Contributing

Contributions are welcome. Please open an issue before submitting a pull request.

---

## ⚠️ Disclaimer

This application provides AI-generated career guidance for **educational and planning purposes only**. It does not guarantee employment, job placement, salary outcomes, or any professional hiring result. Always supplement AI guidance with advice from qualified human career professionals.

---

*Built with ❤️ using Python, Streamlit, and Groq*

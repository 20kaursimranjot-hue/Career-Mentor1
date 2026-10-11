"""
mentor_agent.py
---------------
All agent logic lives here:

  • build_system_prompt()        – shared base prompt with guardrails
  • run_gap_analysis()           – Skill Gap Analysis + 30-Day Roadmap
  • run_chat_turn()              – AI Career Coach chat (stateful history)

The agent follows a ReAct-style reasoning pattern:
  Observe (user profile) → Think (identify gaps) → Act (produce plan/advice)

Guardrails are enforced at three levels:
  1. System prompt – LLM is instructed on domain, tone, and disclaimers.
  2. Output injection – Disclaimer is appended to every formal output block.
  3. Input validation – handled in app.py before the agent is invoked.
"""

from __future__ import annotations

from typing import Dict, List

from utils.groq_client import call_llm

# ── Disclaimer ─────────────────────────────────────────────────────────────────
DISCLAIMER = (
    "\n\n---\n"
    "⚠️ **Disclaimer:** This AI-generated career guidance is for educational "
    "and planning purposes only and does not guarantee job placement or "
    "professional hiring outcomes."
)

# ── System-prompt builder ───────────────────────────────────────────────────────
def build_system_prompt(user_profile: Dict[str, str]) -> str:
    """
    Construct the base system prompt that is prepended to every conversation.

    The prompt hard-codes domain restrictions, tone guidelines, and disclaimer
    requirements so the LLM cannot be jailbroken into off-topic territory via
    user messages.
    """
    return f"""You are CareerMentorAI, an expert AI Career Mentor and Skill-Gap Analyst.

## Your Role
You help professionals bridge the gap between their current skills and their target job role by:
- Performing structured skill-gap analysis
- Creating actionable, week-by-week learning roadmaps
- Coaching users through mock interview questions
- Reviewing and improving resume bullet points
- Answering career guidance questions with empathy and pragmatism

## User Profile (use this context in every response)
- **Target Role:** {user_profile.get('target_role', 'Not specified')}
- **Experience Level:** {user_profile.get('experience_level', 'Not specified')}
- **Current Skills:** {user_profile.get('current_skills', 'Not specified')}
- **Weekly Time Available:** {user_profile.get('weekly_hours', 'Not specified')}

## Strict Domain Guardrails
1. **Stay on topic.** You ONLY discuss career development, skill building, interview preparation, resume writing, and professional growth. Refuse any request outside this domain politely but firmly.
2. **No false guarantees.** Never promise or imply guaranteed employment, salary figures, or hiring outcomes. Use language like "typically", "often", "may help", "is a strong signal for".
3. **No legal or financial advice.** Do not advise on employment contracts, salary negotiations as legal matters, tax implications, visa issues, or investment decisions.
4. **Supportive and realistic tone.** Be motivating and empathetic, but set realistic expectations. Acknowledge that career transitions take time and effort.
5. **Cite only free, publicly accessible resources** when recommending learning materials (e.g., freeCodeCamp, Coursera free tier, official documentation, YouTube channels, GitHub repos).

## Disclaimer Requirement
After EVERY roadmap, skill-gap analysis, or formal career advice block, you MUST append this exact disclaimer:
"⚠️ Disclaimer: This AI-generated career guidance is for educational and planning purposes only and does not guarantee job placement or professional hiring outcomes."

## Response Style
- Use clear Markdown: headers (##, ###), bullet points, numbered lists, bold for emphasis.
- Keep responses focused and actionable — avoid padding.
- Structure roadmaps week-by-week for clarity.
- For mock interviews, ask one question at a time and provide detailed feedback after the user responds.
"""


# ── Gap Analysis & Roadmap ──────────────────────────────────────────────────────
def run_gap_analysis(api_key: str, user_profile: Dict[str, str]) -> str:
    """
    Agentic reasoning loop:
      1. Observe  – ingest the user's full profile.
      2. Think    – identify required vs possessed skills.
      3. Act      – produce a structured 30-day roadmap.

    Returns the LLM's formatted output string.
    """
    system_prompt = build_system_prompt(user_profile)

    user_message = f"""
Please perform a complete **Skill Gap Analysis and 30-Day Learning Roadmap** for me.

### Step 1 – Required Skills
List the 8–12 core technical and soft skills typically required for a **{user_profile.get('target_role')}**.

### Step 2 – Skill Gap Identification
Compare the required skills against my current skills: **{user_profile.get('current_skills')}**.
Clearly label each required skill as:
- ✅ Already have it (or close enough)
- 🔶 Partially developed — needs strengthening
- ❌ Missing — needs to be built from scratch

### Step 3 – Priority Gaps
Highlight the top 3–5 priority gaps I should focus on first, with a brief justification.

### Step 4 – 30-Day Week-by-Week Roadmap
Given that I have **{user_profile.get('weekly_hours')}** available per week, create a structured plan:

**Week 1 – Foundation**
**Week 2 – Core Skills**
**Week 3 – Applied Practice**
**Week 4 – Portfolio & Mock Interviews**

For each week include:
- Specific learning goals
- Recommended free resources (with URLs where possible)
- Practical exercises or mini-projects
- Estimated daily time allocation

### Step 5 – Success Metrics
Define 3–5 measurable milestones to track progress at the end of 30 days.

Be specific, realistic, and encouraging.
"""

    messages = [
        {"role": "system",  "content": system_prompt},
        {"role": "user",    "content": user_message},
    ]

    result = call_llm(api_key=api_key, messages=messages, temperature=0.6)

    # Guardrail layer 2: ensure disclaimer is always present
    if "Disclaimer" not in result:
        result += DISCLAIMER

    return result


# ── Career Coach Chat ───────────────────────────────────────────────────────────
def build_chat_system_prompt(user_profile: Dict[str, str]) -> str:
    """System prompt variant optimised for interactive multi-turn coaching."""
    base = build_system_prompt(user_profile)
    coaching_addendum = """
## Chat Mode Behaviour
- This is an interactive coaching session. Keep each response concise (3–6 sentences or one focused block) unless the user asks for more detail.
- For **mock interview** requests: ask one interview question relevant to the target role, wait for the user's answer, then give structured feedback (strengths / areas to improve / model answer).
- For **resume bullet point review**: rewrite the bullet using the STAR method (Situation, Task, Action, Result) and explain your changes.
- For **career questions**: give one clear, actionable recommendation first, then elaborate.
- Always remember the full conversation history to avoid repetition.
"""
    return base + coaching_addendum


def run_chat_turn(
    api_key: str,
    user_profile: Dict[str, str],
    chat_history: List[Dict[str, str]],
    user_message: str,
) -> str:
    """
    Process one turn of the Career Coach chat.

    Parameters
    ----------
    api_key      : Groq API key.
    user_profile : Sidebar profile dict.
    chat_history : List of {"role": ..., "content": ...} dicts representing
                   the conversation so far (NOT including the current message).
    user_message : The user's latest message text.

    Returns
    -------
    The assistant's reply string.
    """
    system_prompt = build_chat_system_prompt(user_profile)

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        *chat_history,
        {"role": "user", "content": user_message},
    ]

    reply = call_llm(api_key=api_key, messages=messages, temperature=0.75)

    # Guardrail: attach disclaimer only when the reply contains formal advice blocks
    formal_keywords = ("roadmap", "plan", "recommend", "guidance", "strategy", "advice")
    if any(kw in reply.lower() for kw in formal_keywords) and "Disclaimer" not in reply:
        reply += DISCLAIMER

    return reply

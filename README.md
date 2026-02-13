---
title: wamiq_rehman_personal_agent
app_file: app.py
sdk: gradio
sdk_version: 6.5.1
---
# Personal Brand AI Agent

An **AI-powered chat agent** that represents you on your personal site: it answers questions about your background using your resume, captures leads, and stays on-message using **RAG**, **intent-aware prompting**, and **LLM tool use**.

---

## Features

- **RAG over your resume** — Only the most relevant chunks of your PDF are injected into each reply, so answers are grounded and token-efficient.
- **Intent-aware behavior** — User messages are classified (e.g. career Q&A vs. contact intent); the system prompt is tailored so the model emphasizes resume context or lead capture when appropriate.
- **Bounded conversation memory** — The last N turns are kept in context so the agent can maintain a coherent multi-turn dialogue without unbounded history.
- **LLM tool use (function calling)** — The agent can record contact details and log questions it couldn’t answer, with results sent to you via **Pushover** (or pluggable webhooks).
- **Semantic retrieval** — Resume text is chunked, embedded with **OpenAI embeddings**, and retrieved by **cosine similarity** to the user’s question for accurate, context-aware answers.
- **Clean agent architecture** — Single orchestration layer (controller) that runs intent → retrieval → prompt build → OpenAI chat loop with tools, so the pipeline is easy to reason about and extend.
[Live Demo](https://huggingface.co/spaces/Wamiqreh/wamiq_rehman_personal_agent)
---

## Techniques & Architecture

| Area | Approach |
|------|----------|
| **Retrieval (RAG)** | PDF → full-text extraction → word-based chunking (~500 words) → OpenAI `text-embedding-3-small` per chunk → at query time: embed question, cosine similarity over chunk vectors, return top-k chunks as context. |
| **Intent** | Lightweight classifier (keyword-based) labels each message as `resume_qa`, `contact`, or `general`; intent is passed into the system prompt so the model can adapt tone and goals. |
| **Memory** | In-process `Memory` keeps the last N user/assistant turns; history is appended to the message list sent to the LLM each turn. |
| **Tools** | OpenAI function-calling: `record_user_details` (email, name, notes) and `record_unknown_question` (question text). Tool results are fed back into the chat loop until the model produces a final reply. |
| **Orchestration** | One `Agent` instance: load resume once, chunk and embed once at init; each `chat()` run does intent → retrieve chunks → build system prompt (summary + RAG context + intent) → run OpenAI with tools in a loop → return final assistant message. |

---

## Tech Stack

- **Python 3.10+**
- **OpenAI API** — Chat completions (`gpt-4o-mini`), embeddings (`text-embedding-3-small`)
- **Gradio** — Chat UI
- **pypdf** — Resume PDF text extraction
- **NumPy** — Cosine similarity for retrieval
- **Pushover** — Notifications for leads and unknown questions (optional; can be replaced with another webhook)
- **uv** — Dependency and run management (optional; `pip` works too)

---

## Project Structure

```
├── app.py                 # Gradio entrypoint; loads resume/summary, creates Agent, wires chat
├── agent/
│   ├── controller.py      # Agent class: intent → RAG → prompt → OpenAI + tool loop
│   ├── intent.py          # Intent classification (resume_qa | contact | general)
│   ├── memory.py          # Bounded conversation history (last N messages)
│   ├── retrieval.py       # load_resume, chunk_text, embed_texts, retrieve_chunks (RAG)
│   ├── tools.py           # record_user_details, record_unknown_question (+ Pushover)
│   ├── schemas.py         # OpenAI function definitions for tools
│   └── prompts.py         # system_prompt(summary, context, name, intent)
├── data/
│   ├── resume.pdf         # Your resume (PDF)
│   └── summary.txt        # Short summary / bio for the agent
├── pyproject.toml
├── requirements.txt
└── .env.example            # OPENAI_API_KEY, PUSHOVER_*, PERSON_NAME, etc.
```

---

## Setup & Run

1. **Clone and enter the project**
   ```bash
   cd personal-brand-ai-agent
   ```

2. **Environment**
   - Copy `.env.example` to `.env`.
   - Set `OPENAI_API_KEY` (required).
   - Optionally set `PUSHOVER_TOKEN`, `PUSHOVER_USER` for lead/unknown-question notifications, and `PERSON_NAME` for the agent’s identity.

3. **Data**
   - Place your resume as `data/resume.pdf`.
   - Place a short summary/bio as `data/summary.txt`.

4. **Run with uv (recommended)**
   ```bash
   uv sync
   uv run python app.py
   ```
   Or one-shot: `uv run python app.py`

5. **Run with pip**
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

6. Open the URL Gradio prints (e.g. `http://127.0.0.1:7860`) and chat with your personal brand agent.

---

## Design Notes (for discussion)

- **Why RAG instead of full-document context?** — Keeps prompts smaller and focused, reduces cost and latency, and makes it easier to scale to longer resumes or more documents later.
- **Why intent in the prompt?** — Gives the model an explicit signal to emphasize career content vs. encouraging contact, improving consistency without extra model calls.
- **Why tools for “record” actions?** — Keeps lead capture and logging as first-class, auditable actions the model can choose, rather than parsing free text.

This project demonstrates **RAG**, **LLM orchestration with tool use**, **intent-aware prompting**, and **modular agent design** — all directly relevant to production LLM applications.

# AI Personal Brand Assistant

Chat assistant that answers questions about your resume and personal brand using your own data.

## Structure

```
├── app.py                   # Gradio entrypoint
├── agent/
│   ├── controller.py        # Main agent orchestration
│   ├── intent.py            # Intent classification
│   ├── memory.py            # Conversation memory
│   ├── retrieval.py         # RAG logic
│   ├── tools.py             # Tool implementations
│   ├── schemas.py           # Tool JSON schemas
│   └── prompts.py           # Prompt templates
├── data/
│   ├── resume.pdf
│   └── summary.txt
├── pyproject.toml
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. Copy `.env.example` to `.env` and add your API keys (e.g. `OPENAI_API_KEY`), `PUSHOVER_*`, and `PERSON_NAME`.
2. Put your `resume.pdf` and `summary.txt` in `data/`.

## Run locally

**Using uv (recommended):**

```bash
# From the project root (ai-personal-brand-assistant)
uv sync
uv run python app.py
```

Or in one step (uv creates the venv and installs deps on first run):

```bash
uv run python app.py
```

**Using pip:**

```bash
pip install -r requirements.txt
python app.py
```

## Usage

Open the Gradio UI and chat; the agent will use your resume and summary to answer questions (once RAG and tools are implemented).

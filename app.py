"""
Gradio entrypoint for the personal brand assistant.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
import gradio as gr

from agent.controller import Agent
from agent.retrieval import load_resume

load_dotenv(override=True)

# Paths
DATA_DIR = Path(__file__).resolve().parent / "data"
SUMMARY_PATH = DATA_DIR / "summary.txt"

# Load context once at startup
resume_text = load_resume()
summary_text = SUMMARY_PATH.read_text(encoding="utf-8") if SUMMARY_PATH.exists() else ""
agent = Agent(summary_text, resume_text)

PERSON_NAME = os.getenv("PERSON_NAME", "Wamiq Rehman")


def chat_fn(message, history):
    """Gradio chat handler: run agent and return assistant reply."""
    return agent.chat(message)


def main():
    demo = gr.ChatInterface(
        fn=chat_fn,
        title=f"Chat with {PERSON_NAME}",
        description="AI Personal Brand Agent",
    )
    demo.launch()


if __name__ == "__main__":
    main()

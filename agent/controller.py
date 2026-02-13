"""
Main agent orchestration: Agent class with Memory, intent, RAG, and tool loop.
"""

import json
import os

from openai import OpenAI

from agent.intent import classify_intent
from agent.memory import Memory
from agent.prompts import system_prompt
from agent.retrieval import chunk_text, embed_texts, load_resume, retrieve_chunks
from agent.schemas import TOOLS
from agent.tools import record_user_details, record_unknown_question

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


class Agent:
    def __init__(self, summary_text: str, resume_text: str):
        self.summary = summary_text
        self.resume = resume_text
        self.chunks = chunk_text(resume_text)
        self.chunk_embeddings = embed_texts(self.chunks) if self.chunks else []
        self.memory = Memory(10)

    def chat(self, user_message: str) -> str:
        self.memory.add("user", user_message)

        # 1) Intent
        intent = classify_intent(user_message)

        # 2) RAG
        relevant_chunks = retrieve_chunks(
            user_message, self.chunks, self.chunk_embeddings, top_k=3
        )
        context = "\n\n".join(relevant_chunks) if relevant_chunks else "(No relevant excerpts found.)"

        # 3) Build prompt (intent used to tailor the system prompt)
        name = os.getenv("PERSON_NAME", "The site owner")
        prompt = system_prompt(self.summary, context, name=name, intent=intent)

        # 4) Call OpenAI with tool support
        client = _get_client()
        messages = [{"role": "system", "content": prompt}] + self.memory.get_history()

        done = False
        while not done:
            response = client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
                messages=messages,
                tools=TOOLS,
            )
            choice = response.choices[0]

            if choice.finish_reason == "tool_calls":
                tool_calls = choice.message.tool_calls
                # Append assistant message as dict for API
                msg = choice.message
                messages.append({
                    "role": msg.role,
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments or "{}",
                            },
                        }
                        for tc in tool_calls
                    ],
                })
                for call in tool_calls:
                    tool_name = call.function.name
                    args = json.loads(call.function.arguments or "{}")
                    if tool_name == "record_user_details":
                        result = record_user_details(**args)
                    elif tool_name == "record_unknown_question":
                        result = record_unknown_question(**args)
                    else:
                        result = {}
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(result),
                        "tool_call_id": call.id,
                    })
            else:
                done = True

        response_text = choice.message.content or ""
        self.memory.add("assistant", response_text)
        return response_text.strip()

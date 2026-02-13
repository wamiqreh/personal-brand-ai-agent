"""
Load resume PDF, chunk, embed, and retrieve relevant chunks (RAG).
"""

from pathlib import Path

import numpy as np
from openai import OpenAI
from pypdf import PdfReader

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RESUME_PATH = DATA_DIR / "resume.pdf"

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def load_resume(path: str | Path | None = None) -> str:
    """Load resume text from PDF. Default path: data/resume.pdf."""
    p = Path(path) if path else RESUME_PATH
    if not p.exists():
        return ""
    reader = PdfReader(str(p))
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text


def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    """Split text into word-based chunks of roughly chunk_size words."""
    if not text.strip():
        return []
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i : i + chunk_size]))
    return chunks


def embed_texts(texts: list[str], model: str = "text-embedding-3-small") -> list[np.ndarray]:
    """Embed a list of texts using OpenAI. Returns list of numpy vectors (one per chunk)."""
    client = _get_client()
    embeddings = []
    for t in texts:
        inp = t.strip() or " "
        emb = client.embeddings.create(model=model, input=inp)
        embeddings.append(np.array(emb.data[0].embedding))
    return embeddings


def retrieve_chunks(
    user_question: str,
    chunks: list[str],
    chunk_embeddings: list[np.ndarray],
    top_k: int = 3,
    model: str = "text-embedding-3-small",
) -> list[str]:
    """Embed the question, compute cosine similarity, return top_k chunk texts."""
    if not chunks or not chunk_embeddings or top_k <= 0:
        return []
    client = _get_client()
    q_emb = client.embeddings.create(model=model, input=user_question)
    q_vec = np.array(q_emb.data[0].embedding)
    # Cosine similarity (embeddings are typically normalized; if not, normalize)
    sims = [
        np.dot(q_vec, c) / (np.linalg.norm(q_vec) * np.linalg.norm(c) + 1e-9)
        for c in chunk_embeddings
    ]
    top_indices = np.argsort(sims)[-top_k:][::-1]
    return [chunks[i] for i in top_indices]

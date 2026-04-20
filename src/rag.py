"""
RAG module for CXR (Chest X-Ray) knowledge base.

Usage:
    from rag import CXRRag

    rag = CXRRag("cxr_kb.jsonl")
    context = rag.retrieve("what does blunting of costophrenic angle mean?")
    answer  = rag.answer("what does blunting of costophrenic angle mean?", predicted_labels=["effusion"])
"""

from __future__ import annotations

import json
import threading
import numpy as np
from pathlib import Path

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    raise ImportError(
        f"Missing dependency: {e}. Run: pip install faiss-cpu sentence-transformers"
    ) from e

_REQUIRED_DOC_KEYS = {"id", "topic", "type", "text"}
_MAX_QUESTION_LEN = 2000  # chars — prevents DoS via huge embedding inputs


def _validate_doc(doc: dict, line_num: int) -> None:
    missing = _REQUIRED_DOC_KEYS - doc.keys()
    if missing:
        raise ValueError(f"JSONL line {line_num} missing required keys: {missing}")
    if not isinstance(doc["text"], str):
        raise ValueError(
            f"JSONL line {line_num}: 'text' must be a string, got {type(doc['text']).__name__}"
        )


class CXRRag:
    """Retrieval-Augmented Generation over the CXR knowledge base."""

    MODEL_NAME = "all-MiniLM-L6-v2"
    _model_cache: dict[str, SentenceTransformer] = {}
    _model_lock: threading.Lock = threading.Lock()

    def __init__(self, kb_path: str, top_k: int = 5):
        """
        Args:
            kb_path: Path to the .jsonl knowledge base file.
            top_k:   Number of chunks to retrieve by default (must be >= 1).
        """
        if top_k < 1:
            raise ValueError(f"top_k must be >= 1, got {top_k}")
        self.kb_path = Path(kb_path)
        self.top_k = top_k
        self._model = self._load_model()
        self._docs: list[dict] = []
        self._index: faiss.IndexFlatIP | None = None
        self._build_index()

    # ------------------------------------------------------------------
    # Model caching — load once per process, reuse across instances
    # ------------------------------------------------------------------

    @classmethod
    def _load_model(cls) -> SentenceTransformer:
        if cls.MODEL_NAME not in cls._model_cache:
            with cls._model_lock:
                # Double-checked locking: re-check inside the lock
                if cls.MODEL_NAME not in cls._model_cache:
                    cls._model_cache[cls.MODEL_NAME] = SentenceTransformer(cls.MODEL_NAME)
        return cls._model_cache[cls.MODEL_NAME]

    # ------------------------------------------------------------------
    # Index building
    # ------------------------------------------------------------------

    def _build_index(self) -> None:
        """Load the JSONL knowledge base and build the FAISS index."""
        if not self.kb_path.exists():
            raise FileNotFoundError(f"Knowledge base not found: {self.kb_path}")

        self._docs = []
        with open(self.kb_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    doc = json.loads(line)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Malformed JSON on line {line_num} of {self.kb_path}: {e}"
                    ) from e
                _validate_doc(doc, line_num)
                self._docs.append(doc)

        if not self._docs:
            raise ValueError(f"Knowledge base at {self.kb_path} is empty.")

        texts = [doc["text"] for doc in self._docs]
        embeddings = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False, batch_size=64)

        # Ensure float32 — FAISS requires it regardless of hardware/model dtype
        embeddings = embeddings.astype(np.float32)

        # Normalise for cosine similarity via inner product
        faiss.normalize_L2(embeddings)

        dim = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dim)
        self._index.add(embeddings)

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve(
        self,
        question: str,
        predicted_labels: list[str] | None = None,
        top_k: int | None = None,
    ) -> list[dict]:
        """
        Retrieve the most relevant knowledge-base entries.

        Args:
            question:         The user's natural-language question (max 2000 chars).
            predicted_labels: Optional list of conditions detected by the
                              vision model (e.g. ["pneumonia", "effusion"]).
                              These are prepended to the query to bias
                              retrieval toward the detected findings.
            top_k:            How many entries to return (overrides default).

        Returns:
            List of dicts with keys: id, topic, type, text, score.
        """
        if self._index is None:
            raise RuntimeError(
                "FAISS index has not been built. Check that the knowledge base loaded correctly."
            )
        if not question or not question.strip():
            raise ValueError("question must not be empty.")
        if len(question) > _MAX_QUESTION_LEN:
            raise ValueError(
                f"question exceeds maximum length of {_MAX_QUESTION_LEN} characters."
            )

        k = top_k if top_k is not None else self.top_k
        if k < 1:
            raise ValueError(f"top_k must be >= 1, got {k}")

        # Fetch a larger candidate pool to allow diversity filtering.
        # We retrieve up to 4x more candidates than needed, then deduplicate
        # by (topic, type) to avoid returning 3x "Clinical Overview" chunks
        # when the user asks about symptoms or treatment of the same condition.
        candidate_k = min(k * 4, len(self._docs))

        # Filter empty labels, combine with question for a richer query
        clean_labels = [l.strip() for l in predicted_labels if l and l.strip()] if predicted_labels else []
        label_prefix = " ".join(clean_labels)
        query = f"{label_prefix} {question}".strip()[:_MAX_QUESTION_LEN]

        query_vec = self._model.encode([query], convert_to_numpy=True).astype(np.float32)
        faiss.normalize_L2(query_vec)

        scores, indices = self._index.search(query_vec, candidate_k)

        # Deduplicate: keep only the highest-scoring chunk per (topic, type) pair
        seen_keys: set[str] = set()
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            entry = dict(self._docs[idx])
            diversity_key = f"{entry.get('topic', '')}::{entry.get('type', '')}"
            if diversity_key in seen_keys:
                continue  # Skip duplicate (topic, type) — already have a better-scoring one
            seen_keys.add(diversity_key)
            entry["score"] = float(score)
            results.append(entry)
            if len(results) >= k:
                break

        return results

    # ------------------------------------------------------------------
    # Answer generation
    # ------------------------------------------------------------------

    def build_prompt(
        self,
        question: str,
        retrieved: list[dict],
        predicted_labels: list[str] | None = None,
        history: list[dict] | None = None,
    ) -> str:
        """
        Build a prompt string that combines retrieved context with the
        user's question.  Pass this to any LLM (OpenAI, HuggingFace, etc.).

        The user question is placed inside explicit delimiters to reduce
        prompt injection risk.

        Args:
            question:         The user's question.
            retrieved:        Output of retrieve().
            predicted_labels: Vision model detections (optional).
            history:          Previous chat history to prevent repetitive responses.

        Returns:
            A ready-to-use prompt string.
        """
        context_blocks = []
        for i, doc in enumerate(retrieved, 1):
            topic = doc.get("topic", "Unknown")
            type_ = doc.get("type", "Unknown")
            text = doc.get("text", "")
            context_blocks.append(f"[{i}] Topic: {topic} | Type: {type_}\n{text}")
        context = "\n\n".join(context_blocks) if context_blocks else "No relevant context found in the knowledge base."

        # Sanitize labels to prevent prompt injection, then wrap in delimiters
        safe_labels = [l.replace("---", "").strip() for l in predicted_labels if l and l.strip()] if predicted_labels else []
        label_line = ""
        if safe_labels:
            label_line = (
                "--- DETECTED FINDINGS START ---\n"
                f"The vision model detected the following finding(s): "
                f"{', '.join(safe_labels)}.\n"
                "--- DETECTED FINDINGS END ---\n\n"
            )

        # History string building
        history_text = ""
        if history:
            history_lines = []
            for msg in history:
                speaker = "Patient" if msg["type"] == "user" else "Assistant"
                # Exclude internal system preprompts if they are generic, but including all memory is fine
                history_lines.append(f"{speaker}: {msg['text']}")
            history_text = "--- CHAT HISTORY START ---\n" + "\n\n".join(history_lines) + "\n--- CHAT HISTORY END ---\n\n"
            
        prompt = (
            "You are a friendly, highly intelligent, and empathetic AI clinical assistant "
            "explaining chest X-ray findings to a patient. \n\n"
            "STRICT RULES:\n"
            "1. Do NOT repeat the same explanations or greetings. Read the CHAT HISTORY and provide fresh, helpful follow-up responses directly related to what they just asked.\n"
            "2. Be concise but maintain a warm, assuring, and conversational tone.\n"
            "3. Use the provided Context as your primary reference, but actively use your own clinical reasoning and medical knowledge to provide a comprehensive, logical explanation.\n"
            "4. Never provide a final diagnosis, only explain possibilities and strongly recommend consulting a physician.\n\n"
            f"{label_line}"
            f"Context:\n{context}\n\n"
            f"{history_text}"
            "--- USER QUESTION START ---\n"
            f"{question}\n"
            "--- USER QUESTION END ---\n\n"
            "Answer:"
        )
        return prompt

    def answer(
        self,
        question: str,
        predicted_labels: list[str] | None = None,
        top_k: int | None = None,
        history: list[dict] | None = None,
    ) -> dict:
        """
        Full RAG pipeline: retrieve context + build prompt.

        Args:
            question:         The user's question.
            predicted_labels: Vision model detections (optional).
            top_k:            Number of chunks to retrieve.

        Returns:
            dict with keys:
              - "prompt":    Ready-to-use LLM prompt (str)
              - "context":   List of retrieved docs
              - "question":  Original question
        """
        retrieved = self.retrieve(question, predicted_labels=predicted_labels, top_k=top_k)
        prompt = self.build_prompt(question, retrieved, predicted_labels=predicted_labels, history=history)
        return {
            "prompt": prompt,
            "context": retrieved,
            "question": question,
        }

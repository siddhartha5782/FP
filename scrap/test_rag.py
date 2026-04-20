"""
Tests for src/rag.py — CXRRag module.

Run with:
    pytest tests/test_rag.py -v
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from rag import CXRRag

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_DOCS = [
    {"id": "pneumonia_basic", "topic": "pneumonia", "type": "appearance_basic",
     "text": "Pneumonia typically appears as focal or patchy air-space opacity."},
    {"id": "effusion_basic", "topic": "effusion", "type": "appearance_basic",
     "text": "Pleural effusion appears as blunting of the costophrenic angle."},
    {"id": "pneumothorax_basic", "topic": "pneumothorax", "type": "appearance_basic",
     "text": "Pneumothorax shows absence of lung markings in the pleural space."},
    {"id": "edema_basic", "topic": "edema", "type": "appearance_basic",
     "text": "Pulmonary edema presents as bilateral diffuse opacity."},
    {"id": "cardiomegaly_basic", "topic": "cardiomegaly", "type": "appearance_basic",
     "text": "Cardiomegaly is indicated by an enlarged cardiac silhouette."},
    {"id": "atelectasis_basic", "topic": "atelectasis", "type": "appearance_basic",
     "text": "Atelectasis presents as volume loss and increased opacity."},
]


@pytest.fixture(scope="module")
def kb_file(tmp_path_factory):
    """Write sample docs to a temp JSONL file and return its path."""
    path = tmp_path_factory.mktemp("data") / "test_kb.jsonl"
    with open(path, "w") as f:
        for doc in SAMPLE_DOCS:
            f.write(json.dumps(doc) + "\n")
    return str(path)


@pytest.fixture(scope="module")
def rag(kb_file):
    """Shared CXRRag instance for the test module."""
    return CXRRag(kb_file, top_k=3)


# ---------------------------------------------------------------------------
# 1. Happy path tests
# ---------------------------------------------------------------------------

class TestInit:
    def test_loads_all_docs(self, rag):
        assert len(rag._docs) == len(SAMPLE_DOCS)

    def test_builds_faiss_index(self, rag):
        assert rag._index is not None
        assert rag._index.ntotal == len(SAMPLE_DOCS)

    def test_model_is_cached(self, kb_file):
        rag1 = CXRRag(kb_file)
        rag2 = CXRRag(kb_file)
        assert rag1._model is rag2._model


class TestRetrieve:
    def test_returns_top_k_results(self, rag):
        results = rag.retrieve("what is pneumonia?")
        assert len(results) == 3

    def test_result_keys(self, rag):
        results = rag.retrieve("what is pneumonia?")
        for r in results:
            assert {"id", "topic", "type", "text", "score"}.issubset(r.keys())

    def test_top_k_override(self, rag):
        results = rag.retrieve("what is pneumonia?", top_k=2)
        assert len(results) == 2

    def test_with_predicted_labels(self, rag):
        results = rag.retrieve("what do I have?", predicted_labels=["effusion"])
        assert len(results) == 3
        assert all("score" in r for r in results)

    def test_labels_bias_ranking_toward_topic(self, rag):
        # With effusion label, effusion doc should score higher than without
        with_label = rag.retrieve("what do I have?", predicted_labels=["effusion"], top_k=6)
        without_label = rag.retrieve("what do I have?", top_k=6)
        effusion_score_with = next(r["score"] for r in with_label if r["id"] == "effusion_basic")
        effusion_score_without = next(r["score"] for r in without_label if r["id"] == "effusion_basic")
        assert effusion_score_with >= effusion_score_without

    def test_scores_descending(self, rag):
        results = rag.retrieve("lung opacity findings")
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_scores_in_valid_range(self, rag):
        results = rag.retrieve("chest x-ray findings")
        for r in results:
            assert -1.0 <= r["score"] <= 1.0

    def test_no_duplicate_indices(self, rag):
        results = rag.retrieve("lung findings")
        ids = [r["id"] for r in results]
        assert len(ids) == len(set(ids))

    def test_deterministic(self, rag):
        r1 = rag.retrieve("pneumonia findings")
        r2 = rag.retrieve("pneumonia findings")
        assert [r["id"] for r in r1] == [r["id"] for r in r2]

    def test_exact_match_is_top_result(self, rag):
        query = SAMPLE_DOCS[1]["text"]  # effusion text
        results = rag.retrieve(query)
        assert results[0]["id"] == "effusion_basic"

    def test_top_k_larger_than_corpus(self, rag):
        results = rag.retrieve("any finding", top_k=999)
        assert len(results) == len(SAMPLE_DOCS)

    def test_empty_predicted_labels_same_as_none(self, rag):
        r1 = rag.retrieve("chest pain", predicted_labels=None)
        r2 = rag.retrieve("chest pain", predicted_labels=[])
        assert [r["id"] for r in r1] == [r["id"] for r in r2]


class TestBuildPrompt:
    def test_contains_system_instruction(self, rag):
        retrieved = rag.retrieve("what is this?")
        prompt = rag.build_prompt("what is this?", retrieved)
        assert "You are a helpful medical assistant" in prompt

    def test_contains_physician_disclaimer(self, rag):
        retrieved = rag.retrieve("is this serious?")
        prompt = rag.build_prompt("is this serious?", retrieved)
        assert "Always recommend consulting a licensed physician" in prompt

    def test_ends_with_answer_marker(self, rag):
        retrieved = rag.retrieve("what is this?")
        prompt = rag.build_prompt("what is this?", retrieved)
        assert prompt.rstrip().endswith("Answer:")

    def test_question_wrapped_in_delimiters(self, rag):
        retrieved = rag.retrieve("what is this?")
        prompt = rag.build_prompt("what is this?", retrieved)
        assert "--- USER QUESTION START ---" in prompt
        assert "--- USER QUESTION END ---" in prompt

    def test_context_block_numbering(self, rag):
        retrieved = rag.retrieve("lung findings", top_k=3)
        prompt = rag.build_prompt("lung findings", retrieved)
        assert "[1]" in prompt
        assert "[2]" in prompt
        assert "[3]" in prompt

    def test_context_block_contains_topic_and_type(self, rag):
        retrieved = rag.retrieve("lung findings")
        prompt = rag.build_prompt("lung findings", retrieved)
        assert "Topic:" in prompt
        assert "| Type:" in prompt

    def test_label_line_present_when_labels_given(self, rag):
        retrieved = rag.retrieve("what is this?")
        prompt = rag.build_prompt("what is this?", retrieved, predicted_labels=["pneumonia"])
        assert "The vision model detected the following finding(s): pneumonia" in prompt

    def test_label_line_absent_when_no_labels(self, rag):
        retrieved = rag.retrieve("what is this?")
        prompt = rag.build_prompt("what is this?", retrieved, predicted_labels=None)
        assert "vision model detected" not in prompt

    def test_label_line_format_multiple_labels(self, rag):
        retrieved = rag.retrieve("what is this?")
        prompt = rag.build_prompt("what is this?", retrieved, predicted_labels=["pneumonia", "effusion"])
        assert "pneumonia, effusion" in prompt

    def test_question_appears_after_context(self, rag):
        retrieved = rag.retrieve("is this bad?")
        prompt = rag.build_prompt("is this bad?", retrieved)
        context_pos = prompt.index("Context:")
        question_pos = prompt.index("--- USER QUESTION START ---")
        assert question_pos > context_pos

    def test_label_line_absent_when_empty_list(self, rag):
        retrieved = rag.retrieve("what is this?")
        prompt = rag.build_prompt("what is this?", retrieved, predicted_labels=[])
        assert "vision model detected" not in prompt

    def test_empty_retrieved_list_does_not_raise(self, rag):
        prompt = rag.build_prompt("what is this?", [])
        assert "Answer:" in prompt


class TestAnswer:
    def test_returns_correct_keys(self, rag):
        result = rag.answer("what is this finding?")
        assert set(result.keys()) == {"prompt", "context", "question"}

    def test_question_passthrough(self, rag):
        q = "is this serious?"
        result = rag.answer(q)
        assert result["question"] == q

    def test_context_matches_retrieve(self, rag):
        q = "what does this mean?"
        labels = ["pneumonia"]
        context = rag.retrieve(q, predicted_labels=labels)
        result = rag.answer(q, predicted_labels=labels)
        assert [r["id"] for r in result["context"]] == [r["id"] for r in context]

    def test_very_long_question(self, rag):
        q = "what is this? " * 100
        result = rag.answer(q)
        assert "prompt" in result


# ---------------------------------------------------------------------------
# 2. Error / edge case tests
# ---------------------------------------------------------------------------

class TestErrors:
    def test_missing_kb_file_raises(self):
        with pytest.raises(FileNotFoundError):
            CXRRag("nonexistent_file.jsonl")

    def test_empty_kb_file_raises(self, tmp_path):
        empty = tmp_path / "empty.jsonl"
        empty.write_text("")
        with pytest.raises(ValueError, match="empty"):
            CXRRag(str(empty))

    def test_blank_lines_skipped(self, tmp_path):
        path = tmp_path / "blanks.jsonl"
        with open(path, "w") as f:
            f.write("\n")
            f.write(json.dumps(SAMPLE_DOCS[0]) + "\n")
            f.write("\n")
        rag = CXRRag(str(path))
        assert len(rag._docs) == 1

    def test_empty_question_raises(self, rag):
        with pytest.raises(ValueError, match="empty"):
            rag.retrieve("")

    def test_whitespace_question_raises(self, rag):
        with pytest.raises(ValueError, match="empty"):
            rag.retrieve("   ")

    def test_top_k_zero_raises(self, rag):
        with pytest.raises(ValueError):
            rag.retrieve("lung findings", top_k=0)

    def test_top_k_negative_raises(self, rag):
        with pytest.raises(ValueError):
            rag.retrieve("lung findings", top_k=-1)

    def test_init_top_k_zero_raises(self, kb_file):
        with pytest.raises(ValueError):
            CXRRag(kb_file, top_k=0)

    def test_missing_doc_key_raises(self, tmp_path):
        path = tmp_path / "bad.jsonl"
        path.write_text(json.dumps({"id": "x", "topic": "y", "type": "z"}) + "\n")
        with pytest.raises(ValueError, match="missing required keys"):
            CXRRag(str(path))

    def test_malformed_json_line_raises(self, tmp_path):
        path = tmp_path / "corrupt.jsonl"
        path.write_text('{"id": "x", "topic": "y"\n')  # missing closing brace
        with pytest.raises(ValueError, match="Malformed JSON"):
            CXRRag(str(path))

    def test_non_string_text_field_raises(self, tmp_path):
        path = tmp_path / "bad_type.jsonl"
        path.write_text(json.dumps({"id": "x", "topic": "y", "type": "z", "text": 123}) + "\n")
        with pytest.raises(ValueError, match="'text' must be a string"):
            CXRRag(str(path))

    def test_question_max_length_raises(self, rag):
        with pytest.raises(ValueError, match="maximum length"):
            rag.retrieve("x" * 2001)

    def test_answer_top_k_forwarded(self, rag):
        result = rag.answer("what is this?", top_k=2)
        assert len(result["context"]) == 2

    def test_blank_lines_skipped_index_ntotal(self, tmp_path):
        path = tmp_path / "blanks2.jsonl"
        with open(path, "w") as f:
            f.write("\n")
            f.write(json.dumps(SAMPLE_DOCS[0]) + "\n")
            f.write("\n")
        r = CXRRag(str(path))
        assert r._index.ntotal == 1

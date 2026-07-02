"""Pytest-based evaluation gate: fails build if metrics fall below thresholds.

Requires Qdrant + indexed documents. Skip with: pytest -m "not eval"
"""

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.jsonl"
SAMPLE_SIZE = int(os.environ.get("EVAL_SAMPLE_SIZE", "10"))

THRESHOLDS = {
    "faithfulness": 0.85,
    "answer_relevancy": 0.80,
    "context_recall": 0.80,
}

pytestmark = pytest.mark.eval


def load_sample() -> list[dict]:
    items = []
    with open(GOLDEN_SET_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items[:SAMPLE_SIZE]


def run_pipeline_sample():
    from app.config import settings
    from app.llm.anthropic_client import AnthropicClient
    from app.llm.ollama_client import OllamaClient
    from app.query.pipeline import run_query

    if settings.llm_provider == "ollama":
        llm = OllamaClient(settings.ollama_base_url, settings.ollama_model)
    else:
        llm = AnthropicClient(settings.anthropic_api_key, settings.anthropic_model)

    items = load_sample()
    results = []
    for item in items:
        try:
            resp = run_query(item["question"], llm)
            results.append(
                {
                    "question": item["question"],
                    "answer": resp.answer,
                    "contexts": [c.text_snippet for c in resp.citations],
                    "ground_truth": item["ground_truth"],
                    "expected_source": item.get("expected_source"),
                }
            )
        except Exception as exc:
            results.append(
                {
                    "question": item["question"],
                    "answer": f"ERROR: {exc}",
                    "contexts": [],
                    "ground_truth": item["ground_truth"],
                    "expected_source": item.get("expected_source"),
                }
            )
    return results


@pytest.fixture(scope="module")
def eval_results():
    return run_pipeline_sample()


@pytest.fixture(scope="module")
def ragas_scores(eval_results):
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import answer_relevancy, context_recall, faithfulness

    data = {
        "question": [r["question"] for r in eval_results],
        "answer": [r["answer"] for r in eval_results],
        "contexts": [r["contexts"] if r["contexts"] else [""] for r in eval_results],
        "ground_truth": [r["ground_truth"] for r in eval_results],
    }
    dataset = Dataset.from_dict(data)
    scores = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_recall])
    return {
        "faithfulness": float(scores["faithfulness"]),
        "answer_relevancy": float(scores["answer_relevancy"]),
        "context_recall": float(scores["context_recall"]),
    }


@pytest.mark.eval
def test_faithfulness_threshold(ragas_scores):
    score = ragas_scores["faithfulness"]
    assert score >= THRESHOLDS["faithfulness"], (
        f"Faithfulness {score:.3f} < threshold {THRESHOLDS['faithfulness']}"
    )


@pytest.mark.eval
def test_answer_relevancy_threshold(ragas_scores):
    score = ragas_scores["answer_relevancy"]
    assert score >= THRESHOLDS["answer_relevancy"], (
        f"Answer relevancy {score:.3f} < threshold {THRESHOLDS['answer_relevancy']}"
    )


@pytest.mark.eval
def test_context_recall_threshold(ragas_scores):
    score = ragas_scores["context_recall"]
    assert score >= THRESHOLDS["context_recall"], (
        f"Context recall {score:.3f} < threshold {THRESHOLDS['context_recall']}"
    )


@pytest.mark.eval
def test_refusal_accuracy(eval_results):
    """Custom G-Eval: unanswerable questions should be refused."""
    unanswerable = [r for r in eval_results if r["expected_source"] is None]
    if not unanswerable:
        pytest.skip("No unanswerable items in this sample")

    refusals = [
        r for r in unanswerable
        if "don't have" in r["answer"].lower()
        or "not in the provided" in r["answer"].lower()
        or "cannot find" in r["answer"].lower()
    ]
    accuracy = len(refusals) / len(unanswerable)
    assert accuracy >= 0.80, (
        f"Refusal accuracy {accuracy:.2f} < 0.80. "
        f"Model answered {len(unanswerable) - len(refusals)} unanswerable questions."
    )


@pytest.mark.eval
def test_deepeval_faithfulness(eval_results):
    """DeepEval faithfulness gate."""
    try:
        from deepeval import evaluate as deepeval_evaluate
        from deepeval.metrics import FaithfulnessMetric
        from deepeval.test_case import LLMTestCase

        metric = FaithfulnessMetric(threshold=THRESHOLDS["faithfulness"])
        test_cases = [
            LLMTestCase(
                input=r["question"],
                actual_output=r["answer"],
                retrieval_context=r["contexts"] if r["contexts"] else [""],
            )
            for r in eval_results[:5]  # Sample 5 for cost
        ]
        results = deepeval_evaluate(test_cases, [metric])
        for result in results.test_results:
            assert result.success, f"DeepEval faithfulness failed: {result}"
    except ImportError:
        pytest.skip("deepeval not installed")


@pytest.mark.eval
def test_deepeval_answer_relevancy(eval_results):
    """DeepEval answer relevancy gate."""
    try:
        from deepeval import evaluate as deepeval_evaluate
        from deepeval.metrics import AnswerRelevancyMetric
        from deepeval.test_case import LLMTestCase

        metric = AnswerRelevancyMetric(threshold=THRESHOLDS["answer_relevancy"])
        test_cases = [
            LLMTestCase(
                input=r["question"],
                actual_output=r["answer"],
                retrieval_context=r["contexts"] if r["contexts"] else [""],
            )
            for r in eval_results[:5]
        ]
        results = deepeval_evaluate(test_cases, [metric])
        for result in results.test_results:
            assert result.success, f"DeepEval answer relevancy failed: {result}"
    except ImportError:
        pytest.skip("deepeval not installed")

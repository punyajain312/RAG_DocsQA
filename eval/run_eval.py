"""Run the full pipeline over the golden set and compute RAGAS + DeepEval metrics.

Usage:
    python -m eval.run_eval [--sample N] [--no-reranker] [--output eval/results.md]
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.WARNING)

GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.jsonl"
RESULTS_PATH = Path(__file__).parent / "results.md"


def load_golden_set(path: Path, sample: int | None = None) -> list[dict]:
    items = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    if sample:
        items = items[:sample]
    return items


def run_pipeline_over_golden_set(items: list[dict]) -> list[dict]:
    from app.config import settings
    from app.llm.anthropic_client import AnthropicClient
    from app.llm.ollama_client import OllamaClient
    from app.query.pipeline import run_query

    if settings.llm_provider == "ollama":
        llm = OllamaClient(settings.ollama_base_url, settings.ollama_model)
    else:
        llm = AnthropicClient(settings.anthropic_api_key, settings.anthropic_model)

    results = []
    for i, item in enumerate(items, 1):
        print(f"  [{i}/{len(items)}] {item['question'][:70]}")
        try:
            resp = run_query(item["question"], llm)
            results.append(
                {
                    "question": item["question"],
                    "answer": resp.answer,
                    "contexts": [c.text_snippet for c in resp.citations],
                    "ground_truth": item["ground_truth"],
                    "expected_source": item.get("expected_source"),
                    "retrieved_count": resp.retrieved_count,
                    "reranked_count": resp.reranked_count,
                }
            )
        except Exception as exc:
            print(f"    ERROR: {exc}")
            results.append(
                {
                    "question": item["question"],
                    "answer": f"ERROR: {exc}",
                    "contexts": [],
                    "ground_truth": item["ground_truth"],
                    "expected_source": item.get("expected_source"),
                    "retrieved_count": 0,
                    "reranked_count": 0,
                }
            )
    return results


def compute_ragas(results: list[dict]) -> dict:
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )

        data = {
            "question": [r["question"] for r in results],
            "answer": [r["answer"] for r in results],
            "contexts": [r["contexts"] if r["contexts"] else [""] for r in results],
            "ground_truth": [r["ground_truth"] for r in results],
        }
        dataset = Dataset.from_dict(data)
        score = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        )
        return {
            "faithfulness": round(float(score["faithfulness"]), 4),
            "answer_relevancy": round(float(score["answer_relevancy"]), 4),
            "context_precision": round(float(score["context_precision"]), 4),
            "context_recall": round(float(score["context_recall"]), 4),
        }
    except Exception as exc:
        print(f"  RAGAS evaluation failed: {exc}")
        return {}


def compute_refusal_accuracy(results: list[dict]) -> float:
    """Fraction of unanswerable questions correctly refused."""
    unanswerable = [r for r in results if r["expected_source"] is None]
    if not unanswerable:
        return 1.0
    refusals = [
        r for r in unanswerable
        if "don't have" in r["answer"].lower() or "not in the provided" in r["answer"].lower()
    ]
    return round(len(refusals) / len(unanswerable), 4)


def write_results_md(
    ragas_metrics: dict,
    ragas_no_reranker: dict,
    refusal_accuracy: float,
    n_total: int,
    output_path: Path,
) -> None:
    lines = [
        "# RAG DocQA — Evaluation Results\n",
        f"Total questions evaluated: {n_total}\n",
        "## Metrics\n",
        "| Metric | With Reranker | Without Reranker | Threshold |",
        "|---|---|---|---|",
    ]
    thresholds = {
        "faithfulness": 0.85,
        "answer_relevancy": 0.80,
        "context_precision": "-",
        "context_recall": 0.80,
    }
    for metric, threshold in thresholds.items():
        with_val = ragas_metrics.get(metric, "N/A")
        without_val = ragas_no_reranker.get(metric, "N/A")
        lines.append(f"| {metric} | {with_val} | {without_val} | {threshold} |")

    lines += [
        "",
        f"**Refusal accuracy (unanswerable Qs):** {refusal_accuracy}",
        "",
        "_Generated by eval/run_eval.py_",
    ]
    output_path.write_text("\n".join(lines))
    print(f"\nResults written to {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=None, help="Subset of golden set")
    parser.add_argument("--no-reranker", action="store_true")
    parser.add_argument("--output", default=str(RESULTS_PATH))
    args = parser.parse_args()

    sample = args.sample or int(os.environ.get("EVAL_SAMPLE_SIZE", 0)) or None

    items = load_golden_set(GOLDEN_SET_PATH, sample)
    print(f"\nEvaluating {len(items)} questions WITH reranker...")

    results_with = run_pipeline_over_golden_set(items)
    ragas_with = compute_ragas(results_with)

    from app.config import settings

    # Run without reranker for comparison
    print(f"\nEvaluating {len(items)} questions WITHOUT reranker...")
    original = settings.use_reranker
    settings.use_reranker = False
    results_without = run_pipeline_over_golden_set(items)
    settings.use_reranker = original
    ragas_without = compute_ragas(results_without)

    refusal_acc = compute_refusal_accuracy(results_with)

    print("\n=== RAGAS Results (with reranker) ===")
    for k, v in ragas_with.items():
        print(f"  {k}: {v}")
    print("\n=== RAGAS Results (without reranker) ===")
    for k, v in ragas_without.items():
        print(f"  {k}: {v}")
    print(f"\nRefusal accuracy: {refusal_acc}")

    write_results_md(ragas_with, ragas_without, refusal_acc, len(items), Path(args.output))
    return ragas_with, refusal_acc


if __name__ == "__main__":
    main()

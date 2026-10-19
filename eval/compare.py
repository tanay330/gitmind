"""Combine several evaluation runs and compare them.

Usage:
    uv run python eval/compare.py v1=v1_metrics+h_v1 g2=s_g2+sh_g2

Each argument is NAME=result1+result2, where the results are file names
in eval/results (without .json). Their questions are pooled together.
"""
import json
import sys
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / "results"


def load(label: str) -> dict:
    with open(RESULTS_DIR / f"{label}.json", encoding="utf-8") as f:
        run = json.load(f)
    if run["questions"] and "first_rank" not in run["questions"][0]:
        raise SystemExit(f"{label} has no rank data; re-run it with the current run_eval.py")
    return run


def summarize(labels: list[str]) -> dict:
    questions = []
    foreign_weighted = 0.0
    foreign_known = 0

    for label in labels:
        run = load(label)
        questions.extend(run["questions"])
        if run.get("foreign_chunk_rate") is not None:
            foreign_weighted += run["foreign_chunk_rate"] * len(run["questions"])
            foreign_known += len(run["questions"])

    n = len(questions)
    ranks = [q["first_rank"] for q in questions]
    return {
        "n": n,
        "hit8": sum(1 for q in questions if q["hit"]) / n,
        "hit3": sum(1 for r in ranks if r and r <= 3) / n,
        "mrr": sum(1 / r for r in ranks if r) / n,
        "recall": sum(q["file_recall"] for q in questions) / n,
        "foreign": foreign_weighted / foreign_known if foreign_known else None,
    }


def main(args: list[str]) -> None:
    rows = {}
    for arg in args:
        name, labels = arg.split("=", 1)
        rows[name] = summarize(labels.split("+"))

    print(f"{'setting':10} {'n':>3} {'Hit@8':>7} {'Hit@3':>7} {'MRR':>6} {'recall':>7} {'other repos':>12}")
    for name, s in rows.items():
        foreign = f"{s['foreign']:.0%}" if s["foreign"] is not None else "-"
        print(
            f"{name:10} {s['n']:>3} {s['hit8']:>7.0%} {s['hit3']:>7.0%} "
            f"{s['mrr']:>6.3f} {s['recall']:>7.0%} {foreign:>12}"
        )


if __name__ == "__main__":
    main(sys.argv[1:])
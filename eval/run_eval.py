"""Retrieval evaluation.

Usage:
    uv run python eval/run_eval.py v1_baseline          # short summary
    uv run python eval/run_eval.py v1_baseline gm-09    # also show retrieved chunks for gm-09
"""
import contextlib
import io
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

from gitmind.retrieval.router import search

ROOT = Path(__file__).resolve().parent
QUESTIONS_FILE = ROOT / "questions.yaml"
RESULTS_DIR = ROOT / "results"
TOP_K = 8
PREVIEW_CHARS = 90


def load_questions(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_repo(url: str | None) -> str | None:
    if not url:
        return None
    url = url.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    return url.lower()


def short_repo(repo: str | None) -> str:
    return repo.split("github.com/")[-1] if repo else "?"


def preview(text: str) -> str:
    return " ".join(text.split())[:PREVIEW_CHARS]


def run(label: str, show_ids: set[str]) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    questions = load_questions(QUESTIONS_FILE)

    per_style = defaultdict(lambda: {"hits": 0, "total": 0})
    details = []
    total_hits = 0
    recall_sum = 0.0
    foreign = 0
    checked = 0

    for q in questions:
        wanted_repo = normalize_repo(q["repo"])

        # v1's search() prints a lot of debug text; hide it during evaluation
        with contextlib.redirect_stdout(io.StringIO()):
            results = search(q["question"], top_k=TOP_K)

        retrieved = []
        for r in results:
            repo = normalize_repo(r.payload.get("repo_url"))
            retrieved.append(
                {
                    "repo": repo,
                    "path": r.payload["path"],
                    "text": preview(r.payload.get("text", "")),
                }
            )
            if repo is not None:
                checked += 1
                if repo != wanted_repo:
                    foreign += 1

        found = [
            f
            for f in q["expected_files"]
            if any(
                item["path"] == f
                and (item["repo"] is None or item["repo"] == wanted_repo)
                for item in retrieved
            )
        ]
        hit = len(found) > 0
        file_recall = len(found) / len(q["expected_files"])

        total_hits += hit
        recall_sum += file_recall
        per_style[q["style"]]["total"] += 1
        per_style[q["style"]]["hits"] += hit
        details.append(
            {
                "id": q["id"],
                "question": q["question"],
                "style": q["style"],
                "hit": hit,
                "file_recall": file_recall,
                "retrieved": retrieved,
            }
        )

        # one short line per question
        status = "OK  " if file_recall == 1 else ("PART" if hit else "MISS")
        print(f"{q['id']:7} {status} recall {file_recall:4.0%}  {q['style']:9} {q['question']}")
        if file_recall < 1:
            missing = [f for f in q["expected_files"] if f not in found]
            print(f"        missing: {missing}")

        # detailed view only for the questions you ask about
        if q["id"] in show_ids:
            for rank, item in enumerate(retrieved, start=1):
                mark = "*" if item["path"] in q["expected_files"] else " "
                print(
                    f"        {rank}.{mark} {short_repo(item['repo'])} | "
                    f"{item['path']} | {item['text']!r}"
                )

    total = len(questions)
    print(f"\n=== {label} ===")
    print(f"Overall Hit@{TOP_K}: {total_hits}/{total} = {total_hits / total:.0%}")
    print(f"Avg file recall: {recall_sum / total:.0%}")
    for style, s in per_style.items():
        print(f"  {style}: {s['hits']}/{s['total']} = {s['hits'] / s['total']:.0%}")
    if checked:
        print(f"Chunks from other repos: {foreign}/{checked} = {foreign / checked:.0%}")

    out = {
        "label": label,
        "top_k": TOP_K,
        "hit_rate": total_hits / total,
        "avg_file_recall": recall_sum / total,
        "by_style": {s: v["hits"] / v["total"] for s, v in per_style.items()},
        "foreign_chunk_rate": (foreign / checked) if checked else None,
        "questions": details,
    }
    with open(RESULTS_DIR / f"{label}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    run(label, set(sys.argv[2:]))
"""Retrieval evaluation.

Usage:
    uv run python eval/run_eval.py v1_baseline                          # v1 search
    uv run python eval/run_eval.py run4 --v2                            # v2 search
    uv run python eval/run_eval.py run4 --v2 --guarantee=2 gm-01 gm-14  # options, and show chunks for two questions
    uv run python eval/run_eval.py run3 --v2 --rerank                   # with reranking
"""
import contextlib
import io
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
QUESTIONS_FILE = ROOT / "questions.yaml"
RESULTS_DIR = ROOT / "results"
TOP_K = 8
PREVIEW_CHARS = 90


def load_questions(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_repo(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().rstrip("/")
    if value.endswith(".git"):
        value = value[:-4]
    value = value.lower()
    for prefix in ("https://github.com/", "http://github.com/", "https://www.github.com/"):
        if value.startswith(prefix):
            value = value[len(prefix):]
    return value


def preview(text: str) -> str:
    return " ".join(text.split())[:PREVIEW_CHARS]


def parse_args(argv: list[str]):
    engine = "v1"
    options = {}
    positional = []
    for arg in argv:
        if arg == "--v2":
            engine = "v2"
        elif arg == "--rerank":
            options["use_rerank"] = True
        elif arg.startswith("--guarantee="):
            options["guarantee"] = int(arg.split("=", 1)[1])
        else:
            positional.append(arg)
    label = positional[0] if positional else "run"
    return label, engine, options, set(positional[1:])


def make_search(engine: str, options: dict):
    if engine == "v2":
        from gitmind.indexing.github_client import parse_repo_url
        from gitmind.models import make_repo_id
        from gitmind.retrieval.search import search as search_v2

        def run_search(q: dict):
            owner, repo = parse_repo_url(q["repo"])
            return search_v2(
                q["question"], make_repo_id(owner, repo), top_k=TOP_K, **options
            )

        return run_search

    from gitmind.retrieval.router import search as search_v1

    return lambda q: search_v1(q["question"], top_k=TOP_K)


def run(label: str, engine: str, options: dict, show_ids: set[str]) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    questions = load_questions(QUESTIONS_FILE)
    run_search = make_search(engine, options)

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
            results = run_search(q)

        retrieved = []
        for r in results:
            repo = normalize_repo(r.payload.get("repo_id") or r.payload.get("repo_url"))
            start, end = r.payload.get("start_line"), r.payload.get("end_line")
            where = f"{r.payload['path']}:{start}-{end}" if start else r.payload["path"]
            retrieved.append(
                {
                    "repo": repo,
                    "path": r.payload["path"],
                    "where": where,
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

        status = "OK  " if file_recall == 1 else ("PART" if hit else "MISS")
        print(f"{q['id']:7} {status} recall {file_recall:4.0%}  {q['style']:9} {q['question']}")
        if file_recall < 1:
            missing = [f for f in q["expected_files"] if f not in found]
            print(f"        missing: {missing}")

        if q["id"] in show_ids:
            for rank, item in enumerate(retrieved, start=1):
                mark = "*" if item["path"] in q["expected_files"] else " "
                print(f"        {rank}.{mark} {item['repo']} | {item['where']} | {item['text']!r}")

    total = len(questions)
    settings_text = "".join(f" {key}={value}" for key, value in options.items())
    print(f"\n=== {label} ({engine}{settings_text}) ===")
    print(f"Overall Hit@{TOP_K}: {total_hits}/{total} = {total_hits / total:.0%}")
    print(f"Avg file recall: {recall_sum / total:.0%}")
    for style, s in per_style.items():
        print(f"  {style}: {s['hits']}/{s['total']} = {s['hits'] / s['total']:.0%}")
    if checked:
        print(f"Chunks from other repos: {foreign}/{checked} = {foreign / checked:.0%}")

    out = {
        "label": label,
        "engine": engine,
        "options": options,
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
    label, engine, options, show_ids = parse_args(sys.argv[1:])
    run(label, engine, options, show_ids)
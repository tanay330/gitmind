import re

RRF_K = 60


def strip_repo_name(question: str, repo_id: str) -> str:
    repo_name = repo_id.split("/")[-1]
    cleaned = re.sub(rf"\b{re.escape(repo_name)}\b", " ", question, flags=re.IGNORECASE)
    cleaned = " ".join(cleaned.split())
    return cleaned if len(cleaned.split()) >= 2 else question


def reciprocal_rank_fusion(result_lists, k: int = RRF_K):
    scores = {}
    points = {}

    for results in result_lists:
        for rank, point in enumerate(results, start=1):
            scores[point.id] = scores.get(point.id, 0.0) + 1.0 / (k + rank)
            points[point.id] = point

    ranked_ids = sorted(scores, key=scores.get, reverse=True)
    return [(points[point_id], scores[point_id]) for point_id in ranked_ids]


def merge_with_guarantee(fused, dense, sparse, top_k: int, guarantee: int):
    chosen = []
    seen = set()

    def add(point):
        if point.id not in seen and len(chosen) < top_k:
            seen.add(point.id)
            chosen.append(point)

    for point in dense[:guarantee] + sparse[:guarantee]:
        add(point)
    for point in fused:
        add(point)
    return chosen
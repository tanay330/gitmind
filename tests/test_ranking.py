from types import SimpleNamespace

from gitmind.retrieval.ranking import (
    merge_with_guarantee,
    reciprocal_rank_fusion,
    strip_repo_name,
)


def point(point_id):
    return SimpleNamespace(id=point_id)


def ids(points):
    return [p.id for p in points]


def test_rrf_rewards_chunks_found_by_both_lists():
    dense = [point("a"), point("b"), point("c")]
    sparse = [point("c"), point("b"), point("d")]

    fused = reciprocal_rank_fusion([dense, sparse])

    assert ids([p for p, _ in fused]) == ["c", "b", "a", "d"]


def test_rrf_returns_each_chunk_once():
    fused = reciprocal_rank_fusion([[point("a"), point("b")], [point("b"), point("a")]])
    assert len(fused) == 2


def test_guarantee_keeps_top_results_of_each_list():
    fused = [point(i) for i in "abcdef"]
    dense = [point("x"), point("y")]
    sparse = [point("z"), point("a")]

    chosen = merge_with_guarantee(fused, dense, sparse, top_k=5, guarantee=2)

    assert ids(chosen) == ["x", "y", "z", "a", "b"]


def test_guarantee_zero_returns_plain_fusion_order():
    fused = [point(i) for i in "abcdef"]
    chosen = merge_with_guarantee(fused, [point("x")], [point("y")], top_k=3, guarantee=0)
    assert ids(chosen) == ["a", "b", "c"]


def test_merge_never_exceeds_top_k_or_repeats_chunks():
    fused = [point(i) for i in "abc"]
    chosen = merge_with_guarantee(fused, fused, fused, top_k=2, guarantee=3)
    assert ids(chosen) == ["a", "b"]


def test_strip_repo_name_removes_the_name_ignoring_case():
    assert strip_repo_name("Which model does GitMind use?", "tanay330/gitmind") == "Which model does use?"


def test_strip_repo_name_keeps_question_if_too_little_is_left():
    assert strip_repo_name("gitmind", "tanay330/gitmind") == "gitmind"


def test_strip_repo_name_only_matches_whole_words():
    assert strip_repo_name("Is gitminder good?", "tanay330/gitmind") == "Is gitminder good?"
    assert strip_repo_name("what is bxc", "a/b.c") == "what is bxc"
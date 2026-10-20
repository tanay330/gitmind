from gitmind.api.jobs import fail_stale_jobs, finish_job, get_job, is_indexing, start_job, update_job


def test_start_job_creates_a_queued_job():
    job, created = start_job("me/demo")
    assert created is True
    assert job["status"] == "queued"


def test_second_start_returns_the_active_job():
    first, _ = start_job("me/demo")
    second, created = start_job("me/demo")
    assert created is False
    assert second["job_id"] == first["job_id"]


def test_finished_job_allows_a_new_job_and_keeps_its_results():
    first, _ = start_job("me/demo")
    finish_job(first["job_id"], status="ready", files_indexed=3, chunks_stored=9)

    second, created = start_job("me/demo")
    stored = get_job(first["job_id"])

    assert created is True
    assert second["job_id"] != first["job_id"]
    assert (stored["status"], stored["files_indexed"], stored["chunks_stored"]) == ("ready", 3, 9)
    assert stored["finished_at"] is not None


def test_is_indexing_tracks_active_jobs():
    assert is_indexing("me/demo") is False
    job, _ = start_job("me/demo")
    assert is_indexing("me/demo") is True
    finish_job(job["job_id"], status="ready")
    assert is_indexing("me/demo") is False


def test_stale_jobs_are_marked_failed():
    job, _ = start_job("me/demo")
    update_job(job["job_id"], status="indexing")

    assert fail_stale_jobs() == 1

    stored = get_job(job["job_id"])
    assert stored["status"] == "failed"
    assert "restarted" in stored["detail"]
    assert is_indexing("me/demo") is False


def test_unknown_job_is_none():
    assert get_job("does-not-exist") is None
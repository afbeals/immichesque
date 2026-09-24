import os
import time

from app import expiry


def _touch(path, days_old):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x")
    old_time = time.time() - (days_old * 86400)
    os.utime(path, (old_time, old_time))


def test_expired_file_outside_keep_is_found(tmp_path):
    staging = tmp_path / "review_staging"
    old_file = staging / "user-1" / "photo.jpg"
    _touch(old_file, days_old=8)

    expired = expiry.find_expired_files(staging_dir=staging, retention_days=7)

    assert expired == [old_file]


def test_recent_file_is_not_expired(tmp_path):
    staging = tmp_path / "review_staging"
    recent_file = staging / "user-1" / "photo.jpg"
    _touch(recent_file, days_old=3)

    expired = expiry.find_expired_files(staging_dir=staging, retention_days=7)

    assert expired == []


def test_file_exactly_at_retention_boundary_is_not_yet_expired(tmp_path):
    staging = tmp_path / "review_staging"
    boundary_file = staging / "user-1" / "photo.jpg"
    now = time.time()
    boundary_file.parent.mkdir(parents=True)
    boundary_file.write_bytes(b"x")
    seven_days_ago = now - (7 * 86400)
    os.utime(boundary_file, (seven_days_ago, seven_days_ago))

    # `now` is pinned explicitly here so the comparison isn't racing the
    # real clock between when the file's mtime is set and when the
    # function runs -- otherwise this test is flaky by a few milliseconds.
    expired = expiry.find_expired_files(staging_dir=staging, retention_days=7, now=now)

    assert expired == []


def test_kept_file_is_never_expired_even_if_old(tmp_path):
    staging = tmp_path / "review_staging"
    kept_file = staging / "user-1" / "keep" / "photo.jpg"
    _touch(kept_file, days_old=30)

    expired = expiry.find_expired_files(staging_dir=staging, retention_days=7)

    assert expired == []


def test_missing_staging_directory_returns_no_expired_files(tmp_path):
    missing = tmp_path / "does-not-exist"

    expired = expiry.find_expired_files(staging_dir=missing, retention_days=7)

    assert expired == []


def test_sweep_deletes_expired_and_leaves_kept_and_recent(tmp_path):
    staging = tmp_path / "review_staging"
    expired_file = staging / "user-1" / "old.jpg"
    kept_file = staging / "user-1" / "keep" / "old.jpg"
    recent_file = staging / "user-1" / "new.jpg"
    _touch(expired_file, days_old=10)
    _touch(kept_file, days_old=10)
    _touch(recent_file, days_old=1)

    deleted = expiry.sweep(staging_dir=staging, retention_days=7)

    assert deleted == [expired_file]
    assert not expired_file.exists()
    assert kept_file.exists()
    assert recent_file.exists()


def test_sweep_dry_run_reports_without_deleting(tmp_path):
    staging = tmp_path / "review_staging"
    expired_file = staging / "user-1" / "old.jpg"
    _touch(expired_file, days_old=10)

    deleted = expiry.sweep(staging_dir=staging, retention_days=7, dry_run=True)

    assert deleted == [expired_file]
    assert expired_file.exists()

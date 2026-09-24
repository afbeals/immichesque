"""Daily sweep: delete review-staging duplicates older than RETENTION_DAYS.

This script only ever touches REVIEW_STAGING_DIR -- it never talks to
Immich's API and never touches Immich's own managed library folder. Files
under a `keep/` subdirectory anywhere in their path are never deleted,
regardless of age; that's the manual "prevent deletion" override.
"""

import logging
import time
from pathlib import Path

from . import config

logger = logging.getLogger(__name__)


def is_kept(path, staging_root):
    try:
        relative = path.relative_to(staging_root)
    except ValueError:
        return False
    return config.KEEP_SUBDIR_NAME in relative.parts


def find_expired_files(staging_dir=None, retention_days=None, now=None):
    staging_root = Path(staging_dir or config.REVIEW_STAGING_DIR)
    retention_days = retention_days if retention_days is not None else config.RETENTION_DAYS
    now = now if now is not None else time.time()
    cutoff = now - (retention_days * 86400)

    if not staging_root.exists():
        return []

    expired = []
    for path in sorted(staging_root.rglob("*")):
        if not path.is_file():
            continue
        if is_kept(path, staging_root):
            continue
        if path.stat().st_mtime < cutoff:
            expired.append(path)
    return expired


def sweep(staging_dir=None, retention_days=None, now=None, dry_run=False):
    expired = find_expired_files(staging_dir=staging_dir, retention_days=retention_days, now=now)
    for path in expired:
        logger.info("expiring review-staging duplicate: %s", path)
        if not dry_run:
            path.unlink()
    return expired


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sweep()

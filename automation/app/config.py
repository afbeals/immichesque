import os

IMMICH_API_URL = os.environ.get("IMMICH_API_URL", "http://immich-server:2283/api")
IMMICH_API_KEY = os.environ.get("IMMICH_API_KEY", "")
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID", "")
WEBHOOK_SHARED_SECRET = os.environ.get("WEBHOOK_SHARED_SECRET", "")
REVIEW_STAGING_DIR = os.environ.get("REVIEW_STAGING_DIR", "/review_staging")
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "7"))

# Files under a directory with this name (anywhere in their path, under a
# given owner's staging folder) are never auto-expired by expiry.py.
KEEP_SUBDIR_NAME = "keep"

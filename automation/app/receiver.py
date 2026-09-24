"""Webhook receiver for Immich's `Asset Created` Workflow trigger.

Copies files uploaded by non-admin users into a review-staging directory
so they can be auto-expired later by expiry.py, without the automation
service ever reading from or writing to Immich's own managed library
folder directly.
"""

import logging
from pathlib import Path

import requests
from flask import Flask, jsonify, request

from . import config

logger = logging.getLogger(__name__)


def fetch_asset(asset_id, api_url=None, api_key=None, session=None):
    api_url = api_url or config.IMMICH_API_URL
    api_key = api_key or config.IMMICH_API_KEY
    session = session or requests
    response = session.get(
        f"{api_url}/assets/{asset_id}",
        headers={"x-api-key": api_key},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def download_asset_original(asset_id, api_url=None, api_key=None, session=None):
    api_url = api_url or config.IMMICH_API_URL
    api_key = api_key or config.IMMICH_API_KEY
    session = session or requests
    response = session.get(
        f"{api_url}/assets/{asset_id}/original",
        headers={"x-api-key": api_key},
        timeout=60,
    )
    response.raise_for_status()
    return response.content


def copy_to_review_staging(owner_id, filename, content, staging_dir=None):
    staging_root = Path(staging_dir or config.REVIEW_STAGING_DIR)
    dest_dir = staging_root / owner_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename
    # Intentionally not preserving any original timestamp: the copy's
    # mtime becomes "now", which is exactly what expiry.py measures the
    # 7-day retention window against.
    dest_path.write_bytes(content)
    return dest_path


def handle_asset_create(payload, staging_dir=None, api_url=None, api_key=None, session=None):
    """Process one `Asset Created` webhook payload.

    Returns a dict describing what happened, for logging and testing.

    NOTE: as of writing, Immich's webhook payload schema for this trigger
    isn't fully confirmed against official documentation. This function
    accepts either `assetId` or `id`, and either `ownerId` or `userId`,
    falling back to a GET /assets/{id} lookup when the owner isn't present
    in the payload at all. Verify the real payload shape against your own
    instance -- see docs/TROUBLESHOOTING.md.
    """
    asset_id = payload.get("assetId") or payload.get("id")
    owner_id = payload.get("ownerId") or payload.get("userId")

    if not asset_id:
        return {"action": "skipped", "reason": "no asset id in payload"}

    asset = None
    if owner_id is None:
        asset = fetch_asset(asset_id, api_url=api_url, api_key=api_key, session=session)
        owner_id = asset.get("ownerId")

    if owner_id == config.ADMIN_USER_ID:
        return {"action": "skipped", "reason": "uploaded by admin", "assetId": asset_id}

    if asset is None:
        asset = fetch_asset(asset_id, api_url=api_url, api_key=api_key, session=session)

    filename = asset.get("originalFileName") or asset_id
    content = download_asset_original(asset_id, api_url=api_url, api_key=api_key, session=session)
    dest_path = copy_to_review_staging(owner_id, filename, content, staging_dir=staging_dir)

    return {
        "action": "copied",
        "assetId": asset_id,
        "ownerId": owner_id,
        "path": str(dest_path),
    }


def create_app():
    app = Flask(__name__)

    @app.post("/webhook")
    def webhook():
        secret = request.headers.get("X-Webhook-Secret", "")
        if config.WEBHOOK_SHARED_SECRET and secret != config.WEBHOOK_SHARED_SECRET:
            return jsonify({"error": "unauthorized"}), 401

        payload = request.get_json(silent=True) or {}
        result = handle_asset_create(payload)
        logger.info("processed webhook payload: %s", result)
        return jsonify(result), 200

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"}), 200

    return app


app = create_app()

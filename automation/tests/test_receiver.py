from unittest.mock import MagicMock

from app import receiver


def _fake_session(asset_json, content=b"fake-bytes"):
    """A fake requests-like session: GET .../assets/{id} returns asset_json,
    GET .../assets/{id}/original returns `content`."""
    session = MagicMock()

    def get(url, headers=None, timeout=None):
        response = MagicMock()
        response.raise_for_status = MagicMock()
        if url.endswith("/original"):
            response.content = content
        else:
            response.json.return_value = asset_json
        return response

    session.get.side_effect = get
    return session


def test_admin_upload_is_skipped(monkeypatch, tmp_path):
    monkeypatch.setattr(receiver.config, "ADMIN_USER_ID", "admin-1")
    session = _fake_session({"ownerId": "admin-1", "originalFileName": "a.jpg"})

    result = receiver.handle_asset_create(
        {"assetId": "asset-1", "ownerId": "admin-1"},
        staging_dir=tmp_path,
        session=session,
    )

    assert result["action"] == "skipped"
    assert list(tmp_path.rglob("*")) == []


def test_non_admin_upload_is_copied_to_owner_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(receiver.config, "ADMIN_USER_ID", "admin-1")
    session = _fake_session(
        {"ownerId": "user-2", "originalFileName": "family.jpg"}, content=b"hello"
    )

    result = receiver.handle_asset_create(
        {"assetId": "asset-2", "ownerId": "user-2"},
        staging_dir=tmp_path,
        session=session,
    )

    assert result["action"] == "copied"
    dest = tmp_path / "user-2" / "family.jpg"
    assert dest.read_bytes() == b"hello"


def test_missing_owner_in_payload_is_looked_up_via_api(monkeypatch, tmp_path):
    monkeypatch.setattr(receiver.config, "ADMIN_USER_ID", "admin-1")
    session = _fake_session({"ownerId": "user-3", "originalFileName": "b.jpg"}, content=b"data")

    result = receiver.handle_asset_create(
        {"assetId": "asset-3"},
        staging_dir=tmp_path,
        session=session,
    )

    assert result["action"] == "copied"
    assert result["ownerId"] == "user-3"
    assert (tmp_path / "user-3" / "b.jpg").exists()


def test_missing_asset_id_is_skipped(tmp_path):
    result = receiver.handle_asset_create({}, staging_dir=tmp_path)

    assert result["action"] == "skipped"
    assert list(tmp_path.rglob("*")) == []


def test_asset_with_no_original_filename_falls_back_to_asset_id(monkeypatch, tmp_path):
    monkeypatch.setattr(receiver.config, "ADMIN_USER_ID", "admin-1")
    session = _fake_session({"ownerId": "user-4"}, content=b"data")

    result = receiver.handle_asset_create(
        {"assetId": "asset-4", "ownerId": "user-4"},
        staging_dir=tmp_path,
        session=session,
    )

    assert result["action"] == "copied"
    assert (tmp_path / "user-4" / "asset-4").exists()


def test_webhook_route_rejects_missing_or_wrong_secret(monkeypatch):
    monkeypatch.setattr(receiver.config, "WEBHOOK_SHARED_SECRET", "correct-secret")
    app = receiver.create_app()
    client = app.test_client()

    no_header = client.post("/webhook", json={})
    wrong_header = client.post("/webhook", json={}, headers={"X-Webhook-Secret": "wrong"})

    assert no_header.status_code == 401
    assert wrong_header.status_code == 401


def test_webhook_route_accepts_correct_secret(monkeypatch):
    monkeypatch.setattr(receiver.config, "WEBHOOK_SHARED_SECRET", "correct-secret")
    monkeypatch.setattr(receiver.config, "ADMIN_USER_ID", "admin-1")
    app = receiver.create_app()
    client = app.test_client()

    response = client.post(
        "/webhook",
        json={"assetId": "asset-1", "ownerId": "admin-1"},
        headers={"X-Webhook-Secret": "correct-secret"},
    )

    assert response.status_code == 200
    assert response.get_json()["action"] == "skipped"


def test_webhook_route_allows_any_secret_when_none_configured(monkeypatch):
    monkeypatch.setattr(receiver.config, "WEBHOOK_SHARED_SECRET", "")
    monkeypatch.setattr(receiver.config, "ADMIN_USER_ID", "admin-1")
    app = receiver.create_app()
    client = app.test_client()

    response = client.post("/webhook", json={"assetId": "asset-1", "ownerId": "admin-1"})

    assert response.status_code == 200


def test_healthz():
    app = receiver.create_app()
    client = app.test_client()

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

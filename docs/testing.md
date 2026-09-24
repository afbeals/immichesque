# Testing

The automation service (`automation/`) has a pytest suite covering both scripts:

- `automation/tests/test_receiver.py` -- the webhook handler: admin uploads are skipped, non-admin uploads are copied to the right path, a missing owner in the payload is looked up via the Immich API, the shared-secret check on the HTTP route
- `automation/tests/test_expiry.py` -- the sweep: files past the retention window are found and deleted, recent files are left alone, anything under a `keep/` subfolder is never deleted regardless of age, dry-run mode reports without deleting

No Docker or a running Immich instance is required -- Immich's API is mocked, and filesystem operations run against pytest's `tmp_path` fixture.

## Running the suite

```bash
cd automation
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest -v
```

## What isn't covered by these tests

This is infrastructure/config work, not just application code -- the Docker Compose wiring, the Cloudflare Tunnel, and the Unraid drive mounting have no automated tests. Those are verified manually via the end-to-end checks in [01-drive-setup.md](01-drive-setup.md), [03-tunnel-setup.md](03-tunnel-setup.md), and [04-automation-setup.md](04-automation-setup.md) step 5.

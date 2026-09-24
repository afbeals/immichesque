# 4. Automation setup

Covers the one genuinely custom piece of this project: a service that backs up anything a non-admin user uploads into a review-staging area, and auto-expires those copies after a retention window unless you explicitly keep them. The original inside Immich is never touched by this -- see [docs/README.md](README.md#design-decisions-worth-knowing-before-you-read-further) for why.

The service lives in `automation/` and runs as one Docker container (`media-automation` in `immich/docker-compose.override.yml`) with two jobs:

- a small Flask app that Immich calls via webhook on every upload (the **receiver**, `automation/app/receiver.py`)
- a daily cron job that deletes expired review-staging copies (the **sweep**, `automation/app/expiry.py`)

## 1. Generate an Immich API key

Log in as admin → **Account Settings → API Keys → New API Key**. Grant at least asset read access. Put it in `automation.env` as `IMMICH_API_KEY`.

## 2. Fill in the rest of `automation.env`

If you haven't already from [03-tunnel-setup.md](03-tunnel-setup.md):

```bash
cd immich
cp automation.env.example automation.env   # skip if you already did this in 03-tunnel-setup.md
```

Set:

- `ADMIN_USER_ID` -- from [02-immich-setup.md, step 5](02-immich-setup.md)
- `IMMICH_API_KEY` -- from step 1 above
- `WEBHOOK_SHARED_SECRET` -- make up any random string; this is checked on every incoming webhook request so nothing else on your network can POST fake events at the receiver

## 3. Start the automation container

```bash
docker compose up -d media-automation
```

Confirm it's healthy:

```bash
curl http://localhost:5000/healthz
```

## 4. Configure Immich's Workflow

**Immich requires v3.0.0 or later for this** -- Workflows shipped alongside that release (June 2026). Check your version under Account Settings → About if unsure, and upgrade first if needed.

In Immich's web UI: **Utilities → Workflows → Create workflow**

- **Trigger**: `Asset Created`
- **Action**: `Trigger Webhook`
  - URL: `http://media-automation:5000/webhook`
  - Method: `POST`
  - Header: `X-Webhook-Secret: <the same value as WEBHOOK_SHARED_SECRET>`

Save and enable the workflow.

> **Unverified against Immich's documented schema:** as of writing, the exact fields in the webhook's JSON payload aren't fully documented anywhere confirmable. `automation/app/receiver.py` accepts either `assetId`/`id` and `ownerId`/`userId`, and falls back to calling Immich's `GET /assets/{id}` API to look up the owner if it's missing from the payload -- but **verify this against what your instance actually sends** before trusting step 5 below. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#inspecting-the-actual-webhook-payload).

## 5. End-to-end test

1. Log in as a **non-admin** test user and upload a photo.
2. Watch the receiver's logs: `docker compose logs -f media-automation`
3. Confirm a copy landed at `/mnt/disks/media_drive/review_staging/<owner-id>/<filename>`.
4. Log in as **admin** and upload a photo -- confirm nothing appears in `review_staging/` for it (admin uploads are always skipped).
5. To test the "keep" override, move a copied file into a `keep/` subfolder under its owner's staging directory -- the sweep never deletes anything under a `keep/` path, regardless of age.
6. To test expiry without waiting 7 real days, back-date a test file's modification time and run the sweep manually:

```bash
docker compose exec media-automation touch -d "8 days ago" /review_staging/<owner-id>/test.jpg
docker compose exec media-automation python -m app.expiry
```

Confirm the back-dated file is gone, and anything under `keep/` or newer than 7 days survives.

## Next

Continue to [05-face-grouping.md](05-face-grouping.md) to validate face grouping against a real photo batch, or [testing.md](testing.md) to run the automation service's own test suite.

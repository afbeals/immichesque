# Troubleshooting

Specific issues worth knowing about, not generic advice.

## Inspecting the actual webhook payload

Since Immich's webhook payload schema for `Asset Created` isn't fully confirmed against documentation (see [04-automation-setup.md](04-automation-setup.md)), the fastest way to check it against your actual instance:

```bash
docker compose logs -f media-automation
```

Trigger a test upload, then look at the logged `result` dict from `handle_asset_create` in `automation/app/receiver.py` -- or temporarily add `logger.info("raw payload: %s", payload)` at the top of the `/webhook` route in that file to see the exact JSON Immich sent, before it's been picked apart by the field-name guesses in the code.

## `media-automation` / `cloudflared` fail to start on first `docker compose up -d`

Expected if you haven't created `automation.env` yet (see [02-immich-setup.md](02-immich-setup.md) step 2 and [03-tunnel-setup.md](03-tunnel-setup.md) step 4) -- both services depend on variables from that file. Bring up just the core Immich services first (`docker compose up -d immich-server immich-machine-learning redis database`), then start the rest once `automation.env` exists.

## `${REVIEW_STAGING_LOCATION}` is empty / volume mount fails

This variable must be set in `.env` (the plain file Compose auto-loads for `${VAR}` substitution in the compose files), not in `automation.env` (an `env_file:` that only injects runtime environment variables into specific containers). See the gotcha in [02-immich-setup.md](02-immich-setup.md) step 1.

## `media-automation` can't reach Immich (`Connection refused` / name doesn't resolve)

Both services need to be part of the same Compose project so they share a Docker network. Bring everything up from the `immich/` directory with a single `docker compose up -d` -- Compose automatically merges `docker-compose.override.yml` alongside `docker-compose.yml` in the same directory, so a bare `docker compose up -d` (no `-f` flags needed) includes both. If you've split them into separate `docker compose` invocations from different directories, they'll end up on separate networks and won't be able to reach each other by service name.

## Unassigned Devices mount path changed after a drive swap

See the gotcha in [01-drive-setup.md](01-drive-setup.md) step 3 -- rename the drive to a fixed name in the Unassigned Devices UI so its mount path is stable across swaps, rather than relying on the auto-generated name.

## cron doesn't appear to be running inside `media-automation`

`entrypoint.sh` starts `cron` in the background before `exec`-ing the Flask/gunicorn process as PID 1. If you don't see the daily sweep's log lines, confirm the container is actually still running (`docker compose ps`) rather than having restarted, since a crashed-and-restarted container starts a fresh `cron` too -- and check that `/etc/cron.d/media-automation` was installed correctly at build time (rebuild with `docker compose build media-automation` if you've edited `automation/cron/crontab`).

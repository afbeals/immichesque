# 2. Immich setup

Covers deploying Immich's official Docker Compose stack against the drive from [01-drive-setup.md](01-drive-setup.md), first login, and creating accounts.

This repo vendors Immich's actual official `docker-compose.yml` and `example.env` unmodified in `immich/` (fetched from `https://github.com/immich-app/immich/releases/latest/download/`), so upstream updates stay a clean diff against our copy. Everything this project adds lives in `immich/docker-compose.override.yml` and the two `*.env.example` files, which Compose merges in automatically.

## 1. Point Immich at the drive

```bash
cd immich
cp example.env .env
```

Edit `.env`:

- `UPLOAD_LOCATION=/mnt/disks/media_drive/immich_library`
- `DB_DATA_LOCATION` -- Immich's Postgres data. Keep this on the Unraid boot/cache drive (an SSD), not the external HDD -- `example.env`'s own comment warns network shares aren't supported here, and a spinning USB drive is a poor fit for database I/O regardless.
- `DB_PASSWORD` -- change from the default.

Then append this project's one extra variable (used by `docker-compose.override.yml`'s volume mount, not by Immich itself):

```bash
cat immichesque.env.example >> .env
```

and set `REVIEW_STAGING_LOCATION=/mnt/disks/media_drive/review_staging` in `.env`.

> **Gotcha:** `REVIEW_STAGING_LOCATION` has to live in `.env` specifically, not in `automation.env` (from [04-automation-setup.md](04-automation-setup.md)). Compose only reads the plain `.env` file in the working directory for `${VAR}` substitution inside the compose files themselves; `env_file:` entries only inject variables into a container's runtime environment and can't fill in a volume path in the compose file itself.

## 2. Bring up the core stack

```bash
docker compose up -d
```

This starts `immich-server`, `immich-machine-learning`, `redis`, and `database`. The `media-automation` and `cloudflared` services from the override file will fail to start at this point since they depend on values from `automation.env`, which doesn't exist yet -- that's expected; ignore errors from those two for now (see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)).

Confirm the core stack is healthy:

```bash
docker compose ps
```

## 3. First login and account creation

Visit `http://<unraid-ip>:2283` and create the admin account -- this becomes the account you'll upload under, since [the automation's delete-safety model](README.md#design-decisions-worth-knowing-before-you-read-further) depends on you being the primary uploader. Then, still as admin, create one account per other person who'll use this.

## 4. Verify per-user storage separation

Upload a test photo as admin, then log in as a non-admin test account and upload another. On the host:

```bash
ls -R /mnt/disks/media_drive/immich_library/library
```

You should see separate subdirectories per user (keyed by internal user ID, not username) -- confirming uploads never mix on disk. This is automatic Immich behavior, not something configured.

## 5. Find your admin user ID

You'll need this in [04-automation-setup.md](04-automation-setup.md). Generate an API key first (Account Settings → API Keys), then:

```bash
curl -s http://localhost:2283/api/users/me -H "x-api-key: <your-api-key>" | jq .id
```

## Next

Continue to [03-tunnel-setup.md](03-tunnel-setup.md) to make this reachable from outside your home network.

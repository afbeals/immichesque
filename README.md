# immichesque

A self-hosted media-sharing setup built on [Immich](https://immich.app/), running on Unraid with storage on an external drive, reachable from the internet through a Cloudflare Tunnel (no home port-forwarding), plus a small automation service that backs up and auto-expires anything uploaded by non-admin users.

## Docs

| File | Covers |
| --- | --- |
| [docs/README.md](docs/README.md) | Doc index, stack overview, key design decisions |
| [docs/01-drive-setup.md](docs/01-drive-setup.md) | Mounting the external drive on Unraid |
| [docs/02-immich-setup.md](docs/02-immich-setup.md) | Deploying Immich, first login, users |
| [docs/03-tunnel-setup.md](docs/03-tunnel-setup.md) | Cloudflare Tunnel + subdomain, no exposed home IP |
| [docs/04-automation-setup.md](docs/04-automation-setup.md) | The review-staging backup/auto-expire automation |
| [docs/05-face-grouping.md](docs/05-face-grouping.md) | Validating Immich's face grouping at scale |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Known gotchas hit while building this |
| [docs/testing.md](docs/testing.md) | Running the automation service's test suite |

## Quick start

```bash
# 1. Mount the drive and create the directory layout -- see docs/01-drive-setup.md
# 2. Deploy Immich
cd immich
cp example.env .env
cat immichesque.env.example >> .env   # adds REVIEW_STAGING_LOCATION
cp automation.env.example automation.env
$EDITOR .env automation.env           # fill in real values -- see docs/02 and docs/04
docker compose up -d
```

## Scripts

| Command | Purpose |
| --- | --- |
| `docker compose up -d` (from `immich/`) | Start Immich + the tunnel + the automation service |
| `docker compose logs -f media-automation` | Watch the webhook receiver / expiry sweep logs |
| `pytest -v` (from `automation/`) | Run the automation service's test suite -- see [docs/testing.md](docs/testing.md) |

## Why not just build a custom app?

Every feature this project needs -- upload/download/view, tagging, albums with multi-user editing, per-user storage isolation, ownership-based delete protection, and face grouping at scale -- is already covered by Immich. The only genuinely custom piece is the automation service in `automation/`, which backs up non-admin uploads into a review-staging area and auto-expires them after a retention window unless explicitly kept -- something Immich doesn't do natively.

See [docs/README.md](docs/README.md) for the full design rationale.

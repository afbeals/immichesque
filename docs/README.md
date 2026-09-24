# Docs

New to this repo? Start here: [01-drive-setup.md](01-drive-setup.md), then work through the numbered docs in order. Each doc ends by naming the next one.

## Index

| Doc | Covers |
| --- | --- |
| [01-drive-setup.md](01-drive-setup.md) | Mounting the external drive via Unraid's Unassigned Devices plugin, directory layout |
| [02-immich-setup.md](02-immich-setup.md) | Deploying Immich's official Docker Compose stack, first login, creating admin/user accounts |
| [03-tunnel-setup.md](03-tunnel-setup.md) | Cloudflare Tunnel setup, subdomain DNS, no home port exposed |
| [04-automation-setup.md](04-automation-setup.md) | Building/running the automation container, configuring Immich's Workflow to call it |
| [05-face-grouping.md](05-face-grouping.md) | Validating face-grouping accuracy/performance against a real photo batch |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Specific failure modes hit while building this, and fixes |
| [testing.md](testing.md) | Running the automation service's pytest suite |

## Stack at a glance

| Layer | Technology |
| --- | --- |
| Media app | [Immich](https://immich.app/) (official Docker Compose deployment, vendored unmodified in `immich/`) |
| Storage | External USB HDD, mounted via Unraid's Unassigned Devices plugin |
| Public access | Cloudflare Tunnel + a subdomain on an existing domain |
| Automation | Custom Flask service + cron, in `automation/` |
| Automation language | Python 3 |
| Automation tests | pytest |

## Design decisions worth knowing before you read further

- **Two separate directory trees on the drive**: Immich's own managed library (`immich_library/`) and a review-staging area (`review_staging/`) that Immich has zero awareness of. The automation service only ever reads/writes the latter directly on disk -- it never touches Immich's managed folder with raw filesystem operations. See [04-automation-setup.md](04-automation-setup.md).
- **Delete safety comes from Immich's ownership model, not a custom permission system.** Non-admin users cannot delete assets they didn't upload, so as long as you (the admin) are the one uploading the bulk of the library, no extra enforcement layer is needed.
- **The 7-day auto-expiry applies only to the review-staging *duplicate*, never to the original inside Immich.** The original stays in the live gallery permanently unless you delete it yourself through Immich normally.
- **Immich was chosen over a custom-built app** because it already covers upload/download/view, tagging, albums with multi-user editing, per-user storage isolation, ownership-based delete protection, and free built-in face grouping at scale. The only genuinely custom piece is the review/backup/auto-expiry automation, which isn't something Immich does natively.

# 1. Drive setup

Covers mounting the external USB drive on Unraid without adding it to the parity-protected array, and laying out the two directory trees this project depends on.

## 1. Install the Unassigned Devices plugin

**Apps tab → search "Unassigned Devices" → Install.** This lets a drive be mounted and used by Docker containers without joining Unraid's parity array -- no reformat to Unraid's array filesystem, no parity rebuild, and the drive can be swapped or reformatted later without touching the array.

> **Why not just add it to the array?** Parity protection is nice, but it forces the array filesystem, triggers a parity sync on add/remove, and turns "unplug the drive" into a real procedure instead of a casual disconnect. For swappable external storage, Unassigned Devices is the simpler, lower-risk choice. The tradeoff: no parity protection for this drive -- back up anything you can't afford to lose.

## 2. Plug in the drive and format it

Plug the USB drive into the server. In **Main tab → Unassigned Devices**, the drive should appear. Format it (XFS or ext4 both work) from that same panel if it isn't already formatted.

## 3. Mount it at a stable, fixed-name path

Still in **Main tab → Unassigned Devices**, click **Mount** next to the drive.

> **Gotcha:** the auto-generated mount path is derived from the drive's label, so it can change if you rename or replace the drive later. Give it a fixed name (e.g. `media_drive`) in the Unassigned Devices UI first, so the mount path stays `/mnt/disks/media_drive` across drive swaps -- every other doc in this repo assumes that path.

## 4. Create the two directory trees

```bash
mkdir -p /mnt/disks/media_drive/immich_library
mkdir -p /mnt/disks/media_drive/review_staging
```

These stay completely separate on purpose:

- `immich_library/` -- Immich's own managed storage (`UPLOAD_LOCATION`). Nothing outside Immich ever writes to or deletes from this directly.
- `review_staging/` -- where the automation service copies non-admin uploads for review, and where the 7-day auto-expiry actually operates. Immich has no awareness of this path at all, so it's always safe to touch directly with plain file operations.

## Next

Continue to [02-immich-setup.md](02-immich-setup.md) to deploy Immich itself.

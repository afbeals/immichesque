# 5. Face grouping validation

Immich's face grouping is built in and free, but its accuracy and performance at real scale (this project's stated target is thousands of images) haven't been verified anywhere in this repo's planning -- this doc is the check.

## 1. Bulk-import a real batch

Rather than testing with a handful of photos, import a substantial existing batch (ideally hundreds to low thousands) via the [Immich CLI](https://immich.app/docs/features/command-line-interface) or by dragging a large folder into the web uploader, so the People clustering has enough data to be meaningful.

## 2. Let processing finish

Face detection and clustering run as background jobs. Check **Administration → Jobs** for the "Face Detection" and "Facial Recognition" queues to drain before judging results.

## 3. Review the People view

Open **People** in the sidebar. For each cluster, check:

- Are the same real person's photos actually grouped together?
- Are two different people ever merged into one cluster?
- Is one person split across several clusters?

Immich's People view supports merging and renaming clusters directly -- use it to correct what you find, and note whether the correction burden feels reasonable for your actual library size.

## 4. Record the result

There's no fixed pass/fail bar here -- this step exists because "face grouping is important for managing thousands of images" was a stated requirement with no independently-verified accuracy claim behind it. Whatever you observe (good, mediocre, unusable) should decide whether Immich's built-in grouping is sufficient as-is, or whether it's worth revisiting.

## Next

That's the last numbered setup doc. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for gotchas, or [testing.md](testing.md) for the automation service's test suite.

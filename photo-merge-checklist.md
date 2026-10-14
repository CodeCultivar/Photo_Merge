# Photo Merge Checklist (Apple + Google, ~1.6 TB total)

Rule: do NOT delete anything in iCloud or Google Photos until the final step.

## 0. Prep
- [ ] Decide destination (Google Photos or iCloud Photos)
- [ ] Get an external drive or internal disk with 4 TB free (exports + working copy + deduped set)
- [ ] Decide what "duplicate" means: exact copies only, or also edits/resizes/HEIC-vs-JPEG
- [ ] Turn off sleep/auto-lock on the computer doing the downloads

## 1. Export Apple Photos
- [ ] Mac: open Photos > select all > File > Export > Export Unmodified Originals (include XMP sidecars)
- [ ] OR privacy.apple.com > Request a copy of your data > Photos (50 GB chunks)
- [ ] Spot-check: photo count in Photos.app roughly matches files exported
- [ ] Save to `/Volumes/PhotoMerge/apple/`

## 2. Export Google Photos
- [ ] takeout.google.com > deselect all > Google Photos only
- [ ] Format .zip, size 50 GB chunks, one-time export
- [ ] Download every chunk (links expire after about 7 days)
- [ ] Unzip all chunks into ONE folder: `/Volumes/PhotoMerge/google_raw/`
- [ ] Verify each zip extracted without errors

## 3. Fix Google metadata
- [ ] Run GooglePhotosTakeoutHelper (merges the .json sidecar dates/GPS into the files)
- [ ] Output to `/Volumes/PhotoMerge/google_fixed/`
- [ ] Spot-check 20 random files: date taken and location look right

## 4. Remove exact duplicates (script)
- [ ] `python dedupe_by_hash.py /Volumes/PhotoMerge/apple /Volumes/PhotoMerge/google_fixed` (dry run, writes report CSV)
- [ ] Open the report, sanity-check a few groups
- [ ] Re-run with `--apply` (moves duplicates to a quarantine folder, never deletes)

## 5. Remove near-duplicates (GUI tool)
- [ ] Run Czkawka (similar images) or Gemini 2 on the combined set
- [ ] Review visually, keep the highest-resolution/original version
- [ ] Do not auto-delete

## 6. Upload
- [ ] Upload the clean set to the destination service
- [ ] Wait for processing to finish; compare item count to local count

## 7. Verify, then clean up
- [ ] Spot-check 30 photos across years: dates, locations, albums
- [ ] Keep the local exports + quarantine folder for at least 30 days
- [ ] Only then delete the old copies from the source service(s)
- [ ] Back up the final library somewhere else (3-2-1 rule)

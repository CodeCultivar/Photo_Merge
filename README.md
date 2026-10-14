# Photo_Merge

Tools and a checklist for merging a Google Photos library and an Apple Photos library into one, with no duplicates.

- `photo-merge-checklist.md`: step-by-step plan (export both libraries, fix Google metadata, dedupe, upload, verify).
- `dedupe_by_hash.py`: finds byte-identical duplicates across folders. Dry run by default; with `--apply` it moves duplicates to a quarantine folder and never deletes.

```
python dedupe_by_hash.py /path/apple /path/google_fixed          # dry run
python dedupe_by_hash.py /path/apple /path/google_fixed --apply  # quarantine duplicates
```

Note: hashing only catches exact copies. Use a tool like Czkawka or Gemini for near-duplicates.

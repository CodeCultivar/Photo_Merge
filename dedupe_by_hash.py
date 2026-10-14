#!/usr/bin/env python3
"""Find and quarantine byte-identical duplicate photos/videos across folders.

Dry run by default. With --apply, duplicates are MOVED (never deleted) to a
quarantine folder. Only exact duplicates are detected; use Czkawka/Gemini for
near-duplicates.

Usage:
    python dedupe_by_hash.py /path/apple /path/google_fixed
    python dedupe_by_hash.py /path/apple /path/google_fixed --apply
"""
import argparse
import csv
import hashlib
import shutil
import sys
from collections import defaultdict
from pathlib import Path

MEDIA_EXT = {
    ".jpg", ".jpeg", ".png", ".heic", ".heif", ".gif", ".webp", ".tif", ".tiff",
    ".bmp", ".dng", ".raw", ".cr2", ".cr3", ".nef", ".arw", ".orf", ".raf",
    ".mov", ".mp4", ".m4v", ".avi", ".mkv", ".3gp", ".mts",
}


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def collect(roots):
    for root in roots:
        for p in Path(root).rglob("*"):
            if p.is_file() and p.suffix.lower() in MEDIA_EXT:
                yield p


def keeper_key(p):
    # Prefer shorter paths (less likely to be "copy (1)" style), then oldest mtime.
    return (len(str(p)), p.stat().st_mtime)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folders", nargs="+")
    ap.add_argument("--apply", action="store_true", help="move duplicates to quarantine")
    ap.add_argument("--quarantine", default="_duplicates_quarantine")
    ap.add_argument("--report", default="duplicates_report.csv")
    args = ap.parse_args()

    quarantine = Path(args.quarantine).resolve()
    by_size = defaultdict(list)
    count = 0
    for p in collect(args.folders):
        if quarantine in p.resolve().parents:
            continue
        by_size[p.stat().st_size].append(p)
        count += 1
    print(f"Scanned {count} media files.")

    # Only hash files that share a size with another file.
    candidates = [p for group in by_size.values() if len(group) > 1 for p in group]
    print(f"Hashing {len(candidates)} files with matching sizes...")

    by_hash = defaultdict(list)
    for i, p in enumerate(candidates, 1):
        try:
            by_hash[sha256(p)].append(p)
        except OSError as e:
            print(f"  skip {p}: {e}", file=sys.stderr)
        if i % 500 == 0:
            print(f"  {i}/{len(candidates)}")

    dup_groups = [g for g in by_hash.values() if len(g) > 1]
    moved = 0
    saved = 0
    with open(args.report, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["action", "file", "kept_file", "size_bytes"])
        for group in dup_groups:
            group.sort(key=keeper_key)
            keep, extras = group[0], group[1:]
            for dup in extras:
                size = dup.stat().st_size
                saved += size
                if args.apply:
                    dest = quarantine / dup.name
                    n = 1
                    while dest.exists():
                        dest = quarantine / f"{dup.stem}_{n}{dup.suffix}"
                        n += 1
                    quarantine.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(dup), str(dest))
                    w.writerow(["moved", dup, keep, size])
                    moved += 1
                else:
                    w.writerow(["would_move", dup, keep, size])

    verb = "Moved" if args.apply else "Would move"
    n = moved if args.apply else sum(len(g) - 1 for g in dup_groups)
    print(f"{verb} {n} duplicates ({saved / 1e9:.1f} GB). Report: {args.report}")
    if not args.apply:
        print("Dry run only. Re-run with --apply to quarantine them.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Daily sync with upstream danielmiessler/Fabric.

What it does:
  1. Shallow-clone upstream (or reuse --upstream-dir) and read its HEAD commit.
  2. If the commit equals data/patterns.json's upstream_commit, exit quietly.
  3. Otherwise extract every pattern (name, tags + official description from
     scripts/pattern_descriptions/pattern_descriptions.json, sha256 of
     system.md) and diff against data/patterns.json:
       - added   -> new entry, status "pending_translation", zh fields filled
                    from the official English description as a placeholder
       - changed -> content_hash differs: keep zh text, status "needs_review"
       - removed -> entry dropped
       - renamed -> hash match under a new name: treated as remove + add
  4. Update data/patterns.json, rebuild catalog.md + docs/index.html,
     and write a human-readable report to sync_reports/YYYY-MM-DD.md.

Translation itself is intentionally NOT done here: new/changed entries are
flagged in the data file and in the sync report so a human (or an LLM step
you add in CI) can write the Chinese summary and flip status to
"translated". Run scripts/build_catalog.py afterwards to re-render.

Usage:
  python3 scripts/sync_upstream.py [--upstream-dir PATH] [--keep-clone]
Exit code 0 always (check stdout / git diff in CI to decide whether to
commit); exit code 2 on hard errors.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPSTREAM_URL = "https://github.com/danielmiessler/Fabric.git"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def extract(upstream_dir):
    """Return {name: {tags, desc_en, upstream_path, content_hash, purpose}}."""
    base = os.path.join(upstream_dir, "data", "patterns")
    desc = {}
    desc_file = os.path.join(
        upstream_dir, "scripts", "pattern_descriptions", "pattern_descriptions.json"
    )
    if os.path.isfile(desc_file):
        with open(desc_file, encoding="utf-8") as f:
            for p in json.load(f)["patterns"]:
                desc[p["patternName"]] = p
    out = {}
    for name in sorted(os.listdir(base)):
        full = os.path.join(base, name)
        if os.path.isfile(full):  # e.g. pattern_explanations.md
            out[name] = {
                "tags": [], "desc_en": "",
                "upstream_path": f"data/patterns/{name}",
                "content_hash": sha16(full), "purpose": "",
            }
            continue
        sp = os.path.join(full, "system.md")
        if not os.path.isfile(sp):
            continue
        text = open(sp, encoding="utf-8", errors="replace").read()
        m = re.search(r"# IDENTITY and PURPOSE(.*?)(?=\n# |\Z)", text, re.S | re.I)
        purpose = re.sub(r"\s+", " ", m.group(1)).strip()[:700] if m else ""
        out[name] = {
            "tags": desc.get(name, {}).get("tags", []),
            "desc_en": desc.get(name, {}).get("description", ""),
            "upstream_path": f"data/patterns/{name}/system.md",
            "content_hash": sha16(sp),
            "purpose": purpose,
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream-dir", help="existing upstream checkout to use instead of cloning")
    ap.add_argument("--keep-clone", action="store_true")
    args = ap.parse_args()

    data_path = os.path.join(ROOT, "data", "patterns.json")
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    old_commit = data.get("upstream_commit", "")

    tmp = None
    upstream_dir = args.upstream_dir
    if not upstream_dir:
        tmp = tempfile.mkdtemp(prefix="fabric-upstream-")
        subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", UPSTREAM_URL, tmp],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "-C", tmp, "sparse-checkout", "set", "data/patterns",
             "scripts/pattern_descriptions"],
            check=True, capture_output=True, text=True,
        )
        upstream_dir = tmp
    try:
        new_commit = subprocess.run(
            ["git", "-C", upstream_dir, "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        new_commit_date = subprocess.run(
            ["git", "-C", upstream_dir, "log", "-1", "--format=%cs"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()

        if new_commit == old_commit:
            print(f"NO_CHANGE upstream already at {new_commit[:7]}")
            return 0

        fresh = extract(upstream_dir)
        old = {p["name"]: p for p in data["patterns"]}
        added, changed, removed = [], [], []
        merged = []
        # Keep existing entry order (sorted by Chinese title); append new entries at the end.
        for name in old:
            if name not in fresh:
                removed.append(name)
                continue
            f = fresh[name]
            e = dict(old[name])
            e["tags"] = f["tags"] or e.get("tags", [])
            e["desc_en"] = f["desc_en"]
            e["upstream_path"] = f["upstream_path"]
            e["source_url"] = f"https://github.com/danielmiessler/Fabric/blob/main/{f['upstream_path']}"
            if e.get("content_hash") != f["content_hash"]:
                changed.append(name)
                e["content_hash"] = f["content_hash"]
                if e.get("status") == "translated":
                    e["status"] = "needs_review"
                e["_purpose_en"] = f["purpose"]
            merged.append(e)
        for name, f in fresh.items():
            if name in old:
                continue
            added.append(name)
            merged.append({
                "name": name, "zh_title": "", "zh_desc": f["desc_en"],
                "scenario": "", "tags": f["tags"], "group": "格式转换与其他",
                "desc_en": f["desc_en"],
                "source_url": f"https://github.com/danielmiessler/Fabric/blob/main/{f['upstream_path']}",
                "upstream_path": f["upstream_path"],
                "content_hash": f["content_hash"],
                "status": "pending_translation",
                "_purpose_en": f["purpose"],
            })

        data["patterns"] = merged
        data["count"] = len(merged)
        data["upstream_commit"] = new_commit
        data["upstream_commit_date"] = new_commit_date
        data["synced_at"] = date.today().isoformat()
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)

        os.makedirs(os.path.join(ROOT, "sync_reports"), exist_ok=True)
        def _lst(names):
            return [f"- `{n}`" for n in names] if names else ["- 无"]

        report = [
            f"# 上游同步报告 {data['synced_at']}",
            "",
            f"- 上游 commit：`{old_commit[:7]}` → `{new_commit[:7]}`（{new_commit_date}）",
            f"- 新增 {len(added)} · 变更 {len(changed)} · 删除 {len(removed)} · 总数 {len(merged)}",
            "",
            "## 新增（待翻译：status=pending_translation）",
            *_lst(added),
            "",
            "## 内容变更（待复核：status=needs_review）",
            *_lst(changed),
            "",
            "## 已删除",
            *_lst(removed),
            "",
        ]
        with open(os.path.join(ROOT, "sync_reports", f"{data['synced_at']}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(report))

        import build_catalog
        build_catalog.main()
        print(
            f"SYNCED {old_commit[:7]} -> {new_commit[:7]} "
            f"added={len(added)} changed={len(changed)} removed={len(removed)} total={len(merged)}"
        )
        if added or changed:
            print("PENDING_TRANSLATION_OR_REVIEW: " + ",".join(added + changed))
        return 0
    finally:
        if tmp and not args.keep_clone:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())

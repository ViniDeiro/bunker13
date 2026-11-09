"""Read-only inventory of candidate files and reachable Git history. Never stage/push."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 100 * 1024 * 1024
ASSET_EXT = {".uasset", ".umap", ".blend", ".spp", ".fbx", ".glb", ".png", ".jpg", ".jpeg", ".tga", ".exr", ".wav", ".ogg", ".pdf"}

def git(*args, data=None):
    return subprocess.run(["git", *args], cwd=ROOT, input=data, capture_output=True, check=True).stdout

def scan():
    (ROOT / "logs").mkdir(exist_ok=True)
    candidates = sorted(set(git("ls-files", "--cached", "--others", "--exclude-standard", "-z").decode().split("\0")) - {""})
    rows, secret_flags, missing, ignored_tracked = [], [], [], []
    patterns = [re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
                re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
                re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
                re.compile(rb"\bAKIA[A-Z0-9]{16}\b")]
    attrs_data = b"".join(p.encode()+b"\0" for p in candidates)
    attrs = git("check-attr", "--stdin", "-z", "filter", data=attrs_data).decode().split("\0")
    filters = {attrs[i]: attrs[i+2] for i in range(0, len(attrs)-1, 3)}
    tracked = set(git("ls-files", "-z").decode().split("\0"))
    for rel in candidates:
        path = ROOT / rel
        if not path.is_file():
            missing.append(rel)
            continue
        size = path.stat().st_size
        row = dict(path=rel, bytes=size, filter=filters.get(rel), tracked=rel in tracked)
        if path.suffix.lower() in ASSET_EXT:
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024*1024), b""): digest.update(block)
            row["sha256"] = digest.hexdigest()
        if path.name == ".env" or path.suffix.lower() in {".sav", ".key", ".p12", ".pfx"}:
            secret_flags.append(dict(path=rel, reason="private filename"))
        if size < 2*1024*1024 and path.suffix.lower() not in ASSET_EXT:
            raw = path.read_bytes()
            if b"\0" not in raw and any(p.search(raw) for p in patterns):
                secret_flags.append(dict(path=rel, reason="credential signature; inspect locally, value withheld"))
        rows.append(row)
    # New ignores do not remove already tracked files; report these explicitly.
    ignored = subprocess.run(["git", "check-ignore", "--no-index", "--stdin", "-z"],
                             cwd=ROOT, input=b"".join(p.encode()+b"\0" for p in tracked if p), capture_output=True)
    if ignored.returncode not in (0, 1): raise RuntimeError(ignored.stderr.decode())
    ignored_tracked = sorted(set(ignored.stdout.decode().split("\0")) - {""})
    objects = git("rev-list", "--objects", "--all")
    sizes = git("cat-file", "--batch-check=%(objecttype) %(objectname) %(objectsize) %(rest)", data=objects).decode().splitlines()
    large_history = []
    history_bytes = 0
    for line in sizes:
        fields = line.split(" ", 3)
        if fields[0] != "blob": continue
        size = int(fields[2]); history_bytes += size
        if size >= LIMIT:
            large_history.append(dict(oid=fields[1], bytes=size, path=fields[3] if len(fields)>3 else ""))
    lfs = subprocess.run(["git", "lfs", "version"], cwd=ROOT, capture_output=True, text=True)
    indexed_lfs = git("lfs", "ls-files", "--name-only").decode().splitlines() if lfs.returncode==0 else []
    assets = [r for r in rows if Path(r["path"]).suffix.lower() in ASSET_EXT]
    pending_lfs = [r["path"] for r in assets if r["tracked"] and r["path"] not in indexed_lfs]
    config = git("remote").decode().splitlines()
    result = dict(date="2026-11-09", candidate_count=len(rows), candidate_bytes=sum(r["bytes"] for r in rows),
                  assets_count=len(assets), assets_bytes=sum(r["bytes"] for r in assets),
                  missing=missing, credential_signatures=secret_flags, ignored_but_tracked=ignored_tracked,
                  history_blob_bytes=history_bytes, history_over_100mib=large_history,
                  oversized_non_lfs=[r["path"] for r in rows if r["bytes"]>=LIMIT and r["filter"]!="lfs"],
                  assets_without_lfs_rule=[r["path"] for r in assets if r["filter"]!="lfs"],
                  lfs_installed=lfs.returncode==0, lfs_version=lfs.stdout.strip(),
                  tracked_assets_pending_lfs_staging=pending_lfs, remotes=config,
                  largest=sorted(rows,key=lambda r:r["bytes"],reverse=True)[:15],
                  asset_manifest=assets,
                  limits=["No staging, commit, remote mutation, upload or history rewrite.",
                          "Credential pattern scan is limited to candidate text files, not a full history/secret audit.",
                          "Hashes describe files at audit time; close source editors before final publication snapshot."])
    result["ready_to_publish"] = not any((missing,secret_flags,ignored_tracked,large_history,
        result["oversized_non_lfs"],result["assets_without_lfs_rule"],pending_lfs)) and lfs.returncode==0 and bool(config)
    (ROOT/"logs/repository_audit.json").write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in {"asset_manifest","largest","tracked_assets_pending_lfs_staging","ignored_but_tracked"}},indent=2))
    print(f"tracked_pending_lfs={len(pending_lfs)} ignored_but_tracked={len(ignored_tracked)}")
    return result

if __name__ == "__main__": scan()

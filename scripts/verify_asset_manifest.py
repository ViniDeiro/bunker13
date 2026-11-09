"""Verify recovered source assets against the publication snapshot, including LFS content."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "docs/validation/assets_2026-11-09.json").read_text())
failures = []
for entry in manifest["assets"]:
    path = (ROOT / entry["path"]).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        failures.append(dict(path=entry["path"], reason="missing or invalid path"))
        continue
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            digest.update(block)
    if path.stat().st_size != entry["bytes"] or digest.hexdigest() != entry["sha256"]:
        failures.append(dict(path=entry["path"], reason="size or SHA-256 mismatch"))
result = dict(passed=not failures, assets_checked=len(manifest["assets"]), failures=failures)
(ROOT / "logs").mkdir(exist_ok=True)
(ROOT / "logs/clone_asset_verification.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["passed"] else 1)
